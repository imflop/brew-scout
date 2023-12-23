import dataclasses as dc
import typing as t

from ..clients.telegram import TelegramClient
from ..domains.telegram import TelegramMethods, Button, Keyboard


@dc.dataclass(frozen=True, repr=False, slots=True)
class BusService:
    client: TelegramClient

    async def send_welcome_message(self, chat_id: int) -> None:
        welcome_message = "Hello there, send me your location"
        keyboard = Keyboard(keyboard=[[Button(text="📍 Current location", request_location=True)]])
        data_to_sent = self._construct_sending_data(chat_id=chat_id, message=welcome_message, keyboard=keyboard)
        await self._send_text_message(data_to_sent)

    async def send_empty_location_message(self, chat_id: int) -> None:
        error_message = "Sorry but you should share your location, use button below for that"
        data_to_sent = self._construct_sending_data(chat_id=chat_id, message=error_message)
        await self._send_text_message(data_to_sent)

    async def send_city_not_found_message(self, chat_id: int) -> None:
        error_message = "Sorry but right now your city not added yet"
        data_to_sent = self._construct_sending_data(chat_id=chat_id, message=error_message)
        await self._send_text_message(data_to_sent)

    async def send_shops_not_found_message(self, chat_id: int, city_name: str) -> None:
        error_message = f"Sorry but can't find coffee shops from you city: {city_name}"
        data_to_sent = self._construct_sending_data(chat_id=chat_id, message=error_message)
        await self._send_text_message(data_to_sent)

    async def send_nearest_coffee_shops_message(
        self, chat_id: int, coffee_shop_name: str, coffee_shop_url: str
    ) -> None:
        message = f"{coffee_shop_name}\n{coffee_shop_url}"
        data_to_sent = self._construct_sending_data(chat_id=chat_id, message=message)
        await self._send_text_message(data_to_sent)

    async def _send_text_message(self, sending_data: t.Mapping[str, t.Any]) -> None:
        await self.client.post(TelegramMethods.SEND_MESSAGE, sending_data)

    @staticmethod
    def _construct_sending_data(chat_id: int, message: str, keyboard: Keyboard | None = None) -> t.Mapping[str, t.Any]:
        return {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "html",
            "reply_markup": keyboard.json() if keyboard else None,
        }
