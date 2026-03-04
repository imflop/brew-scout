from pydantic import BaseModel, Field

from ..utils.orj import orjson_dumps


class CommonModel(BaseModel):
    ...


class Location(CommonModel):
    latitude: float
    longitude: float


class Chat(CommonModel):
    id: int
    first_name: str | None
    last_name: str | None
    username: str
    type: str


class From(CommonModel):
    tuid: int = Field(alias="id")
    is_bot: bool
    first_name: str | None
    last_name: str | None
    username: str
    language_code: str


class Message(CommonModel):
    message_id: int
    message_from: From = Field(alias="from")
    chat: Chat
    date: int
    text: str | None
    location: Location | None = Field(default=None)


class TelegramHookIn(CommonModel):
    update_id: int
    message: Message


class Button(CommonModel):
    text: str


class ReplyKeyboardButton(Button):
    request_location: bool = Field(default=False)


class InlineKeyboardButton(Button):
    url: str


class ReplyKeyboardOut(CommonModel):
    keyboard: list[list[ReplyKeyboardButton]]
    one_time_keyboard: bool = Field(default=True)
    resize_keyboard: bool = Field(default=True)


class InlineKeyboardOut(CommonModel):
    inline_keyboard: list[list[InlineKeyboardButton]]
