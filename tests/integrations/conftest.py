import pytest

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from brew_scout.libs.settings import AppSettings
from brew_scout.libs.setup_app import setup_app
from brew_scout.vars import set_async_session
from brew_scout.libs.managers import rds_manager

from tests.conftest import AsyncScopedSession


@pytest.fixture()
async def async_app(pg_conf):
    settings = AppSettings(
        database_dsn=f"postgresql+asyncpg://{pg_conf['user']}:{pg_conf['password']}@{pg_conf['host']}:{pg_conf['port']}/{pg_conf['db']}",
        redis_dsn="redis://localhost:6379/0",
        telegram_api_url="https://telegram.org",
        telegram_api_token="token",
    )
    app = setup_app(settings)

    async with LifespanManager(app, startup_timeout=None):
        yield app


@pytest.fixture()
async def configure_session(pg_conf, create_db):
    engine = create_async_engine(
        f"postgresql+asyncpg://{pg_conf['user']}:{pg_conf['password']}@{pg_conf['host']}:{pg_conf['port']}/{pg_conf['db']}"
    )
    AsyncScopedSession.configure(bind=engine, expire_on_commit=False)

    try:
        yield
    finally:
        await AsyncScopedSession.remove()
        await engine.dispose()


@pytest.fixture()
def app(async_app, configure_session):
    set_async_session(AsyncScopedSession)
    return async_app


@pytest.fixture()
async def client(app):
    async with AsyncClient(app=app, base_url="http://base") as client:
        yield client


@pytest.fixture()
def db_session(app):
    return AsyncScopedSession


@pytest.fixture()
async def rds_session(app):
    async with rds_manager.session() as redis_client:
        yield redis_client
