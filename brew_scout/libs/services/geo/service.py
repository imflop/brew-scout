import dataclasses as dc
import typing as t
from collections import abc

from .client import GeoClient
from ...dal.models.shops import CoffeeShopModel
from ...serializers.geo import NominatimResponse
from ...serializers.telegram import Location


@dc.dataclass(frozen=True, slots=True)
class GeoService:
    client: GeoClient
    default_language: str = "en"

    async def find_nearest_coffee_shops(
        self, source_location: Location, coffee_shops: abc.Sequence[CoffeeShopModel]
    ) -> abc.Mapping[float, CoffeeShopModel]:
        coffee_shops_with_distance = {}

        for cs in coffee_shops:
            distance = self.client.calculate_distance(
                (source_location.latitude, source_location.longitude), (cs.latitude, cs.longitude)
            )

            coffee_shops_with_distance[float(distance.kilometers)] = cs

        sorted_distances = sorted(coffee_shops_with_distance.keys())

        return {k: coffee_shops_with_distance[k] for k in sorted_distances}

    async def find_city_from_coordinates(self, latitude: float, longitude: float) -> abc.Sequence[float]:
        raw_result = await self._request(latitude, longitude)
        result = NominatimResponse.parse_obj(raw_result)

        return result.boundingbox

    async def _request(self, latitude: float, longitude: float) -> abc.Mapping[str, t.Any]:
        async with self.client() as geolocator:
            location = await geolocator.reverse((latitude, longitude), language=self.default_language)

            return location.raw
