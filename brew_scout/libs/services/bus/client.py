import dataclasses as dc
import json
import typing as t
from collections import abc
from contextlib import asynccontextmanager
from http import HTTPMethod

import aiohttp
import yarl
from aiohttp.typedefs import StrOrURL

from brew_scout import MODULE_NAME, VERSION
from brew_scout.libs.managers import ClientSessionManager


@dc.dataclass(frozen=True, slots=True, repr=False)
class TelegramClient:
    api_url: str
    client_session_manager: ClientSessionManager
    _session: aiohttp.ClientSession = dc.field(init=False)

    default_timeout: float = 35.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_session",
            self.client_session_manager.get_session(
                timeout=aiohttp.ClientTimeout(total=self.default_timeout),
                headers=self._get_headers(),
                trust_env=False,
            ),
        )

    async def cleanup(self) -> None:
        await self._session.close()

    async def post(self, telegram_method: str, data: abc.Mapping[str, t.Any]) -> abc.Mapping[str, t.Any]:
        return await self._json_request(HTTPMethod.POST, f"{self.api_url}/{telegram_method}", data)

    async def _json_request(self, method: str, url: StrOrURL, data: abc.Mapping[str, t.Any]) -> abc.Mapping[str, t.Any]:
        async with self._request(method, url, data) as response:
            return await self._parse_json_response(response)

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
