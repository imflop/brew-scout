from fastapi import Depends

from .clients import geo_client_factory, telegram_client_factory
from .repositories import city_repository_factory, coffee_shop_repository_factory
from ..clients.geo import GeoClient
from ..clients.telegram import TelegramClient
from ..services.city import CityService
from ..services.geo import GeoService
from ..services.shop import CoffeeShopService
from ..services.bus import BusService
from ..dal.city import CityRepository
from ..dal.shop import CoffeeShopRepository


def city_service_factory(city_repository: CityRepository = Depends(city_repository_factory)) -> CityService:
    return CityService(city_repository)


def coffee_shop_service_factory(
    coffee_shop_repository: CoffeeShopRepository = Depends(coffee_shop_repository_factory),
) -> CoffeeShopService:
    return CoffeeShopService(coffee_shop_repository)


def bus_service_factory(telegram_client: TelegramClient = Depends(telegram_client_factory)) -> BusService:
    return BusService(telegram_client)


def geo_service_factory(geo_client: GeoClient = Depends(geo_client_factory)) -> GeoService:
    return GeoService(geo_client)
