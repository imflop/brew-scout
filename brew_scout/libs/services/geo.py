import dataclasses as dc
import typing as t
from collections import abc

from geopy.distance import distance, Distance

from ..clients.geo import GeoClient
from ..dal.models.shops import CoffeeShopModel
from ..serializers.geo import NominatimResponse
from ..serializers.telegram import Location


@dc.dataclass(frozen=True, slots=True, repr=False)
class GeoService:
    client: GeoClient
    default_language: t.ClassVar[str] = "en"

    async def find_city_from_coordinates(self, latitude: float, longitude: float) -> abc.Sequence[float]:
        raw_result = await self._request(latitude, longitude)
        result = NominatimResponse.parse_obj(raw_result)

        return result.boundingbox

    async def find_nearest_coffee_shops(
        self, init_location: Location, coffee_shops: abc.Sequence[CoffeeShopModel]
    ) -> abc.Sequence[CoffeeShopModel]:
        sorted_coffee_shops_coordinates = sorted(
            coffee_shops,
            key=lambda coffee_shop: self._calculate_distance(
                (init_location.latitude, init_location.longitude),
                (coffee_shop.latitude, coffee_shop.longitude)
            ),
        )

        return sorted_coffee_shops_coordinates[:3]

    async def _request(self, latitude: float, longitude: float) -> abc.Mapping[str, t.Any]:
        async with self.client() as geolocator:
            location = await geolocator.reverse((latitude, longitude), language=self.default_language)

            return location.raw

    @staticmethod
    def _calculate_distance(
        init_coordinates: abc.Sequence[float], coffee_shop_coordinates: abc.Sequence[float]
    ) -> Distance:
        return distance(init_coordinates, coffee_shop_coordinates).kilometers
