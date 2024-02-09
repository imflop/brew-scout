import dataclasses as dc
from collections import abc
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncConnection, async_sessionmaker, create_async_engine


@dc.dataclass(slots=True)
class DatabaseSessionManager:
    _engine: AsyncEngine | None = dc.field(default=None)
    _session_factory: async_sessionmaker[AsyncSession] | None = dc.field(default=None)

    def init(self, database_dsn: str, debug: bool = False) -> None:
        self._engine = create_async_engine(database_dsn, echo=debug)
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


db_manager = DatabaseSessionManager()
