import pytest
from jose import jwt

from src.auth.service import (
    create_access_token,
    create_password_reset_token,
    get_email_from_password_token,
)
from src.utils.env_variables import settings


@pytest.mark.asyncio
async def test_create_access_token_contains_role_and_subject():
    token = await create_access_token(
        {"sub": "user1", "role": "user"}, expires_delta=60
    )
    payload = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )

    assert payload["sub"] == "user1"
    assert payload["role"] == "user"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_password_reset_token_roundtrip():
    token = create_password_reset_token(
        {"sub": "reset@example.com"}, expires_seconds=60
    )
    email = await get_email_from_password_token(token)
    assert email == "reset@example.com"
