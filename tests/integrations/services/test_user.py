import pytest

from brew_scout.libs.services.user import UserService
from brew_scout.libs.dal.user import UserRepository
from brew_scout.libs.dal.models.users import UserModel
from brew_scout.libs.serializers.telegram import From

from ...factory_boys import UserFactory


@pytest.fixture()
def user_service(db_session):
    return UserService(
        repository=UserRepository(UserModel, db_session)
    )


@pytest.fixture()
def parsed_user_payload(faker):
    first_name, last_name, username = faker.first_name(), faker.last_name(), faker.user_name()
    raw_user = {
        "id": faker.pyint(),
        "is_bot": "false",
        "first_name": f"{first_name}",
        "last_name": f"{last_name}",
        "username": f"{username}",
        "language_code": "en",
    }

    return From(**raw_user)


async def test_store_user(user_service, parsed_user_payload):
    assert await user_service.get_users() == []

    await user_service.store_user(parsed_user_payload)
    users = await user_service.get_users()

    assert users != []
    assert users[0].first_name == parsed_user_payload.first_name
    assert users[0].last_name == parsed_user_payload.last_name
    assert users[0].username == parsed_user_payload.username
    assert users[0].tuid == parsed_user_payload.tuid


async def test_store_user_if_exist(user_service, faker):
    user = await UserFactory.create()
    user_payload = From(
        **{
            "id": user.tuid,
            "is_bot": "false",
            "first_name": f"{user.first_name}",
            "last_name": f"{user.last_name}",
            "username": f"{user.username}",
            "language_code": "en",
        }
    )
    await user_service.store_user(user_payload)

    users = await user_service.get_users()
    assert len(users) == len([user])
    assert str(users[0].id) == user.id


async def test_store_user_if_exist_do_update(user_service):
    user = await UserFactory.create()
    user_payload = From(**{
        "id": user.tuid,
        "is_bot": "false",
        "first_name": "UpdatedName",
        "last_name": "UpdatedLastName",
        "username": f"{user.username}",
        "language_code": "en",
    })

    await user_service.store_user(user_payload)

    users = await user_service.get_users()
    assert str(users[0].id) == user.id
    assert users[0].first_name == user_payload.first_name
    assert users[0].last_name == user_payload.last_name
