import typing as t

from collections import abc

from sqlalchemy import select
from sqlalchemy.orm import joinedload


from .models.common import BaseRepository
from .models.shops import CityModel


CityId: t.TypeAlias = int


class CityRepository(BaseRepository[CityModel]):
    async def get_all(self) -> abc.Sequence[CityModel]:
        q = select(CityModel).options(joinedload(CityModel.country))

        result = await self.session.scalars(q)

        return result.all()

    async def get_city_by_coordinates(self, latitude: float, longitude: float) -> CityModel | None:
        q = (
            select(CityModel)
            .join(CityModel.country)
            .options(joinedload(CityModel.country))
            .filter(
                (CityModel.bounding_box_min_latitude <= latitude)
                & (CityModel.bounding_box_max_latitude >= latitude)
                & (CityModel.bounding_box_min_longitude <= longitude)
                & (CityModel.bounding_box_max_longitude >= longitude)
            )
        )

        result = await self.session.scalars(q)

        return result.one_or_none()
