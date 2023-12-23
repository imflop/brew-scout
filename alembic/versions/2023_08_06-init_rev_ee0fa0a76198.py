"""init_rev

Revision ID: ee0fa0a76198
Revises: 
Create Date: 2023-08-06 13:27:07.522929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ee0fa0a76198"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("timezone('UTC'::text, now())"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("timezone('UTC'::text, now())"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("timezone('UTC'::text, now())"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("timezone('UTC'::text, now())"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"]),
    )

    op.create_table(
        "shops",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("web_url", sa.String(512), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("timezone('UTC'::text, now())"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("timezone('UTC'::text, now())"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"]),
    )


def downgrade() -> None:
    op.drop_table("countries")
    op.drop_table("cities")
    op.drop_table("shops")
