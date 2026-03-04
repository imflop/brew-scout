from fastapi import Depends

from .common import resource_provider_factory
from ..managers import ResourceProvider
from ..handlers.handle_telegram_hook import TelegramHookHandler


async def telegram_hook_handler_factory(rp: ResourceProvider = Depends(resource_provider_factory)) -> TelegramHookHandler:
    return rp.telegram_hook_handler
