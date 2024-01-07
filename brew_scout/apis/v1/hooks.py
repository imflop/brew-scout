from fastapi import APIRouter, Depends, status

from ...libs.dependencies.common import on_async_session_factory, background_runner_factory, BackgroundRunner
from ...libs.dependencies.handlers import telegram_hook_handler_factory
from ...libs.serializers.telegram import TelegramHookIn
from ...libs.handlers.handle_telegram_hook import TelegramHookHandler


router = APIRouter(tags=["Hooks"])


@router.post("/hook/telegram", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(on_async_session_factory)])
async def handle_hook(
    hook_in: TelegramHookIn,
    bg_runner: BackgroundRunner = Depends(background_runner_factory),
    handler: TelegramHookHandler = Depends(telegram_hook_handler_factory),
) -> None:
    await bg_runner(handler.process_hook, payload=hook_in)
