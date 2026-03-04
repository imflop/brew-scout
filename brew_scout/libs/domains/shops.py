from pydantic import BaseModel, AnyHttpUrl, ConfigDict, Field

class CoffeeShop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    latitude: float
    longitude: float
    web_url: AnyHttpUrl
    distance: float | None = Field(default=None)
