import pytest

from brew_scout.libs.services.kv import KVService

from ...factory_boys import CoffeeShopFactory, CityFactory


@pytest.fixture()
def service(rds_session):
    return KVService(rds_session)


async def test_get_coffee_shops_key_not_exist(service: KVService, faker):
    assert await service.get_coffee_shops(faker.pystr()) == []


async def test_get_coffee_shops_key_exist(service: KVService):
    city = CityFactory.build(name="doge")
    shops = CoffeeShopFactory.build_batch(3, city=city)

    await service.set_coffee_shops(city.name, shops)

    assert {shop.name for shop in shops} == {r.name for r in await service.get_coffee_shops(city.name)}


async def test_get_nearest_coffee_shops_if_key_not_exist(service: KVService, faker):
    assert await service.get_nearest_coffee_shops(
        city_name=faker.pystr(),
        source_latitude=faker.pyfloat(min_value=-85.05112878, max_value=85.05112878),
        source_longitude=faker.pyfloat(min_value=-180, max_value=180)
    ) == []


async def test_get_nearest_coffee_shops(service: KVService):
    city = CityFactory.build(name="dogenyc")

    shop1 = CoffeeShopFactory.build(name="Birch", latitude=40.7433827899312, longitude=-73.98009804904653, city=city)
    shop2 = CoffeeShopFactory.build(name="Paper", latitude=40.74619137684745, longitude=-73.98947395732176, city=city)
    shop3 = CoffeeShopFactory.build(name="Peets", latitude=40.73467545954848, longitude=-73.99098086853408, city=city)
    source_latitude, source_longitude = 40.74143875192839, -73.98897869240372

    await service.set_coffee_shops(city.name, [shop1, shop2, shop3])
    result = await service.get_nearest_coffee_shops(city.name, source_latitude, source_longitude)

    assert shop2.name == result[0].name
