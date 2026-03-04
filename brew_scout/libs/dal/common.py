import typing as t
from collections import abc

from sqlalchemy.ext.asyncio import AsyncSession

from .models.common import Base


Model = t.TypeVar("Model", bound=Base)


class DatabaseSessionManagerProto(t.Protocol):
    def session(self) -> t.AsyncContextManager[AsyncSession]:
        ...


class BaseRepository(t.Generic[Model]):
    def __init__(self, model: t.Type[Model], session_manager: DatabaseSessionManagerProto):
        self.model = model
        self.session_manager = session_manager

    def _get_session(self) -> t.AsyncContextManager[AsyncSession]:
        return self.session_manager.session()