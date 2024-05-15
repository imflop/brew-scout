import pytest

from brew_scout.libs.dal.city import CityRepository
from brew_scout.libs.dal.models.cities import CityModel
from brew_scout.libs.domains.cities import City


@pytest.fixture()
def repository(db_session):
    return CityRepository(CityModel, db_session)


@pytest.mark.parametrize(
    "some_city_latitude, some_city_longitude, expected_city",
    (
        (51.51363862348303, -0.06889059337225804, City.LONDON),
        (52.50737398157598, 13.390585604308393, City.BERLIN),
        (35.15618162842344, 33.36394409277844, City.NICOSIA),
        (34.685225375270704, 33.04887733663054, City.LIMASSOL),
        (41.37866340172198, 2.1813662707408095, City.BARCELONA),
        (41.14925128732046, -8.622305046242658, City.PORTO),
        (38.723427892007145, -9.12490716764528, City.LISBON),
        (25.10321919666715, 55.21584622655509, City.DUBAI),
    ),
)
async def test_get_city_by_place_coordinates(
    repository: CityRepository,
    some_city_latitude: float,
    some_city_longitude: float,
    expected_city: City,
):
    res = await repository.get_city_by_coordinates(latitude=some_city_latitude, longitude=some_city_longitude)

    assert res.name == expected_city
