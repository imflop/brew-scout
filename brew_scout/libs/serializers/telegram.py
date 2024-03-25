from pydantic import BaseModel, Field

from ..utils.orj import orjson_dumps


class CommonModel(BaseModel):
    class Config:
        json_dumps = orjson_dumps


class From(CommonModel):
    id: int
    username: str
    is_bot: bool
    language_code: str
    first_name: str | None
    last_name: str | None


class Chat(CommonModel):
    id: int
    username: str
    type: str
    first_name: str | None
    last_name: str | None


class Location(CommonModel):
    latitude: float
    longitude: float


class Message(CommonModel):
    message_id: int
    message_from: From
    chat: Chat
    date: int
    text: str | None
    location: Location | None

    class Config:
        fields = {"message_from": "from"}


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
