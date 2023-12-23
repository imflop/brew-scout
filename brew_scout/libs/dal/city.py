import dataclasses as dc
import typing as t
from collections import abc

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from .models.cities import CityModel
from ...vars import get_async_session


CityId: t.TypeAlias = int


@dc.dataclass(slots=True, repr=False)
class CityRepository:
    db: AsyncSession = dc.field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "db", get_async_session())

    async def get_one_or_none(self, city_id: CityId) -> CityModel | None:
        q = select(CityModel).options(joinedload(CityModel.country)).where(CityModel.id == city_id)

        result = await self.db.scalars(q)

        return result.one_or_none()

    async def get_all(self) -> abc.Sequence[CityModel]:
        q = select(CityModel).options(joinedload(CityModel.country))

        result = await self.db.scalars(q)

        return result.all()

    async def get_city_by_coordinates(self, latitude: float, longitude: float) -> CityModel | None:
        q = select(CityModel).filter(
            (CityModel.bounding_box_min_latitude <= latitude)
            & (CityModel.bounding_box_max_latitude >= latitude)
            & (CityModel.bounding_box_min_longitude <= longitude)
            & (CityModel.bounding_box_max_longitude >= longitude)
        ).options(joinedload(CityModel.country))

        result = await self.db.scalars(q)

        return result.one_or_none()
