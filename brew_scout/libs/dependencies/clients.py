from fastapi import Depends

from .common import settings_factory, manager_provider_factory
from ..managers import ManagerProvider
from ..settings import AppSettings
from ..services.bus.client import TelegramClient
from ..services.geo.client import GeoClient


def telegram_client_factory(
    settings: AppSettings = Depends(settings_factory),
    manager_provider: ManagerProvider = Depends(manager_provider_factory),
) -> TelegramClient:
    return TelegramClient(
        api_url=f"{settings.telegram_api_url}/{settings.telegram_api_token}",
        client_session_manager=manager_provider.client_session_manager,
    )


def geo_client_factory() -> GeoClient:
    return GeoClient()
