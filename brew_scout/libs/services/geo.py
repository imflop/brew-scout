import dataclasses as dc
import typing as t
from collections import abc

from ..clients.geo import GeoClient
from ..dal.models.shops import CoffeeShopModel
from ..serializers.geo import NominatimResponse


@dc.dataclass(frozen=True, slots=True, repr=False)
class GeoService:
    client: GeoClient
    default_language: str = "en"

    async def find_city_from_coordinates(self, latitude: float, longitude: float) -> abc.Sequence[float]:
        raw_result = await self._request(latitude, longitude)
        result = NominatimResponse.parse_obj(raw_result)

        return result.boundingbox

    async def find_nearest_coffee_shops(self, coffee_shops: abc.Sequence[CoffeeShopModel]) -> abc.Sequence[str]:
        return []

    async def _request(self, latitude: float, longitude: float) -> abc.Mapping[str, t.Any]:
        async with self.client() as geolocator:
            location = await geolocator.reverse((latitude, longitude), language=self.default_language)

            return location.raw
