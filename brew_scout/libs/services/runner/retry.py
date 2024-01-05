import asyncio
import dataclasses as dc
from collections import abc
import logging
import typing as t

import tenacity
from tenacity import RetryError, RetryCallState
from tenacity.wait import wait_base
from tenacity.stop import stop_base
from tenacity.retry import retry_base


T = t.TypeVar("T")
P = t.ParamSpec("P")
RetryErrorCallback = abc.Callable[[RetryCallState], t.Any]


@dc.dataclass(frozen=True, slots=True)
class RetryService:
    default_tries: int = 2
    default_pause: int = 30
    logger: logging.Logger = dc.field(default=logging.getLogger(__name__))

    async def run_with_retry(
        self,
        func: abc.Callable[..., abc.Awaitable[T]],
        tries: int | None = None,
        pause: int | None = None,
        reraise: bool = True,
        retry_exception: t.Any | None = Exception,
        retry_error_callback: RetryErrorCallback | None = None,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> T:
        if tries is None:
            tries = self.default_tries

        if pause is None:
            pause = self.default_pause

        return await self._with_retry(
            func,
            wait=tenacity.wait_fixed(pause) if pause else tenacity.wait_none(),
            stop=tenacity.stop_after_attempt(tries) if tries else tenacity.stop_never,
            retry=self._get_retry_predicate(retry_exception),
            reraise=reraise,
            retry_error_callback=retry_error_callback,
            *args,
            **kwargs,
        )  # type: ignore

    async def _with_retry(
        self,
        func: abc.Callable[..., abc.Awaitable[T]],
        wait: wait_base,
        stop: stop_base,
        retry: retry_base,
        reraise: bool = True,
        retry_error_callback: RetryErrorCallback | None = None,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> T:
        retrying = tenacity.AsyncRetrying(
            wait=wait,
            stop=stop,
            retry=retry,
            sleep=asyncio.sleep,
            reraise=reraise,
            retry_error_cls=RetryError,
            retry_error_callback=retry_error_callback,
            before=tenacity.before_log(self.logger, logging.DEBUG),
            after=tenacity.after_log(self.logger, logging.DEBUG),
        )

        return await retrying(func, *args, **kwargs)

    @staticmethod
    def _get_retry_predicate(exception_type: t.Any) -> retry_base:
        if isinstance(exception_type, retry_base):
            return exception_type

        if not isinstance(exception_type, type) and callable(exception_type):
            return tenacity.retry_if_exception(predicate=exception_type)
        else:
            return tenacity.retry_if_exception(
                predicate=lambda e: isinstance(e, exception_type) and not isinstance(e, asyncio.CancelledError)
            )
