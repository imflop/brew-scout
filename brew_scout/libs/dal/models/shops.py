import datetime as dt

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import Base


class CountryModel(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow, nullable=True
    )

    cities: Mapped[list["CityModel"]] = relationship(back_populates="country")

    def __repr__(self) -> str:
        return f"{self.name}: {self.id}"


class CityModel(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    name: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow, nullable=True
    )
    bounding_box_min_latitude: Mapped[float]
    bounding_box_max_latitude: Mapped[float]
    bounding_box_min_longitude: Mapped[float]
    bounding_box_max_longitude: Mapped[float]

    country: Mapped[CountryModel] = relationship(back_populates="cities")
    shops: Mapped[list["CoffeeShopModel"]] = relationship(back_populates="city")

    def __repr__(self) -> str:
        return f"{self.name}: {self.id}"


class CoffeeShopModel(Base):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    name: Mapped[str]
    web_url: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow, nullable=True
    )

    city: Mapped[CityModel] = relationship(back_populates="shops")
