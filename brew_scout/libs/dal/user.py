import datetime as dt
from collections import abc

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from .models.common import BaseRepository
from .models.users import UserModel
from ..serializers.telegram import From


class UserRepository(BaseRepository[UserModel]):
    async def get_all(self) -> abc.Sequence[UserModel]:
        result = await self.session.scalars(select(UserModel))

        return result.all()

    async def upsert_user(self, user: From) -> None:
        ins_stmt = insert(UserModel).values(
            tuid=user.tuid,
            username=user.username,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        ups_stmt = ins_stmt.on_conflict_do_update(
            index_elements=[UserModel.username, UserModel.tuid],
            set_=dict(
                is_bot=ins_stmt.excluded.is_bot,
                first_name=ins_stmt.excluded.first_name,
                last_name=ins_stmt.excluded.last_name,
                created_at=ins_stmt.excluded.created_at,
                updated_at=dt.datetime.now(tz=dt.timezone.utc),
            ),
        )

        await self.session.execute(ups_stmt)
