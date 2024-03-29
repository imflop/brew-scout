import pytest

from brew_scout.libs.dal.city import CityRepository
from brew_scout.libs.dal.models.cities import CityModel
from brew_scout.libs.domains.cities import City


@pytest.fixture()
def repository(db_session):
    return CityRepository(CityModel, db_session)


async def test_get_all_shops(repository: CityRepository):
    res = await repository.get_city_by_coordinates(51.50183925568836, -0.14131817635799537)

    assert res.name == City.LONDON
