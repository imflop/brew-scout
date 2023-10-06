from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from brew_scout.vars import get_async_session
from ..dal.city import CityRepository
from ..dal.shop import CoffeeShopRepository


def city_repository_factory() -> CityRepository:
    return CityRepository()


def coffee_shop_repository_factory() -> CoffeeShopRepository:
    return CoffeeShopRepository()
