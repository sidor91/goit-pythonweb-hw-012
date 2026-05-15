import pytest

from src.auth.controller import send_email, send_password_reset_email
from src.auth.service import create_email_token


async def fake_send_email(*args, **kwargs):
    return None


async def fake_send_password_reset_email(*args, **kwargs):
    return None


@pytest.mark.asyncio
async def test_register_login_and_me_route(client, monkeypatch):
    monkeypatch.setattr("src.auth.controller.send_email", fake_send_email)

    register_payload = {
        "username": "eve",
        "email": "eve@example.com",
        "password": "strongpassword",
    }
    response = await client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "eve"
    assert data["email"] == "eve@example.com"
    assert data["role"] == "user"

    token = create_email_token({"sub": "eve@example.com"})
    confirm_response = await client.get(f"/api/auth/confirmed_email/{token}")
    assert confirm_response.status_code == 200

    login_response = await client.post(
        "/api/auth/login",
        data={"username": "eve", "password": "strongpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "eve@example.com"


@pytest.mark.asyncio
async def test_full_contact_crud_flow(client, monkeypatch):
    monkeypatch.setattr("src.auth.controller.send_email", fake_send_email)
    monkeypatch.setattr(
        "src.auth.controller.send_password_reset_email", fake_send_password_reset_email
    )

    register_payload = {
        "username": "frank",
        "email": "frank@example.com",
        "password": "sec123",
    }
    response = await client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201

    token = create_email_token({"sub": "frank@example.com"})
    confirm_response = await client.get(f"/api/auth/confirmed_email/{token}")
    assert confirm_response.status_code == 200

    login_response = await client.post(
        "/api/auth/login",
        data={"username": "frank", "password": "sec123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    contact_payload = {
        "first_name": "Olena",
        "phone": "+380501112233",
        "email": "olena@example.com",
        "second_name": "Ivanova",
        "birthday": "2000-01-01",
        "additional_info": "Works at test",
    }
    create_response = await client.post(
        "/api/contacts/", json=contact_payload, headers=auth_headers
    )
    assert create_response.status_code == 201
    contact_data = create_response.json()
    assert contact_data["first_name"] == "Olena"

    list_response = await client.get("/api/contacts/", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(item["id"] == contact_data["id"] for item in list_response.json())

    get_response = await client.get(
        f"/api/contacts/{contact_data['id']}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["phone"] == "+380501112233"

    update_payload = {"first_name": "Olena", "phone": "+380501112233"}
    update_response = await client.put(
        f"/api/contacts/{contact_data['id']}",
        json=update_payload,
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "Olena"

    delete_response = await client.delete(
        f"/api/contacts/{contact_data['id']}", headers=auth_headers
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == contact_data["id"]

    not_found_response = await client.get(
        f"/api/contacts/{contact_data['id']}", headers=auth_headers
    )
    assert not_found_response.status_code == 404


@pytest.mark.asyncio
async def test_healthchecker_endpoint(client):
    response = await client.get("/api/healthchecker")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to FastAPI!"


@pytest.mark.asyncio
async def test_password_reset_flow(client, monkeypatch):
    monkeypatch.setattr("src.auth.controller.send_email", fake_send_email)
    monkeypatch.setattr(
        "src.auth.controller.send_password_reset_email", fake_send_password_reset_email
    )

    register_payload = {
        "username": "grace",
        "email": "grace@example.com",
        "password": "mypassword",
    }
    response = await client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201

    token = create_email_token({"sub": "grace@example.com"})
    confirm_response = await client.get(f"/api/auth/confirmed_email/{token}")
    assert confirm_response.status_code == 200

    token_store = {}

    async def fake_set_key(key, value, ex=None):
        token_store[key] = value

    async def fake_get_key(key):
        return token_store.get(key)

    async def fake_delete_key(key):
        token_store.pop(key, None)

    monkeypatch.setattr("src.auth.controller.cache_service.set_key", fake_set_key)
    monkeypatch.setattr("src.auth.controller.cache_service.get_key", fake_get_key)
    monkeypatch.setattr("src.auth.controller.cache_service.delete_key", fake_delete_key)

    reset_request = await client.post(
        "/api/auth/request_password_reset",
        json={"email": "grace@example.com"},
    )
    assert reset_request.status_code == 200

    token_key = next(iter(token_store))
    token = token_key.replace("pwdreset:", "")
    reset_response = await client.post(
        f"/api/auth/reset_password?token={token}",
        data={"new_password": "newsecret"},
    )
    assert reset_response.status_code == 200

    login_response = await client.post(
        "/api/auth/login",
        data={"username": "grace", "password": "newsecret"},
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_upcoming_birthdays_route(client, monkeypatch):
    monkeypatch.setattr("src.auth.controller.send_email", fake_send_email)

    registration = {
        "username": "hanna",
        "email": "hanna@example.com",
        "password": "safe123",
    }
    response = await client.post("/api/auth/register", json=registration)
    assert response.status_code == 201

    token = create_email_token({"sub": "hanna@example.com"})
    confirm_response = await client.get(f"/api/auth/confirmed_email/{token}")
    assert confirm_response.status_code == 200

    login_response = await client.post(
        "/api/auth/login",
        data={"username": "hanna", "password": "safe123"},
    )
    assert login_response.status_code == 200
    auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    birthday_contact = {
        "first_name": "Maksym",
        "phone": "+380501113344",
        "birthday": "2001-01-04",
    }
    await client.post("/api/contacts/", json=birthday_contact, headers=auth_headers)

    upcoming = await client.get(
        "/api/contacts/birthdays/upcoming", headers=auth_headers
    )
    assert upcoming.status_code == 200
    assert isinstance(upcoming.json(), list)
