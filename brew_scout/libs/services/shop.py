import dataclasses as dc
from collections import abc

from ..dal.shop import CoffeeShopRepository
from ..dal.models.shops import CoffeeShopModel
from ..domains.shops import CoffeeShop


@dc.dataclass(slots=True, repr=True, frozen=True)
class CoffeeShopService:
    repository: CoffeeShopRepository

    async def get_coffee_shops(self) -> abc.Sequence[CoffeeShopModel]:
        return await self.repository.get_all()

    async def get_coffee_shops_for_city(self, city_name: str) -> abc.Sequence[CoffeeShop]:
        if not (coffee_shops := await self.repository.get_by_city_name(city_name)):
            return []

        return [
            CoffeeShop.model_validate(cs)
            for cs in coffee_shops
        ]
