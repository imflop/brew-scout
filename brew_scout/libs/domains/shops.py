from pydantic import BaseModel, AnyHttpUrl

from ..utils.orj import orjson_dumps


class CommonModel(BaseModel):
    class Config:
        json_dumps = orjson_dumps


class CoffeeShop(CommonModel):
    name: str
    latitude: float
    longitude: float
    web_url: AnyHttpUrl
    distance: float | None
