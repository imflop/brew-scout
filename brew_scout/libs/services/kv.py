import dataclasses as dc
import typing as t
from collections import abc

from redis.asyncio.client import Redis

from ..domains.shops import CoffeeShop


@dc.dataclass(slots=True, repr=True, frozen=True)
class KVService:
    client: Redis
    locations_key = "shops:{}:locations"

    async def get_coffee_shops(self, city_name: str) -> abc.Sequence[CoffeeShop]:
        cursor, result = await self.client.zscan(name=self.locations_key.format(city_name.lower()))

        if not result:
            return []

        parsed_result = self._parse_zscan_result(result)

        return [CoffeeShop(**data) for data in parsed_result]

    async def set_coffee_shops(
        self, city_name: str, coffee_shops: abc.Sequence[CoffeeShop], expiration_time: int = 600
    ) -> None:
        key = self.locations_key.format(city_name.lower())

        for cs in coffee_shops:
            await self.client.geoadd(
                name=key,
                values=(cs.longitude, cs.latitude, f"{cs.name}:{cs.latitude}:{cs.longitude}:{cs.web_url}"),
            )

        await self.client.expire(name=key, time=expiration_time)

    async def get_nearest_coffee_shops(
        self, city_name: str, source_latitude: float, source_longitude: float, radius: int = 1000
    ) -> abc.Sequence[CoffeeShop]:
        if not (
            geosearch_result := await self.client.geosearch(
                name=self.locations_key.format(city_name.lower()),
                latitude=source_latitude,
                longitude=source_longitude,
                radius=radius,
                withcoord=True,
                withdist=True,
                sort="ASC",
            )
        ):
            return []

        parsed_result = self._parse_geosearch_result(geosearch_result)

        return [CoffeeShop(**data) for data in parsed_result]

    @staticmethod
    def _parse_zscan_result(result: abc.Sequence[t.Tuple[str, float]]) -> abc.Sequence[abc.Mapping[str, t.Any]]:
        return [
            {"name": name, "latitude": latitude, "longitude": longitude, "web_url": web_url}
            for member, score in result
            for name, longitude, latitude, web_url in [member.split(":", 3)]
        ]

    @staticmethod
    def _parse_geosearch_result(
        result: abc.Sequence[t.Tuple[str, float, t.Tuple[float, float]]]
    ) -> abc.Sequence[abc.Mapping[str, t.Any]]:
        return [
            {
                "name": name,
                "distance": distance,
                "latitude": coordinates[0],
                "longitude": coordinates[1],
                "web_url": web_url,
            }
            for key, distance, coordinates in result
            for name, _, _, web_url in [key.split(":", 3)]
        ]
