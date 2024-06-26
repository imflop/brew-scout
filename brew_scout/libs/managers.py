import asyncio
import dataclasses as dc
import typing as t
from asyncio import AbstractEventLoop
from collections import abc
from contextlib import asynccontextmanager
from functools import partial

import aiohttp
from authlib.integrations.starlette_client import OAuth
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncConnection, async_sessionmaker, create_async_engine

from brew_scout.libs.admin.backends import AdminAuthenticationBackend
from brew_scout.libs.settings import AppSettings


P = t.ParamSpec("P")


@dc.dataclass(slots=True)
class RedisSessionManager:
    _client: Redis | None = dc.field(default=None)

    def init(self, redis_dsn: str) -> None:
        self._client = Redis.from_url(redis_dsn, encoding="utf-8", decode_responses=True)

    async def close(self) -> None:
        if self._client is None:
            return

        await self._client.aclose()

    @asynccontextmanager
    async def session(self) -> abc.AsyncIterator[Redis]:
        if self._client is None:
            raise IOError("Redis client is not initialized")

        yield self._client


@dc.dataclass(slots=True)
class DatabaseSessionManager:
    _engine: AsyncEngine | None = dc.field(default=None)
    _session_factory: async_sessionmaker[AsyncSession] | None = dc.field(default=None)

    def init(self, database_dsn: str, debug: bool = False) -> None:
        self._engine = create_async_engine(database_dsn, pool_pre_ping=True, echo=debug)
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    async def close(self) -> None:
        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    @asynccontextmanager
    async def session(self) -> abc.AsyncIterator[AsyncSession]:
        if self._session_factory is None:
            raise IOError("DatabaseSessionManager: session factory is not initialized")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

    @asynccontextmanager
    async def connection(self) -> abc.AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise IOError("DatabaseSessionManager: engine is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
                await connection.close()
            except Exception:
                await connection.rollback()
                raise

    def get_engine(self) -> AsyncEngine:
        if not self._engine:
            raise IOError("DatabaseSessionManager: engine is not initialized")

        return self._engine


@dc.dataclass(slots=True)
class ClientSessionManager:
    _session_factory: abc.Callable[..., aiohttp.ClientSession] | None = dc.field(default=None)
    _client_session: aiohttp.ClientSession | None = dc.field(default=None)

    def init(self, loop: AbstractEventLoop) -> None:
        self._session_factory = partial(self._session_getter, loop=loop)

    def get_session(self, **kwargs: t.Any) -> aiohttp.ClientSession:
        if self._session_factory is None:
            raise IOError("ClientSessionManager: session factory is not initialized")

        if self._client_session is None:
            self._client_session = self._session_factory(**kwargs)
            return self._client_session

        return self._client_session

    async def close(self) -> None:
        if self._client_session is None:
            return

        await self._client_session.close()
        self._client_session = None

    def _session_getter(self, loop: AbstractEventLoop, *args: P.args, **kwargs: P.kwargs) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(loop=loop)


@dc.dataclass(slots=True)
class OAuthClientManager:
    _backend: AdminAuthenticationBackend | None = dc.field(default=None)
    _client: t.Any | None = dc.field(default=None)

    def init(
        self, remote_app_name: str, client_id: str, client_secret: str, server_metadata_url: str, secret_key: str
    ) -> None:
        oauth = OAuth()
        oauth.register(
            name=remote_app_name,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=server_metadata_url,
            client_kwargs={
                "scope": "openid email profile",
                "prompt": "select_account",
            },
        )

        self._client = oauth.create_client(remote_app_name)
        self._backend = AdminAuthenticationBackend(secret_key, self._client)

    def get_backend(self) -> AdminAuthenticationBackend:
        if self._backend is None:
            raise IOError("OAuthClientManager: backend is not initialized")

        return self._backend

    def get_client(self) -> t.Any:
        if self._client is None:
            raise IOError("OAuthClientManager: oauth client is not initialized")

        return self._client

    def close(self) -> None:
        if self._client is None:
            return

        self._client = None
        self._backend = None


@dc.dataclass(frozen=True, slots=True, repr=False)
class ManagerProvider:
    settings: AppSettings
    client_session_manager: ClientSessionManager
    database_session_manager: DatabaseSessionManager
    redis_session_manager: RedisSessionManager
    oauth_client_manager: OAuthClientManager
    running_loop: AbstractEventLoop = dc.field(default_factory=lambda: asyncio.get_running_loop())

    def start(self) -> None:
        self.database_session_manager.init(self.settings.database_dsn, self.settings.debug)
        self.redis_session_manager.init(self.settings.redis_dsn)
        self.client_session_manager.init(self.running_loop)
        self.oauth_client_manager.init(
            remote_app_name=self.settings.oauth_app_name,
            client_id=self.settings.oauth_client_id,
            client_secret=self.settings.oauth_client_secret,
            server_metadata_url=self.settings.oauth_server_metadata_url,
            secret_key=self.settings.secret_key,
        )

    async def stop(self) -> None:
        await self.database_session_manager.close()
        await self.redis_session_manager.close()
        await self.client_session_manager.close()
        self.oauth_client_manager.close()
