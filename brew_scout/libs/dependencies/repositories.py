from collections import abc
import typing as t

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dal.models.shops import CoffeeShopModel, CityModel
from ..dal.models.common import Base as BaseModel
from ..dal.city import BaseRepository  # type: ignore
from ..dal.city import CityRepository
from ..dal.models.users import UserModel
from ..dal.shop import CoffeeShopRepository
from ..dal.user import UserRepository
from ..dependencies.common import get_db_session


T = t.TypeVar("T", bound=BaseRepository[t.Any])


def get_repository(model: type[BaseModel], repository: t.Callable[..., T]) -> abc.Callable[[AsyncSession], T]:
    def func(session: AsyncSession = Depends(get_db_session)) -> T:
        return repository(model, session)

    return func


def city_repository_factory(
    city_repository: CityRepository = Depends(get_repository(CityModel, CityRepository))
) -> CityRepository:
    return city_repository


def coffee_shop_repository_factory(
    coffee_shop_repository: CoffeeShopRepository = Depends(get_repository(CoffeeShopModel, CoffeeShopRepository))
) -> CoffeeShopRepository:
    return coffee_shop_repository


def user_repository_factory(
    user_repository: UserRepository = Depends(get_repository(UserModel, UserRepository))
) -> UserRepository:
    return user_repository
