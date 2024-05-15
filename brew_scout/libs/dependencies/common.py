import typing as t
from collections import abc

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis
from starlette.background import BackgroundTasks
from starlette.requests import Request

from ..settings import AppSettings, SETTINGS_KEY
from ..managers import ManagerProvider


T = t.TypeVar("T")
P = t.ParamSpec("P")
BackgroundRunner = abc.Callable[..., abc.Awaitable[None]]


def settings_factory(request: Request) -> AppSettings:
    return request.app.extra[SETTINGS_KEY]


def manager_provider_factory(request: Request) -> ManagerProvider:
    return request.app.state.manager_provider


async def get_db_session(
    manager_provider: ManagerProvider = Depends(manager_provider_factory),
) -> t.AsyncGenerator[AsyncSession, None]:
    async with manager_provider.database_session_manager.session() as session:
        yield session


async def get_rds_session(
    manager_provider: ManagerProvider = Depends(manager_provider_factory),
) -> abc.AsyncGenerator[Redis, None]:
    async with manager_provider.redis_session_manager.session() as redis_client:
        yield redis_client


async def background_runner_factory(request: Request, background_tasks: BackgroundTasks) -> BackgroundRunner:
    run_now = bool(request.query_params.get("run_now", False))

    async def background_runner(func: abc.Callable[P, abc.Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> None:
        if run_now:
            await func(*args, **kwargs)
            return

        # Run the function in the background
        background_tasks.add_task(func, *args, **kwargs)
        return

    return background_runner
