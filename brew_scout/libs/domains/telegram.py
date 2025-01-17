from enum import StrEnum


class TelegramMethods(StrEnum):
    SEND_MESSAGE = "sendMessage"
    SEND_VENUE = "sendVenue"


class TelegramMessage(StrEnum):
    COMMAND_PREFIX = "/"
    START = "/start"
