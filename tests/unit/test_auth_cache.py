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

# Ensure project root is on sys.path so `src` package can be imported in tests
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.cache import service as cache_module


@pytest.mark.asyncio
async def test_cache_set_get_delete(monkeypatch):
    # Use fakeredis FakeRedis as the underlying client to avoid external Redis
    try:
        import fakeredis.aioredis as fake_aioredis
    except Exception:
        pytest.skip("fakeredis.aioredis not available")

    fake = fake_aioredis.FakeRedis()
    # Patch the module-level cache instance to use the fake client
    await cache_module.cache_service.connect()
    cache_module.cache_service._client = fake

    username = "alice"
    data = {"id": 1, "username": username, "email": "a@b.com", "avatar": ""}

    await cache_module.cache_service.set_user_by_username(username, data)
    got = await cache_module.cache_service.get_user_by_username(username)
    assert got is not None
    assert got["username"] == username

    await cache_module.cache_service.delete_user_by_username(username)
    got2 = await cache_module.cache_service.get_user_by_username(username)
    assert got2 is None
