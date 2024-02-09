from collections import abc

from sqlalchemy import select, LABEL_STYLE_TABLENAME_PLUS_COL
from sqlalchemy.orm import joinedload

from .city import BaseRepository
from .models.shops import CoffeeShopModel
from .models.cities import CityModel


class CoffeeShopRepository(BaseRepository[CoffeeShopModel]):
    async def get_all(self) -> abc.Sequence[CoffeeShopModel]:
        q = (
            select(CoffeeShopModel)
            .options(joinedload(CoffeeShopModel.city).joinedload(CityModel.country))
            .set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)
        )

        result = await self.session.scalars(q)

        return result.all()

    async def get_by_city_name(self, city_name: str) -> abc.Sequence[CoffeeShopModel]:
        q = (
            select(CoffeeShopModel)
            .join(CoffeeShopModel.city)
            .options(joinedload(CoffeeShopModel.city))
            .where(CityModel.name.ilike(city_name))
        )

        result = await self.session.scalars(q)

        return result.all()
