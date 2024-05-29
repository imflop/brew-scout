import typing as t
import uuid
from collections import abc

from sqlalchemy import select, BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    ...


Model = t.TypeVar("Model", bound=Base)
ModelIdFilter: t.TypeAlias = int | uuid.UUID


class BaseRepository(t.Generic[Model]):
    def __init__(self, model: t.Type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id_filter: ModelIdFilter) -> Model | None:
        return await self.session.get(self.model, id_filter)

    async def filter(self, *expressions: BinaryExpression[t.Any]) -> abc.Sequence[Model]:
        q = select(self.model)

        if expressions:
            q = q.where(*expressions)

        return list(await self.session.scalars(q))
