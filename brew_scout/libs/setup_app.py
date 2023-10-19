from collections import abc
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware import Middleware

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

from brew_scout import MODULE_NAME, DESCRIPTION, VERSION
from .settings import AppSettings, SETTINGS_KEY
from ..apis.v1.base import router as router_v1


def configure_db_session_factory(
    engine: AsyncEngine, factory: async_sessionmaker[AsyncSession]
) -> async_sessionmaker[AsyncSession]:
    factory.configure(bind=engine, expire_on_commit=False)
    return factory


def setup_app(settings: AppSettings) -> FastAPI:
    @asynccontextmanager
    async def app_lifespan(app: FastAPI) -> abc.AsyncIterator[None]:
        engine = create_async_engine(settings.database_dsn, echo=settings.debug)
        app.state.async_session_factory = configure_db_session_factory(engine, async_sessionmaker())

        try:
            yield
        finally:
            await engine.dispose()

    middlewares = [
        Middleware(
            CORSMiddleware,
            allow_origins=add_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    app = FastAPI(
        title=MODULE_NAME,
        version=VERSION,
        description=DESCRIPTION,
        middleware=middlewares,
        lifespan=app_lifespan,
        default_response_class=ORJSONResponse,
        **{SETTINGS_KEY: settings}  # type: ignore
    )

    app.include_router(router_v1)

    return app


def add_origins() -> abc.Sequence[str]:
    return "http://localhost:9090", "http://0.0.0.0:9090"
