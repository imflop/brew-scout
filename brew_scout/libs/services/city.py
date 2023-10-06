import dataclasses as dc
from collections import abc

from ..dal.city import CityRepository
from ..dal.models.cities import CityModel


@dc.dataclass(slots=True, repr=False, frozen=True)
class CityService:
    city_repository: CityRepository

    async def get_cities(self) -> abc.Sequence[CityModel]:
        return await self.city_repository.get_all()

    async def try_to_find_city_from_coordinates(self, latitude: float, longitude: float) -> CityModel | None:
        return await self.city_repository.get_city_by_coordinates(latitude, longitude)
