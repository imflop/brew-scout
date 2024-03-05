from collections import abc
from contextlib import asynccontextmanager
import typing as t

import asyncio
from functools import partial

import aiohttp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware import Middleware
import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from brew_scout import MODULE_NAME, DESCRIPTION, VERSION
from .settings import AppSettings, SETTINGS_KEY
from .managers import db_manager
from ..apis.v1.base import router as router_v1

P = t.ParamSpec("P")


def setup_app(settings: AppSettings) -> FastAPI:
    @asynccontextmanager
    async def app_lifespan(app: FastAPI) -> abc.AsyncIterator[None]:
        app.state.client_session_getter = partial(session_getter, loop=asyncio.get_running_loop())
        db_manager.init(settings.database_dsn, settings.debug)

        try:
            yield
        finally:
            await db_manager.close()

    middlewares = [
        Middleware(
            CORSMiddleware,
            allow_origins=add_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        enable_tracing=True,
        integrations=[
            StarletteIntegration(
                transaction_style="url"
            ),
            FastApiIntegration(
                transaction_style="url"
            ),
        ],
    )

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


def session_getter(loop: asyncio.AbstractEventLoop, *args: P.args, **kwargs: P.kwargs) -> aiohttp.ClientSession:
    return aiohttp.ClientSession(loop=loop)


def add_origins() -> abc.Sequence[str]:
    return "http://localhost:9090", "http://0.0.0.0:9090"
