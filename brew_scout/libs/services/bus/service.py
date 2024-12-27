import dataclasses as dc
import typing as t
import logging
from collections import abc
from functools import partial

from .client import TelegramClient
from ..runner.service import CommonRunnerService
from ...domains.shops import CoffeeShop
from ...domains.telegram import TelegramMethods
from ...serializers.telegram import ReplyKeyboardOut, InlineKeyboardOut


@dc.dataclass(frozen=True, repr=False, slots=True)
class BusService:
    telegram_client: TelegramClient
    runner_service: CommonRunnerService

    logger: logging.Logger = dc.field(default_factory=lambda: logging.getLogger(__name__))

    async def send_welcome_message(self, chat_id: int) -> None:
        welcome_message = "Hi there, send me your location and I will try to find some coffee shops in your area."
        data_to_sent = self._make_text_message_data(chat_id=chat_id, message=welcome_message, is_request_location=True)
        await self._send_text_message(data_to_sent)

    async def send_empty_location_message(self, chat_id: int) -> None:
        error_message = "Sorry, but you need to share your location, use the button below for that message"
        data_to_sent = self._make_text_message_data(chat_id=chat_id, message=error_message)
        await self._send_text_message(data_to_sent)

    async def send_city_not_found_message(self, chat_id: int) -> None:
        error_message = "Sorry, your city has not been added yet."
        data_to_sent = self._make_text_message_data(chat_id=chat_id, message=error_message)
        await self._send_text_message(data_to_sent)

    async def send_shops_not_found_message(self, chat_id: int, city_name: str) -> None:
        error_message = f"Sorry but can't find any coffee shops from your city: {city_name}"
        data_to_sent = self._make_text_message_data(chat_id=chat_id, message=error_message)
        await self._send_text_message(data_to_sent)

    async def send_nearest_coffee_shops_message(
        self,
        chat_id: int,
        coffee_shop: CoffeeShop,
    ) -> None:
        if coffee_shop.distance is None:
            self.logger.error(
                "The coffee shop will not be sent because the distance has not been calculated",
                extra={"chat_id": chat_id, "coffee_shop_name": coffee_shop.name},
            )
            return

        data_to_sent = self._make_venue_message_data(
            chat_id=chat_id,
            latitude=coffee_shop.latitude,
            longitude=coffee_shop.longitude,
            name=coffee_shop.name,
            url=coffee_shop.web_url,
            distance=coffee_shop.distance,
        )
        await self._send_venue_message(data_to_sent)

    async def _send_text_message(self, sending_data: abc.Mapping[str, t.Any]) -> None:
        run_me = partial(self._send_message, telegram_method=TelegramMethods.SEND_MESSAGE, data=sending_data)
        await self.runner_service.run_with_retry(run_me)

    async def _send_venue_message(self, sending_data: abc.Mapping[str, t.Any]) -> None:
        run_me = partial(self._send_message, telegram_method=TelegramMethods.SEND_VENUE, data=sending_data)
        await self.runner_service.run_with_retry(run_me)

    async def _send_message(self, telegram_method: TelegramMethods, data: abc.Mapping[str, t.Any]) -> None:
        await self.telegram_client.post(telegram_method, data)

    @staticmethod
    def _make_text_message_data(
        chat_id: int, message: str, is_request_location: bool = False
    ) -> abc.Mapping[str, t.Any]:
        result = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "html",
        }

        if is_request_location:
            keyboard = ReplyKeyboardOut(**{"keyboard": [[{"text": "📍 Current location", "request_location": True}]]})
            result["reply_markup"] = keyboard.json()

        return result

    @staticmethod
    def _make_venue_message_data(
        chat_id: int, latitude: float, longitude: float, name: str, url: str, distance: float
    ) -> abc.Mapping[str, t.Any]:
        if distance < 1.0:
            formatted_distance = f"~ {distance * 1000:.0f} m away"
        else:
            formatted_distance = f"~ {distance:.2f} km away"

        keyboard = InlineKeyboardOut(**{"inline_keyboard": [[{"text": "🌐 / 📷 Link", "url": url}]]})

        return {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "title": name,
            "address": formatted_distance,
            "reply_markup": keyboard.json(),
        }
