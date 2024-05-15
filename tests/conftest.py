import asyncio
import dataclasses as dc
import time
import typing as t
import uuid
from collections import abc
from pathlib import Path
from enum import StrEnum

import pytest
from docker import DockerClient
from docker.errors import ImageNotFound
from docker.models.containers import Container
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, async_sessionmaker
from sqlalchemy.pool import NullPool

from alembic.command import upgrade
from alembic.config import Config


AsyncScopedSession = async_scoped_session(async_sessionmaker(), scopefunc=lambda: 1)
ROOT_DIR = Path(__file__).parent.parent
# POSTGRES_IMAGE = "postgres:14.9-alpine"
POSTGRES_IMAGE = "postgres:16.2-alpine"
POSTGRES_CONTAINER_BASE_NAME = "postgres-test"


class ContainerKeyName(StrEnum):
    PG = "pg"
    RDS = "rds"


@dc.dataclass(frozen=True, slots=True)
class BaseContainer:
    @classmethod
    def wait_until_ports_are_available(
        cls,
        raw_container: Container,
        ports: abc.Mapping[str, t.Any],
        timeout: float = 3.5,
    ) -> None:
        now = time.monotonic()
        delay = 0.001

        while (time.monotonic() - now) < timeout:
            raw_container.reload()
            container_ports = {k: v for k, v in raw_container.ports.items() if v}

            if set(ports).issubset(container_ports):
                break

            time.sleep(delay)
            delay *= 5
        else:
            raise TimeoutError(f"Docker failed to expose ports in {timeout}")

    @classmethod
    def wait_until_ready(cls, raw_container: Container, searched_log_string: str, timeout: float = 5.5) -> None:
        now = time.monotonic()
        delay = 0.001

        while (time.monotonic() - now) < timeout:
            log = raw_container.logs(tail=1)

            if searched_log_string in log.decode():
                break

            time.sleep(delay)
            delay *= 5
        else:
            raise TimeoutError(f"Docker container did not start in {timeout}s")


@dc.dataclass(frozen=True, slots=True)
class RedisContainer(BaseContainer):
    dsn: str

    @staticmethod
    def get_name() -> str:
        return f"redis-test-{uuid.uuid4().hex}"

    @staticmethod
    def get_image() -> str:
        return "redis:7.2.4-alpine"

    @staticmethod
    def get_ports() -> abc.Mapping[str, t.Any]:
        return {"6379/tcp": None}

    @staticmethod
    def get_envs() -> abc.Mapping[str, t.Any]:
        return {}

    @staticmethod
    def get_searched_log_string() -> str:
        return "Ready to accept connections tcp"

    @classmethod
    def from_container(cls, raw_container: Container) -> t.Self:
        container_host_port = int(raw_container.ports["6379/tcp"][0]["HostPort"])

        return RedisContainer(dsn=f"redis://127.0.0.1:{container_host_port}/0")


@dc.dataclass(frozen=True, slots=True)
class PostgresContainer(BaseContainer):
    dsn: str
    host: str
    port: int
    username: str
    password: str
    db_name: str

    @staticmethod
    def get_name() -> str:
        return f"postgres-test-{uuid.uuid4().hex}"

    @staticmethod
    def get_image() -> str:
        return "postgres:16.2-alpine"

    @staticmethod
    def get_ports() -> abc.Mapping[str, t.Any]:
        return {"5432/tcp": None}

    @staticmethod
    def get_envs() -> abc.Mapping[str, t.Any]:
        return {
            "POSTGRES_DB": "postgres",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "password",
        }

    @staticmethod
    def get_searched_log_string() -> str:
        return "database system is ready to accept connections"

    @classmethod
    def from_container(cls, raw_container: Container) -> t.Self:
        container_host_port = int(raw_container.ports["5432/tcp"][0]["HostPort"])
        db_name, username, password = cls.get_envs().values()
        host = "127.0.0.1"

        return PostgresContainer(
            dsn=f"postgresql+asyncpg://{username}:{password}@{host}:{container_host_port}/{db_name}",
            port=container_host_port,
            host=host,
            db_name="test_database",
            username="test_username",
            password="test_password",
        )


def get_container(
    container_key_name: ContainerKeyName,
    docker_client_factory: abc.Callable[[], DockerClient] = DockerClient.from_env
) -> PostgresContainer | RedisContainer:
    if not (future_container := {
        ContainerKeyName.PG: PostgresContainer,
        ContainerKeyName.RDS: RedisContainer
    }.get(container_key_name)):
        raise KeyError(f"unidentified container {container_key_name}")

    docker_client = docker_client_factory()

    try:
        docker_client.images.get(future_container.get_image())
    except ImageNotFound:
        docker_client.images.pull(future_container.get_image())

    raw_container = docker_client.containers.create(
        image=future_container.get_image(),
        name=future_container.get_name(),
        detach=True,
        environment=future_container.get_envs(),
        ports=future_container.get_ports(),
    )

    raw_container.start()
    future_container.wait_until_ports_are_available(raw_container, future_container.get_ports())
    future_container.wait_until_ready(raw_container, future_container.get_searched_log_string())
    container = future_container.from_container(raw_container)

    try:
        yield container
    finally:
        raw_container.kill(signal=9)
        raw_container.remove(v=True, force=True)


@pytest.fixture(scope="session")
def pg_container():
    """Start the PostgreSQL container"""
    docker_client = DockerClient.from_env()
    ports = {"5432/tcp": None}
    host = "127.0.0.1"
    db_name = "postgres"
    username = "postgres"
    password = "password"

    def generate_container_name(x):
        return f"{x}-{uuid.uuid4().hex}"

    try:
        docker_client.images.get(POSTGRES_IMAGE)
    except ImageNotFound:
        docker_client.images.pull(POSTGRES_IMAGE)

    container = docker_client.containers.create(
        image=POSTGRES_IMAGE,
        name=generate_container_name(POSTGRES_CONTAINER_BASE_NAME),
        detach=True,
        environment={
            "POSTGRES_DB": db_name,
            "POSTGRES_USER": username,
            "POSTGRES_PASSWORD": password,
        },
        ports=ports,
    )

    container.start()

    # Wait until ports are available
    while True:
        container.reload()
        container_ports = {k: v for k, v in container.ports.items() if v}
        if set(ports).issubset(container_ports):
            break
        time.sleep(0.05)

    # Wait until the container is ready
    while True:
        log = container.logs(tail=1)
        if "database system is ready to accept connections" in log.decode():
            break
        time.sleep(0.5)

    container_host_port = int(container.ports["5432/tcp"][0]["HostPort"])

    yield {
        "host": host,
        "port": container_host_port,
        "user": username,
        "password": password,
        "db": db_name,
        "dsn": f"postgresql+asyncpg://{username}:{password}@{host}:{container_host_port}/{db_name}",
    }

    container.kill(signal=9)
    container.remove(v=True, force=True)


@pytest.fixture(scope="session")
def rds_container() -> RedisContainer:
    yield from get_container(ContainerKeyName.RDS)


@pytest.fixture(scope="session")
def pg_container_new() -> PostgresContainer:
    yield from get_container(ContainerKeyName.PG)


@pytest.fixture(scope="session")
def rds_conf(rds_container):
    return {"dsn": rds_container.dsn}


@pytest.fixture(scope="session")
def pg_conf(pg_container_new):
    return {
        "host": pg_container_new.host,
        "port": pg_container_new.port,
        "db": pg_container_new.db_name,
        "user": pg_container_new.username,
        "password": pg_container_new.password,
        "system_async_dsn": pg_container_new.dsn,
    }


@pytest.fixture(scope="session")
def system_async_engine(pg_conf):
    return create_async_engine(
        pg_conf["system_async_dsn"], poolclass=NullPool, execution_options={"isolation_level": "AUTOCOMMIT"}
    )


@pytest.fixture(scope="session")
def template_db(system_async_engine):
    name = "templatedb"

    async def _async():
        async with system_async_engine.begin() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS {name}"))
            await conn.execute(text(f"CREATE DATABASE {name}"))
            await conn.close()

    asyncio.run(_async())
    return name


@pytest.fixture(scope="session")
def alembic_config(pg_conf, template_db):
    config = Config(f"{ROOT_DIR}/alembic.ini")
    config.set_main_option(
        "sqlalchemy.url",
        f"postgresql+asyncpg://{pg_conf['user']}:{pg_conf['password']}@{pg_conf['host']}:{pg_conf['port']}/{template_db}",
    )
    config.set_main_option("script_location", f"{ROOT_DIR}/alembic")
    return config


@pytest.fixture(scope="session")
def alembic_upgrade(alembic_config, system_async_engine, pg_conf, template_db):
    async def _async():
        async with system_async_engine.begin() as conn:
            await conn.execute(text(f"CREATE USER {pg_conf['user']} WITH SUPERUSER PASSWORD '{pg_conf['password']}'"))

    asyncio.run(_async())
    upgrade(alembic_config, "head")


@pytest.fixture()
async def create_db(system_async_engine, pg_conf, alembic_upgrade, template_db):
    async with system_async_engine.begin() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {pg_conf['db']}"))
        await conn.execute(text(f"CREATE DATABASE {pg_conf['db']} WITH TEMPLATE {template_db}"))
