from pydantic import BaseModel, AnyHttpUrl

from .cities import CityOut


class CoffeeShopsOut(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    web_url: AnyHttpUrl
    city: CityOut

    class Config:
        orm_mode = True
