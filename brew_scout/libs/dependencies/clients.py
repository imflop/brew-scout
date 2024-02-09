from fastapi import Depends
from aiohttp import ClientSession
from collections import abc

from .common import settings_factory, client_session_factory
from ..settings import AppSettings
from ..services.bus.client import TelegramClient
from ..services.geo.client import GeoClient


def telegram_client_factory(
    settings: AppSettings = Depends(settings_factory),
    session_getter: abc.Callable[..., ClientSession] = Depends(client_session_factory),
) -> TelegramClient:
    return TelegramClient(
        api_url=f"{settings.telegram_api_url}/{settings.telegram_api_token}",
        session_getter=session_getter,
    )


def geo_client_factory() -> GeoClient:
    return GeoClient()
