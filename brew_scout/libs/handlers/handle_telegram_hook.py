import dataclasses as dc
import logging

from ..domains.telegram import TelegramMessage
from ..serializers.telegram import TelegramHookIn
from ..serializers.telegram import Message
from ..services.bus import BusService
from ..services.geo import GeoService
from ..services.city import CityService
from ..services.shop import CoffeeShopService


@dc.dataclass(slots=True, repr=False)
class TelegramHookUseCase:
    bus_service: BusService
    geo_service: GeoService
    city_service: CityService
    shop_service: CoffeeShopService
    logger: logging.Logger = dc.field(default_factory=lambda: logging.getLogger(__name__))

    async def process_hook(self, payload: TelegramHookIn) -> None:
        if self._does_message_start_conversation(payload.message):
            self.logger.info(f"Start message from {payload.message.chat}")
            return await self.bus_service.send_welcome_message(payload.message.chat.id)

        if not self._does_message_contain_location(payload.message):
            self.logger.info(f"Message is not <START> and without locations {payload.message}")
            return await self.bus_service.send_empty_location_message(payload.message.chat.id)

        if not (
            city := await self.city_service.try_to_find_city_from_coordinates(
                payload.message.location.latitude, payload.message.location.longitude
            )
        ):
            self.logger.info(
                f"City is not found by: {payload.message.location.latitude} {payload.message.location.longitude}"
            )
            return await self.bus_service.send_city_not_found_message(payload.message.chat.id)

        if not (coffee_shops := await self.shop_service.get_coffee_shops_for_city(city.name)):
            return await self.bus_service.send_shops_not_found_message(payload.message.chat.id, city.name)

        nearest_coffee_shops = await self.geo_service.find_nearest_coffee_shops(coffee_shops)
        await self.bus_service.send_nearest_coffee_shops_message(payload.message.chat.id, nearest_coffee_shops)

    @staticmethod
    def _does_message_start_conversation(msg: Message) -> bool:
        match msg.text:
            case TelegramMessage.START:
                return True
            case _:
                return False

    @staticmethod
    def _does_message_contain_location(msg: Message) -> bool:
        return bool(msg.location)
