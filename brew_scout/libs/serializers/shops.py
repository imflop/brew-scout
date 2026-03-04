from pydantic import AnyHttpUrl

from .cities import CityOut
from .common import CommonOut


class CoffeeShopsOut(CommonOut):
    id: int
    name: str
    latitude: float
    longitude: float
    web_url: AnyHttpUrl
    city: CityOut
