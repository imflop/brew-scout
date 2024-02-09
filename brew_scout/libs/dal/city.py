import typing as t
import uuid
from collections import abc

from sqlalchemy import select, BinaryExpression
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from .models.cities import CityModel
from .models.common import Base


CityId: t.TypeAlias = int
ModelIdFilter: t.TypeAlias = int | uuid.UUID
Model = t.TypeVar("Model", bound=Base)


class BaseRepository(t.Generic[Model]):
    def __init__(self, model: t.Type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id_filter: ModelIdFilter) -> Model | None:
        return await self.session.get(self.model, id_filter)

    async def filter(self, *expressions: BinaryExpression[t.Any]) -> abc.Sequence[Model]:
        q = select(self.model)

        if expressions:
            q = q.where(*expressions)

        return list(await self.session.scalars(q))


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
