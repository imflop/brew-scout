import typing as t
import orjson
from enum import StrEnum

from pydantic import BaseModel, Field


def orjson_dumps(v: t.Any, *, default: t.Any) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class TelegramMethods(StrEnum):
    SEND_MESSAGE = "sendMessage"
    SEND_VENUE = "sendVenue"


class TelegramMessage(StrEnum):
    START = "/start"


class TelegramBaseModel(BaseModel):
    class Config:
        json_dumps = orjson_dumps


class Button(TelegramBaseModel):
    text: str


class ReplyKeyboardButton(Button):
    request_location: bool = Field(default=False)


class ReplyKeyboard(TelegramBaseModel):
    keyboard: list[list[ReplyKeyboardButton]]
    one_time_keyboard: bool = Field(default=True)
    resize_keyboard: bool = Field(default=True)


class InlineKeyboardButton(Button):
    url: str


class InlineKeyboard(TelegramBaseModel):
    inline_keyboard: list[list[InlineKeyboardButton]]
