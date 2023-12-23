import asyncio
import time
import uuid
from pathlib import Path

import pytest
from docker import DockerClient
from docker.errors import ImageNotFound
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, async_sessionmaker
from sqlalchemy.pool import NullPool

from alembic.command import upgrade
from alembic.config import Config


AsyncScopedSession = async_scoped_session(async_sessionmaker(), scopefunc=lambda: 1)
ROOT_DIR = Path(__file__).parent.parent
POSTGRES_IMAGE = "postgres:14.9-alpine"
POSTGRES_CONTAINER_BASE_NAME = "postgres-test"


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
def pg_conf(pg_container):
    """Manage PostgreSQL settings"""
    return {
        "host": pg_container["host"],
        "port": pg_container["port"],
        "db": "test_database_name",
        "user": "username",
        "password": "password",
        "system_async_dsn": pg_container["dsn"],
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
