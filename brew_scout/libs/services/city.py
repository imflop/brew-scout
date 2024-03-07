import dataclasses as dc
import logging
from collections import abc

from ..dal.city import CityRepository
from ..dal.models.cities import CityModel


@dc.dataclass(slots=True, repr=False, frozen=True)
class CityService:
    city_repository: CityRepository
    logger: logging.Logger = dc.field(default_factory=lambda: logging.getLogger(__name__))

    async def get_cities(self) -> abc.Sequence[CityModel]:
        return await self.city_repository.get_all()

    async def try_to_find_city_from_coordinates(self, latitude: float, longitude: float) -> CityModel | None:
        return await self.city_repository.get_city_by_coordinates(latitude, longitude)
