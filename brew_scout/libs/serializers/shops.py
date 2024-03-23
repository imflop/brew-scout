from pydantic import BaseModel, AnyHttpUrl, Field

from .cities import CityOut


class CoffeeShopOut(BaseModel):
    name: str
    latitude: float
    longitude: float
    web_url: AnyHttpUrl
    distance: float = Field(default=0.0)


class CoffeeShopsOut(CoffeeShopOut):
    id: int
    city: CityOut

    class Config:
        orm_mode = True
