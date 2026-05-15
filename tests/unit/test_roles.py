import os
import pytest

# Set minimal environment variables required by `src.utils.env_variables.Settings`
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "testsecret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_SECONDS", "3600")
os.environ.setdefault("MAIL_USERNAME", "test@example.com")
os.environ.setdefault("MAIL_PASSWORD", "password")
os.environ.setdefault("MAIL_FROM", "noreply@example.com")
os.environ.setdefault("MAIL_PORT", "1025")
os.environ.setdefault("MAIL_SERVER", "localhost")
os.environ.setdefault("MAIL_FROM_NAME", "TestApp")
os.environ.setdefault("CLOUDINARY_NAME", "test")
os.environ.setdefault("CLOUDINARY_API_KEY", "1")
os.environ.setdefault("CLOUDINARY_API_SECRET", "secret")

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import HTTPException
from src.auth.service import require_role
from src.database.users.schemas import User as UserSchema


@pytest.mark.asyncio
async def test_require_role_admin_allows_admin():
    admin = UserSchema(
        id=1, username="admin", email="admin@example.com", avatar="", role="admin"
    )
    checker = require_role("admin")
    returned = await checker(user=admin)

    assert returned == admin


@pytest.mark.asyncio
async def test_require_role_raises_for_non_admin():
    user = UserSchema(
        id=2, username="user", email="user@example.com", avatar="", role="user"
    )
    checker = require_role("admin")

    with pytest.raises(HTTPException) as exc_info:
        await checker(user=user)

    assert exc_info.value.status_code == 403
    assert "Insufficient privileges" in str(exc_info.value.detail)
