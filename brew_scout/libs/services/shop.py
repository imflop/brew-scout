import dataclasses as dc
from collections import abc

from ..dal.shop import CoffeeShopRepository
from ..dal.models.shops import CoffeeShopModel
from ..domains.shops import CoffeeShop


@dc.dataclass(slots=True, repr=True, frozen=True)
class CoffeeShopService:
    coffee_shop_repository: CoffeeShopRepository

    async def get_coffee_shops(self) -> abc.Sequence[CoffeeShopModel]:
        return await self.coffee_shop_repository.get_all()

    async def get_coffee_shops_for_city(self, city_name: str) -> abc.Sequence[CoffeeShop]:
        if coffee_shops := await self.coffee_shop_repository.get_by_city_name(city_name):
            return [
                CoffeeShop(
                    **{"name": cs.name, "latitude": cs.latitude, "longitude": cs.longitude, "web_url": cs.web_url}
                )
                for cs in coffee_shops
            ]

        return []
