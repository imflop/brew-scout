import pytest

from brew_scout.libs.dal.shop import CoffeeShopRepository
from brew_scout.libs.dal.models.shops import CoffeeShopModel

from ...factory_boys import CountryFactory, CityFactory, CoffeeShopFactory


@pytest.fixture()
def repository(db_session):
    return CoffeeShopRepository(CoffeeShopModel, db_session)


@pytest.mark.usefixtures("db_session")
async def test_get_all_shops(repository: CoffeeShopRepository):
    coffee_shop = await CoffeeShopFactory.create()
    result = await repository.get_all()

    assert result[0].name == coffee_shop.name


@pytest.mark.usefixtures("db_session")
async def test_get_by_city_name(repository: CoffeeShopRepository):
    city = await CityFactory.create(country=CountryFactory.create())
    coffee_shops = await CoffeeShopFactory.create_batch(2, city=city)
    result = await repository.get_by_city_name(city.name)

    assert len(coffee_shops) == len(result)
