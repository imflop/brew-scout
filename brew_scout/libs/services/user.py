import dataclasses as dc
from collections import abc

from ..dal.user import UserRepository
from ..dal.models.users import UserModel
from ..serializers.telegram import From


@dc.dataclass(frozen=True, slots=True, repr=False)
class UserService:
    repository: UserRepository

    async def get_users(self) -> abc.Sequence[UserModel]:
        return await self.repository.get_all()

    async def store_user(self, user: From) -> None:
        await self.repository.upsert_user(user)
