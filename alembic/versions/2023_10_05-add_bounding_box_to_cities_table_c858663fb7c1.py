"""add_bounding_box_to_cities_table

Revision ID: c858663fb7c1
Revises: ee0fa0a76198
Create Date: 2023-10-05 20:37:21.325561

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from brew_scout.libs.dal.models.cities import CountryModel, CityModel
from brew_scout.libs.domains.cities import City

# revision identifiers, used by Alembic.
revision = "c858663fb7c1"
down_revision = "ee0fa0a76198"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable the PostGIS extension for the database
    # op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # Create a session to interact with the database
    Session = sessionmaker(bind=op.get_bind())
    session = Session()

    # Create countries
    england = CountryModel(name="England")
    germany = CountryModel(name="Germany")
    cyprus = CountryModel(name="Cyprus")

    # Add countries to the session
    session.add_all([england, germany, cyprus])
    session.commit()

    # Add the new columns for bounding box coordinates
    op.add_column("cities", sa.Column("bounding_box_min_latitude", sa.Float(), nullable=False))
    op.add_column("cities", sa.Column("bounding_box_max_latitude", sa.Float(), nullable=False))
    op.add_column("cities", sa.Column("bounding_box_min_longitude", sa.Float(), nullable=False))
    op.add_column("cities", sa.Column("bounding_box_max_longitude", sa.Float(), nullable=False))

    # Create cities
    london = CityModel(
        name=City.LONDON,
        bounding_box_min_latitude=-0.5103751,
        bounding_box_max_latitude=51.6918741,
        bounding_box_min_longitude=-0.14131817635799537,
        bounding_box_max_longitude=0.3340155,
        country=england,
    )
    berlin = CityModel(
        name=City.BERLIN,
        bounding_box_min_latitude=13.0883450,
        bounding_box_max_latitude=52.6755087,
        bounding_box_min_longitude=13.7611609,
        bounding_box_max_longitude=13.0883450,
        country=germany,
    )
    nicosia = CityModel(
        name=City.NICOSIA,
        bounding_box_min_latitude=32.5670761,
        bounding_box_max_latitude=35.2017784,
        bounding_box_min_longitude=33.5192942,
        bounding_box_max_longitude=32.5670761,
        country=cyprus,
    )

    # Add cities to the session
    session.add_all([london, berlin, nicosia])
    session.commit()

    # Create a spatial index for the bounding box coordinates
    op.create_index(
        "idx_cities_bounding_box",
        "cities",
        ["bounding_box_min_latitude", "bounding_box_max_latitude", "bounding_box_min_longitude", "bounding_box_max_longitude"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_cities_bounding_box", "cities")
    op.drop_column("cities", "bounding_box_min_latitude")
    op.drop_column("cities", "bounding_box_max_latitude")
    op.drop_column("cities", "bounding_box_min_longitude")
    op.drop_column("cities", "bounding_box_max_longitude")
