from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import Base
from .shops import CoffeeShopModel


class CountryModel(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )

    cities: Mapped[list["CityModel"]] = relationship(back_populates="country")


class CityModel(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )
    bounding_box_min_latitude: Mapped[float]
    bounding_box_max_latitude: Mapped[float]
    bounding_box_min_longitude: Mapped[float]
    bounding_box_max_longitude: Mapped[float]

    country: Mapped["CountryModel"] = relationship(back_populates="cities")
    shops: Mapped[list["CoffeeShopModel"]] = relationship(back_populates="city")
