import dataclasses as dc
from collections import abc
from contextlib import asynccontextmanager

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncConnection, async_sessionmaker, create_async_engine


@dc.dataclass(slots=True)
class RedisSessionManager:
    _client: Redis | None = dc.field(default=None)

    def init(self, redis_dsn: str) -> None:
        self._client = Redis.from_url(redis_dsn, encoding="utf-8", decode_responses=True)

    async def close(self) -> None:
        await self._client.aclose()  # type: ignore

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
            raise IOError("Session factory is not initialized")

        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @asynccontextmanager
    async def connection(self) -> abc.AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise


rds_manager = RedisSessionManager()
db_manager = DatabaseSessionManager()
