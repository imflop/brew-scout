import json
import typing as t
from collections import abc
from contextlib import asynccontextmanager
from types import TracebackType

import aiohttp
import yarl
from aiohttp.hdrs import METH_POST
from aiohttp.typedefs import StrOrURL

from brew_scout import MODULE_NAME, VERSION


# @dc.dataclass(slots=True, repr=False, init=False)
# @dc.dataclass(slots=True, repr=False)
class TelegramClient:
    # api_url: str
    # session_getter: abc.Callable[..., aiohttp.ClientSession]
    # default_timeout: float = 35.0
    # _session: aiohttp.ClientSession = dc.field(init=False)

    # def __init__(
    #     self,
    #     api_url: str,
    #     session_getter: abc.Callable[..., aiohttp.ClientSession],
    #     default_timeout: float = 35.0
    # ):
    #     self.api_url = api_url
    #     self._session = session_getter(
    #         timeout=aiohttp.ClientTimeout(total=default_timeout), headers=self._get_headers()
    #     )

    def __init__(
        self, api_url: str, session_getter: abc.Callable[..., aiohttp.ClientSession], default_timeout: float = 35.0
    ):
        self.api_url = api_url
        self.session_getter = session_getter
        self.default_timeout = default_timeout

    async def __aenter__(self) -> t.Self:
        return self

    async def __aexit__(self, exc_type: t.Type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> None:
        await self._session.close()

    async def cleanup(self) -> None:
        await self._session.close()

    @property
    def _session(self) -> aiohttp.ClientSession:
        if (session := self.__dict__.get("_session")) is None:
            session = self.session_getter(
                timeout=aiohttp.ClientTimeout(total=self.default_timeout), trust_env=False, headers=self._get_headers()
            )
            self.__dict__["_session"] = session

        return session

    async def post(self, url: str, data: abc.Mapping[str, t.Any]) -> abc.Mapping[str, t.Any]:
        return await self._json_request(METH_POST, f"{self.api_url}/{url}", data)

    async def _json_request(self, method: str, url: StrOrURL, data: abc.Mapping[str, t.Any]) -> abc.Mapping[str, t.Any]:
        async with self._request(method, url, data) as response:
            return await self._parse_json_response(response)

            # await response.read()

            # return await self._parse_json_response(response)
            # await response.read()
            #
            # try:
            #     response.raise_for_status()
            #
            #     return await self._parse_json_response(response)
            # except aiohttp.ClientResponseError as e:
            #     raise e

    @asynccontextmanager
    async def _request(
        self,
        method: str,
        url: StrOrURL,
        data: abc.Mapping[str, t.Any] | None = None,
    ) -> abc.AsyncIterator[aiohttp.ClientResponse]:
        if not yarl.URL(url).is_absolute():
            url = yarl.URL(self.api_url) / str(url).lstrip("/")

        async with self._session.request(method, url, data=data) as response:
            await response.read()

            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                raise e

            yield response

    # def _request(self, method: str, url: StrOrURL, **kwargs: t.Any) -> t.Any:
    #     if not yarl.URL(url).is_absolute():
    #         url = yarl.URL(self.api_url) / str(url).lstrip("/")
    #
    #     return self._session.request(method, url, **kwargs)

    @staticmethod
    def _get_headers() -> abc.Mapping[str, str]:
        return {"User-Agent": f"{MODULE_NAME}/{VERSION}", "Accept": "application/json"}

    @staticmethod
    async def _parse_json_response(response: aiohttp.ClientResponse) -> abc.Mapping[str, t.Any]:
        try:
            response_dict = await response.json()
        except (json.JSONDecodeError, aiohttp.ClientResponseError) as e:
            raise e

        return response_dict
