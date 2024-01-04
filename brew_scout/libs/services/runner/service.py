import dataclasses as dc
import typing as t
from collections import abc

from .retry import RetryService


T = t.TypeVar("T")
F = t.TypeVar("F", bound=abc.Callable[..., abc.Awaitable[t.Any]])
P = t.ParamSpec("P")


@dc.dataclass(frozen=True, slots=True)
class CommonRunnerService:
    retry_service: RetryService

    async def run_with_retry(
        self,
        func: F,
        tries: int | None = None,
        pause: int | None = None,
        retry_exception: t.Any = Exception,
        *args: P.args,
        **kwargs: P.kwargs
    ) -> T:
        return await self.retry_service.run_with_retry(
            func=func, tries=tries, pause=pause, retry_exception=retry_exception, *args, **kwargs
        )
