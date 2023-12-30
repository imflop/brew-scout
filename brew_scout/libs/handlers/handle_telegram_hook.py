import asyncio
import dataclasses as dc
import logging
from collections import abc

from ..dal.models.shops import CoffeeShopModel
from ..domains.telegram import TelegramMessage
from ..serializers.telegram import TelegramHookIn, Location
from ..serializers.telegram import Message
from ..services.bus.service import BusService
from ..services.geo.service import GeoService
from ..services.city import CityService
from ..services.shop import CoffeeShopService


@dc.dataclass(slots=True, repr=False)
class TelegramHookHandler:
    bus_service: BusService
    geo_service: GeoService
    city_service: CityService
    shop_service: CoffeeShopService

    logger: logging.Logger = dc.field(default_factory=lambda: logging.getLogger(__name__))

    async def process_hook(self, payload: TelegramHookIn) -> None:
        if self._does_message_start_conversation(payload.message):
            self.logger.info(f"Start message from {payload.message.chat}")
            return await self.bus_service.send_welcome_message(payload.message.chat.id)

        if not (location := self._does_message_contain_location(payload.message)):
            self.logger.info(f"Message is not <START> and without locations {payload.message}")
            return await self.bus_service.send_empty_location_message(payload.message.chat.id)

        if not (
            city := await self.city_service.try_to_find_city_from_coordinates(location.latitude, location.longitude)
        ):
            self.logger.info(f"City is not found by: {location.latitude} {location.longitude}")
            return await self.bus_service.send_city_not_found_message(payload.message.chat.id)

        if not (coffee_shops := await self.shop_service.get_coffee_shops_for_city(city.name)):
            return await self.bus_service.send_shops_not_found_message(payload.message.chat.id, city.name)

        nearest_coffee_shops = await self.geo_service.find_nearest_coffee_shops(location, coffee_shops)
        await self._send_message(payload.message.chat.id, nearest_coffee_shops)
        self.logger.info("Nearest coffee shops sent")

    @staticmethod
    def _does_message_start_conversation(msg: Message) -> bool:
        match msg.text:
            case TelegramMessage.START:
                return True
            case _:
                return False

    @staticmethod
    def _does_message_contain_location(msg: Message) -> Location | None:
        return msg.location or None

    async def _send_message(self, chat_id: int, coffee_shops: abc.Sequence[CoffeeShopModel]) -> None:
        await asyncio.gather(
            *(
                self.bus_service.send_nearest_coffee_shops_message(
                    chat_id=chat_id,
                    coffee_shop_latitude=coffee_shop.latitude,
                    coffee_shop_longitude=coffee_shop.longitude,
                    coffee_shop_name=coffee_shop.name,
                    coffee_shop_url=coffee_shop.web_url,
                )
                for coffee_shop in coffee_shops
            )
        )
