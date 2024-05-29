import datetime as dt
from random import randint

import factory as f
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from brew_scout.libs.dal.models.shops import CoffeeShopModel, CountryModel, CityModel
from brew_scout.libs.dal.models.users import UserModel

from .conftest import AsyncScopedSession


def generate_id(obj, create, value):
    if hasattr(obj, "id") and obj.id is None:
        obj.id = value or randint(1, 1000000)


class BaseFactory(AsyncSQLAlchemyFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = AsyncScopedSession
        strategy = f.BUILD_STRATEGY

    id = f.PostGeneration(generate_id)


class CountryFactory(BaseFactory):
    class Meta:
        model = CountryModel

    name = f.Faker("pystr")


class CityFactory(BaseFactory):
    class Meta:
        model = CityModel

    name = f.Faker("pystr")
    country_id = f.Faker("pyint")

    country = f.SubFactory(CountryFactory)


class CoffeeShopFactory(BaseFactory):
    class Meta:
        model = CoffeeShopModel

    name = f.Faker("pystr")
    web_url = f.Faker("url")
    city_id = f.Faker("pyint")
    latitude = f.Faker("pyfloat", min_value=-85.05112878, max_value=85.05112878)
    longitude = f.Faker("pyfloat", min_value=-180, max_value=180)
    created_at = f.LazyFunction(lambda: dt.datetime.now(tz=dt.UTC))
    updated_at = f.LazyFunction(lambda: dt.datetime.now(tz=dt.UTC))

    city = f.SubFactory(CityFactory)


class UserFactory(BaseFactory):
    class Meta:
        model = UserModel

    id = f.Faker("uuid4")
    tuid = f.Faker("pyint")
    first_name = f.Faker("first_name")
    last_name = f.Faker("last_name")
    username = f.Faker("user_name")
    created_at = f.LazyFunction(lambda: dt.datetime.now(tz=dt.timezone.utc))
    updated_at = f.LazyFunction(lambda: dt.datetime.now(tz=dt.timezone.utc))
