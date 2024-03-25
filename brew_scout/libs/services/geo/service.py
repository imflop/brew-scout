import dataclasses as dc
import typing as t
from collections import abc

from .client import GeoClient
from ...serializers.geo import NominatimResponseIn
from ...domains.shops import CoffeeShop


@dc.dataclass(frozen=True, slots=True)
class GeoService:
    client: GeoClient
    default_language: str = "en"

    async def find_nearest_coffee_shops(
        self, source_latitude: float, source_longitude: float, coffee_shops: abc.Sequence[CoffeeShop]
    ) -> abc.Sequence[CoffeeShop]:
        coffee_shops_with_distance = {}

        for cs in coffee_shops:
            distance = self.client.calculate_distance((source_latitude, source_longitude), (cs.latitude, cs.longitude))
            coffee_shops_with_distance[float(distance.kilometers)] = cs

        sorted_distances = sorted(coffee_shops_with_distance.keys())
        result = []

        for k in sorted_distances:
            cs = coffee_shops_with_distance[k]
            cs.distance = k
            result.append(cs.dict())

        return [CoffeeShop(**data) for data in result]

    async def find_city_from_coordinates(self, latitude: float, longitude: float) -> abc.Sequence[float]:
        raw_result = await self._request(latitude, longitude)
        result = NominatimResponseIn.parse_obj(raw_result)

        return result.boundingbox

    async def _request(self, latitude: float, longitude: float) -> abc.Mapping[str, t.Any]:
        async with self.client() as geolocator:
            location = await geolocator.reverse((latitude, longitude), language=self.default_language)

            return location.raw
