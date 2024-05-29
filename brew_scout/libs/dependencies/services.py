from fastapi import Depends

from redis.asyncio.client import Redis

from .common import get_rds_session
from .clients import geo_client_factory, telegram_client_factory
from .repositories import (
    city_repository_factory,
    coffee_shop_repository_factory,
    user_repository_factory,
)
from ..dal.user import UserRepository
from ..dal.city import CityRepository
from ..dal.shop import CoffeeShopRepository
from ..services.geo.client import GeoClient
from ..services.city import CityService
from ..services.geo.service import GeoService
from ..services.kv import KVService
from ..services.shop import CoffeeShopService
from ..services.bus.service import BusService
from ..services.bus.client import TelegramClient
from ..services.runner.retry import RetryService
from ..services.runner.service import CommonRunnerService
from ..services.user import UserService


def city_service_factory(city_repository: CityRepository = Depends(city_repository_factory)) -> CityService:
    return CityService(city_repository)


def coffee_shop_service_factory(
    coffee_shop_repository: CoffeeShopRepository = Depends(coffee_shop_repository_factory),
) -> CoffeeShopService:
    return CoffeeShopService(coffee_shop_repository)


def retry_service_factory() -> RetryService:
    return RetryService()


def common_runner_service_factory(retry_service: RetryService = Depends(retry_service_factory)) -> CommonRunnerService:
    return CommonRunnerService(retry_service)


def bus_service_factory(
    telegram_client: TelegramClient = Depends(telegram_client_factory),
    common_runner_service: CommonRunnerService = Depends(common_runner_service_factory),
) -> BusService:
    return BusService(telegram_client, common_runner_service)


def geo_service_factory(geo_client: GeoClient = Depends(geo_client_factory)) -> GeoService:
    return GeoService(geo_client)


def kv_service_factory(client: Redis = Depends(get_rds_session)) -> KVService:
    return KVService(client)


def user_service_factory(user_repository: UserRepository = Depends(user_repository_factory)) -> UserService:
    return UserService(user_repository)
