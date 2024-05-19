"""add_and_update_bounding_boxes

Revision ID: 9ec756593897
Revises: c858663fb7c1
Create Date: 2024-04-22 18:34:01.076376

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

from brew_scout.libs.dal.models.shops import CountryModel, CityModel
from brew_scout.libs.domains.cities import City

# revision identifiers, used by Alembic.
revision = '9ec756593897'
down_revision = 'c858663fb7c1'
branch_labels = None
depends_on = None


def _get_bounding_box_for_city(city: City):
    data = {
        City.LONDON: {
            "bounding_box_min_latitude": 51.3307670297,
            "bounding_box_min_longitude": -0.4972101459,
            "bounding_box_max_latitude": 51.6918729074,
            "bounding_box_max_longitude": 0.2944295731,
        },
        City.BERLIN: {
            "bounding_box_min_latitude": 52.37494747,
            "bounding_box_min_longitude": 13.1082092598,
            "bounding_box_max_latitude": 52.6624102143,
            "bounding_box_max_longitude": 13.761160858,
        },
        City.NICOSIA: {
            "bounding_box_min_latitude": 35.09721013205341,
            "bounding_box_min_longitude": 33.25530209445766,
            "bounding_box_max_latitude": 35.19370373335157,
            "bounding_box_max_longitude": 33.40508576929706,
        }
    }

    return data[city]


def upgrade() -> None:
    session = Session(bind=op.get_bind())

    cy_country_id = None

    # Update existing bounding boxes
    for city in [City.LONDON, City.BERLIN, City.NICOSIA]:
        result = session.query(CityModel).filter(CityModel.name == city).first()
        bbox_coordinates = _get_bounding_box_for_city(city)
        result.bounding_box_min_latitude = bbox_coordinates["bounding_box_min_latitude"]
        result.bounding_box_min_longitude = bbox_coordinates["bounding_box_min_longitude"]
        result.bounding_box_max_latitude = bbox_coordinates["bounding_box_max_latitude"]
        result.bounding_box_max_longitude = bbox_coordinates["bounding_box_max_longitude"]

        if city == City.NICOSIA:
            cy_country_id = result.country_id

    session.commit()

    # Add new countries
    spain = CountryModel(name="Spain")
    portugal = CountryModel(name="Portugal")
    uae = CountryModel(name="United Arab Emirates")

    session.add_all([spain, portugal, uae])
    session.flush()

    # Create new cities
    new_cities = [
        CityModel(
            name=City.BARCELONA,
            bounding_box_min_latitude=41.2650563938,
            bounding_box_min_longitude=2.0216253997,
            bounding_box_max_latitude=41.4575362888,
            bounding_box_max_longitude=2.4115217113,
            country_id=spain.id
        ),
        CityModel(
            name=City.PORTO,
            bounding_box_min_latitude=41.1225622251,
            bounding_box_min_longitude=-8.7191197385,
            bounding_box_max_latitude=41.2223604744,
            bounding_box_max_longitude=-8.5691671283,
            country_id=portugal.id
        ),
        CityModel(
            name=City.LISBON,
            bounding_box_min_latitude=38.6913996234,
            bounding_box_min_longitude=-9.2298356071,
            bounding_box_max_latitude=38.7967543948,
            bounding_box_max_longitude=-9.0863330662,
            country_id=portugal.id
        ),
        CityModel(
            name=City.DUBAI,
            bounding_box_min_latitude=24.6230663993,
            bounding_box_min_longitude=54.8892109282,
            bounding_box_max_latitude=25.5250677653,
            bounding_box_max_longitude=56.011189688,
            country_id=uae.id,
        )
    ]

    if cy_country_id:
        new_cities.append(CityModel(
            name=City.LIMASSOL,
            bounding_box_min_latitude=34.6437391774,
            bounding_box_min_longitude=32.9859757796,
            bounding_box_max_latitude=34.732663974,
            bounding_box_max_longitude=33.1477228738,
            country_id=cy_country_id,
        ))

    session.add_all(new_cities)
    session.commit()


def downgrade() -> None:
    pass
