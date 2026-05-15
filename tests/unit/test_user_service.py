import pytest

from src.database.users.schemas import UserCreate
from src.users.service import UserService


class DummyGravatar:
    def __init__(self, email: str):
        self.email = email

    def get_image(self):
        return "https://example.com/avatar.png"


@pytest.mark.asyncio
async def test_user_service_create_user_uses_gravatar(db_session, monkeypatch):
    monkeypatch.setattr("src.users.service.Gravatar", DummyGravatar)
    service = UserService(db_session)

    user = await service.create_user(
        UserCreate(username="charlie", email="charlie@example.com", password="pass")
    )

    assert user.avatar == "https://example.com/avatar.png"
    assert user.username == "charlie"


@pytest.mark.asyncio
async def test_user_service_invalidate_cache_on_password_update(
    db_session, monkeypatch
):
    called = {"deleted_by_username": False, "deleted_by_id": False}

    async def fake_delete_user_by_username(username: str):
        called["deleted_by_username"] = True

    async def fake_delete_user(user_id: int):
        called["deleted_by_id"] = True

    monkeypatch.setattr(
        "src.users.service.cache_service.delete_user_by_username",
        fake_delete_user_by_username,
    )
    monkeypatch.setattr("src.users.service.cache_service.delete_user", fake_delete_user)

    service = UserService(db_session)
    user = await service.create_user(
        UserCreate(username="dave", email="dave@example.com", password="pass")
    )

    updated = await service.update_password(user.email, "newhash")

    assert updated is not None
    assert updated.hashed_password == "newhash"
    assert called["deleted_by_username"] is True
    assert called["deleted_by_id"] is True
