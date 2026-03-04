from pydantic import BaseModel, ConfigDict


class CommonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
