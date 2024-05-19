import json
from collections import abc
from contextlib import asynccontextmanager
from pathlib import Path
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware import Middleware
import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqladmin import Admin, ModelView

from brew_scout import MODULE_NAME, DESCRIPTION, VERSION
from .dal.models.shops import CoffeeShopModel
from .settings import AppSettings, SETTINGS_KEY
from .managers import ManagerProvider, DatabaseSessionManager, RedisSessionManager, ClientSessionManager
from ..apis.v1.base import router as router_v1


def setup_app(settings: AppSettings) -> FastAPI:
    @asynccontextmanager
    async def app_lifespan(app: FastAPI) -> abc.AsyncIterator[None]:
        manager_provider = ManagerProvider(
            settings=settings,
            database_session_manager=DatabaseSessionManager(),
            redis_session_manager=RedisSessionManager(),
            client_session_manager=ClientSessionManager(),
        )
        manager_provider.start()
        app.state.manager_provider = manager_provider

        admin = Admin(app, manager_provider.database_session_manager.get_engine(), debug=True)

        class CoffeeShopModelAdmin(ModelView, model=CoffeeShopModel):
            column_list = [CoffeeShopModel.id, CoffeeShopModel.name, CoffeeShopModel.city, CoffeeShopModel.created_at]
            column_details_list = [CoffeeShopModel.id, CoffeeShopModel.name, "shops.city.name"]
            form_ajax_refs = {
                "city": {
                    "fields": ("id", "name"),
                    "order_by": "id",
                }
            }

        admin.add_view(CoffeeShopModelAdmin)

        setup_logging()

        try:
            yield
        finally:
            await manager_provider.stop()

    middlewares = [
        Middleware(
            CORSMiddleware,
            allow_origins=add_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            enable_tracing=True,
            integrations=[
                StarletteIntegration(transaction_style="url"),
                FastApiIntegration(transaction_style="url"),
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


def add_origins() -> abc.Sequence[str]:
    return "http://localhost:9090", "http://0.0.0.0:9090"


def setup_logging() -> None:
    current_path = Path(__file__)
    config_file = None

    for parent_directory in current_path.parents:
        if (parent_directory / "log_cfg.json").is_file():
            config_file = parent_directory / "log_cfg.json"

    if config_file:
        with open(config_file) as cfg_file:
            config = json.load(cfg_file)

        logging.config.dictConfig(config)

        for _log in ["uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine.Engine"]:
            # Clear the log handlers for uvicorn loggers, and enable propagation
            # so the messages are caught by our root logger and formatted as we want
            logging.getLogger(_log).handlers.clear()
            logging.getLogger(_log).propagate = True
