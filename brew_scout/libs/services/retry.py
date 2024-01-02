import dataclasses as dc
from collections import abc
import logging
import typing as t

import tenacity
from tenacity.wait import wait_base
from tenacity.stop import stop_base
from tenacity.retry import retry_base


T = t.TypeVar("T")
F = t.TypeVar("F", bound=abc.Callable[..., abc.Awaitable[t.Any]])
P = t.ParamSpec("P")


@dc.dataclass(frozen=True, slots=True)
class RetryService:
    logger: logging.Logger = dc.field(default=logging.getLogger(__name__))

    async def run_with_retry(self) -> T:
        return await self._with_retry()

    async def _with_retry(
        self,
        func: F,
        wait: wait_base,
        stop: stop_base,
        retry: retry_base,
        reraise: bool = True,
        *args: P.args,
        **kwargs: P.kwargs
    ) -> T:
        retryer = tenacity.AsyncRetrying(
            wait=wait,
            stop=stop,
            retry=retry,
            reraise=reraise,
            before=tenacity.before_log(self.logger, logging.DEBUG),
            after=tenacity.after_log(self.logger, logging.DEBUG),
        )

        return await retryer(func, *args, **kwargs)
