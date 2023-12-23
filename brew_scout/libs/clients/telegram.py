import dataclasses as dc
import typing as t
from enum import StrEnum

import httpx


class HttpMethods(StrEnum):
    GET = "GET"
    POST = "POST"


@dc.dataclass(slots=True, repr=False)
class TelegramClient:
    api_url: str
    default_timeout: float = 35.0
    default_max_keepalive_connections: int = 5
    default_max_connections: int = 10

    async def post(self, url: str, data: t.Mapping[str, t.Any]) -> t.Mapping[str, t.Any]:
        response = await self._request(f"{self.api_url}/{url}", HttpMethods.POST, data)

        try:
            return response.json()
        except BaseException:
            return {}

    async def _request(
        self,
        url: str,
        method: str = HttpMethods.GET,
        params: t.Mapping[str, t.Any] | None = None,
        json: t.Mapping[str, t.Any] | None = None,
        data: t.Mapping[str, t.Any] | None = None,
    ) -> httpx.Response:
        async with httpx.AsyncClient(
            limits=self._get_limits(), headers=self._get_headers(), timeout=self.default_timeout
        ) as client:
            return await client.request(method=method, url=url, params=params, json=json, data=t.cast(dict, data))

    @staticmethod
    def _get_headers() -> httpx.Headers:
        return httpx.Headers({"Accept": "application/json"})

    def _get_limits(self) -> httpx.Limits:
        return httpx.Limits(
            max_keepalive_connections=self.default_max_keepalive_connections,
            max_connections=self.default_max_connections,
        )
