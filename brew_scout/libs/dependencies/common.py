import typing as t
from collections import abc

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis
from starlette.background import BackgroundTasks
from starlette.requests import Request

from ..settings import AppSettings, SETTINGS_KEY
from ..managers import ResourceProvider


T = t.TypeVar("T")
P = t.ParamSpec("P")
BackgroundRunner = abc.Callable[..., abc.Awaitable[None]]


async def settings_factory(request: Request) -> AppSettings:
    return request.app.extra[SETTINGS_KEY]


async def resource_provider_factory(request: Request) -> ResourceProvider:
    return request.app.state.manager_provider


async def get_db_session(
    rp: ResourceProvider = Depends(resource_provider_factory),
) -> t.AsyncGenerator[AsyncSession, None]:
    async with rp.database_session_manager.session() as session:
        yield session


async def get_rds_session(rp: ResourceProvider = Depends(resource_provider_factory)) ->Redis:
    return rp.redis_session_manager.get_client()


async def get_oauth_client(rp: ResourceProvider = Depends(resource_provider_factory)) -> t.Any:
    return rp.oauth_client_manager.get_client()


async def background_runner_factory(request: Request, background_tasks: BackgroundTasks) -> BackgroundRunner:
    run_now = bool(request.query_params.get("run_now", False))

    async def background_runner(func: abc.Callable[P, abc.Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> None:
        if run_now:
            await func(*args, **kwargs)
            return None

        # Run the function in the background
        return background_tasks.add_task(func, *args, **kwargs)

    return background_runner
