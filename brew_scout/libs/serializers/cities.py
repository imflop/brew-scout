from .common import CommonOut


class CountryOut(CommonOut):
    id: int
    name: str


class CityOut(CommonOut):
    id: int
    name: str
    country: CountryOut
