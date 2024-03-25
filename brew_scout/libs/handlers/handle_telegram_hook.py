import asyncio
import dataclasses as dc
import logging
from collections import abc

from ..domains.telegram import TelegramMessage
from ..domains.shops import CoffeeShop
from ..serializers.telegram import TelegramHookIn, Location
from ..serializers.telegram import Message
from ..services.bus.service import BusService
from ..services.geo.service import GeoService
from ..services.city import CityService
from ..services.shop import CoffeeShopService
from ..services.kv import KVService


@dc.dataclass(slots=True, repr=False)
class TelegramHookHandler:
    bus_service: BusService
    geo_service: GeoService
    city_service: CityService
    shop_service: CoffeeShopService
    kv_service: KVService

    default_quantity_for_response: int = 2
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

        if not (coffee_shops := await self._get_coffee_shops_for_city(city.name)):
            return await self.bus_service.send_shops_not_found_message(payload.message.chat.id, city.name)

        nearest_coffee_shops = await self._find_nearby_coffee_shops(city.name, location, coffee_shops)
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

    async def _get_coffee_shops_for_city(self, city_name: str) -> abc.Sequence[CoffeeShop]:
        if coffee_shops_from_rds := await self.kv_service.get_coffee_shops(city_name):
            self.logger.info(f"Return coffee shops from cache for {city_name}", extra={"city": city_name})
            return coffee_shops_from_rds

        if coffee_shops_from_db := await self.shop_service.get_coffee_shops_for_city(city_name):
            self.logger.info(f"Return coffee shops from db for {city_name}", extra={"city": city_name})
            await self.kv_service.set_coffee_shops(city_name, coffee_shops_from_db)

            return coffee_shops_from_db

        return []

    async def _find_nearby_coffee_shops(
        self, city_name: str, location: Location, coffee_shops: abc.Sequence[CoffeeShop]
    ) -> abc.Sequence[CoffeeShop]:
        if nearest_coffee_shops_from_rds := await self.kv_service.get_nearest_coffee_shops(
            city_name=city_name,
            source_latitude=location.latitude,
            source_longitude=location.longitude,
        ):
            self.logger.info(f"Returning nearby coffee shops from cache for {city_name}", extra={"city": city_name})
            return nearest_coffee_shops_from_rds[: self.default_quantity_for_response]

        if nearest_coffee_shops_from_db := await self.geo_service.find_nearest_coffee_shops(
            source_latitude=location.latitude,
            source_longitude=location.longitude,
            coffee_shops=coffee_shops,
        ):
            self.logger.info(f"Returning nearby coffee shops from db for {city_name}", extra={"city": city_name})
            return nearest_coffee_shops_from_db[: self.default_quantity_for_response]

        return []

    async def _send_message(self, chat_id: int, coffee_shops: abc.Sequence[CoffeeShop]) -> None:
        gathered_result = await asyncio.gather(
            *(
                self.bus_service.send_nearest_coffee_shops_message(chat_id=chat_id, coffee_shop=coffee_shop)
                for coffee_shop in coffee_shops
            ),
            return_exceptions=True,
        )

        if errors := {
            repr(result_or_error) for result_or_error in gathered_result if isinstance(result_or_error, Exception)
        }:
            self.logger.error("Errors occurred while sending nearest coffee shops messages", errors)
