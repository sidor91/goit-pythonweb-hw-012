import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from src.contacts.service import ContactService
from src.users.repository import UserRepository
from src.database.users.schemas import UserCreate
from src.database.contacts.schemas import ContactCreateSchema, ContactUpdateSchema


@pytest.mark.asyncio
async def test_contact_service_create_and_duplicate_phone(db_session):
    user = await UserRepository(db_session).create_user(
        UserCreate(username="owner2", email="owner2@example.com", password="hash")
    )
    service = ContactService(db_session)

    contact_payload = ContactCreateSchema(
        first_name="Lena",
        phone="+380501234000",
        email="lena@example.com",
    )
    contact = await service.create_contact(contact_payload, user)
    assert contact.first_name == "Lena"

    with pytest.raises(HTTPException) as exc_info:
        await service.create_contact(contact_payload, user)

    assert exc_info.value.status_code == 400
    assert str(exc_info.value.detail) in (
        "Integrity error",
        "Phone already exists",
        "Email already exists",
    )


@pytest.mark.asyncio
async def test_contact_service_update_and_delete(db_session):
    user = await UserRepository(db_session).create_user(
        UserCreate(username="owner3", email="owner3@example.com", password="hash")
    )
    service = ContactService(db_session)
    contact = await service.create_contact(
        ContactCreateSchema(
            first_name="Oksana",
            phone="+380501234001",
            email="oksana@example.com",
        ),
        user,
    )

    updated = await service.update_contact(
        contact.id,
        ContactUpdateSchema(
            first_name="Oksana",
            phone="+380501234001",
            email="oksana@example.com",
        ),
        user,
    )
    assert updated is not None
    assert updated.id == contact.id

    deleted = await service.remove_contact(contact.id, user)
    assert deleted is not None
    assert deleted.id == contact.id
