from fastapi import Depends

from .services import bus_service_factory, geo_service_factory, coffee_shop_service_factory
from ..services.bus import BusService
from ..services.shop import CoffeeShopService
from ..services.geo import GeoService
from ..handlers.handle_telegram_hook import TelegramHookUseCase


def telegram_hook_use_case_factory(
    bus_service: BusService = Depends(bus_service_factory),
    geo_service: GeoService = Depends(geo_service_factory),
    coffee_shop_service: CoffeeShopService = Depends(coffee_shop_service_factory),
) -> TelegramHookUseCase:
    return TelegramHookUseCase(bus_service, geo_service, coffee_shop_service)
