from fastapi import Depends

from .services import (
    bus_service_factory,
    geo_service_factory,
    coffee_shop_service_factory,
    city_service_factory,
    kv_service_factory,
)
from ..services.bus.service import BusService
from ..services.city import CityService
from ..services.shop import CoffeeShopService
from ..services.geo.service import GeoService
from ..services.kv import KVService
from ..handlers.handle_telegram_hook import TelegramHookHandler


def telegram_hook_handler_factory(
    bus_service: BusService = Depends(bus_service_factory),
    geo_service: GeoService = Depends(geo_service_factory),
    city_service: CityService = Depends(city_service_factory),
    coffee_shop_service: CoffeeShopService = Depends(coffee_shop_service_factory),
    kv_service: KVService = Depends(kv_service_factory),
) -> TelegramHookHandler:
    return TelegramHookHandler(
        bus_service=bus_service,
        geo_service=geo_service,
        city_service=city_service,
        shop_service=coffee_shop_service,
        kv_service=kv_service,
    )
