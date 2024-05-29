import datetime as dt
from uuid import UUID

from sqlalchemy import DateTime, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from .common import Base


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", "tuid"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    tuid: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str]
    last_name: Mapped[str]
    is_bot: Mapped[bool] = mapped_column(unique=False, nullable=False, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow, nullable=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow, nullable=True
    )
