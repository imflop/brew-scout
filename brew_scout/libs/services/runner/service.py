import dataclasses as dc
import typing as t
from collections import abc

from .retry import RetryService


T = t.TypeVar("T")


@dc.dataclass(frozen=True, slots=True)
class CommonRunnerService:
    retry_service: RetryService

    async def run_with_retry(
        self,
        func: abc.Callable[..., abc.Awaitable[T]],
        tries: int | None = None,
        pause: int | None = None,
        retry_exception: t.Any = Exception,
        *args: t.Any,
        **kwargs: t.Any
    ) -> T:
        return await self.retry_service.run_with_retry(func, tries, pause, retry_exception, *args, **kwargs)
