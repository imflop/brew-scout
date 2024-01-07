import typing as t
from collections import abc

from aiohttp import ClientSession
from fastapi import Request, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession

from brew_scout.vars import set_async_session
from ..settings import AppSettings, SETTINGS_KEY


T = t.TypeVar("T")
P = t.ParamSpec("P")
BackgroundRunner = abc.Callable[..., abc.Awaitable[None]]


def settings_factory(request: Request) -> AppSettings:
    return request.app.extra[SETTINGS_KEY]


def client_session_factory(request: Request) -> abc.Callable[..., ClientSession]:
    return request.app.state.client_session_getter


async def on_async_session_factory(request: Request) -> t.AsyncIterator[AsyncSession]:
    async_session_factory = request.app.state.async_session_factory

    async with async_session_factory() as session:
        set_async_session(session)
        yield session


async def background_runner_factory(request: Request, background_tasks: BackgroundTasks) -> BackgroundRunner:
    run_now = request.query_params.get("run_now", False)

    async def background_runner(func: abc.Callable[P, abc.Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> None:
        if run_now:
            await func(*args, **kwargs)
            return

        # Run the function in the background
        background_tasks.add_task(func, *args, **kwargs)
        return

    return background_runner
