import pytest

from src.database.users.schemas import UserCreate
from src.users.repository import UserRepository


@pytest.mark.asyncio
async def test_user_repository_create_and_find(db_session):
    repository = UserRepository(db_session)
    user_data = UserCreate(
        username="alice",
        email="alice@example.com",
        password="hashedpassword",
    )

    user = await repository.create_user(user_data)
    assert user.id is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.role == "user"

    found_by_username = await repository.get_user_by_username("alice")
    assert found_by_username is not None
    assert found_by_username.id == user.id

    found_by_email = await repository.get_user_by_email("alice@example.com")
    assert found_by_email is not None
    assert found_by_email.id == user.id

    found_by_id = await repository.get_user_by_id(user.id)
    assert found_by_id is not None
    assert found_by_id.username == "alice"


@pytest.mark.asyncio
async def test_user_repository_updates(db_session):
    repository = UserRepository(db_session)
    user_data = UserCreate(
        username="bob",
        email="bob@example.com",
        password="secret",
    )

    user = await repository.create_user(user_data)
    await repository.confirmed_email(user.email)
    reloaded = await repository.get_user_by_email(user.email)
    assert reloaded is not None
    assert reloaded.confirmed is True

    updated = await repository.update_avatar_url(
        user.email, "http://avatar.test/avatar.png"
    )
    assert updated.avatar == "http://avatar.test/avatar.png"

    hashed_password = "newhashed"
    updated_password = await repository.update_password(user.email, hashed_password)
    assert updated_password.hashed_password == hashed_password
