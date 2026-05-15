import pytest
from datetime import date, timedelta

from src.contacts.repository import ContactRepository
from src.users.repository import UserRepository
from src.database.users.schemas import UserCreate
from src.database.contacts.schemas import ContactCreateSchema, ContactUpdateSchema


@pytest.mark.asyncio
async def test_contact_repository_crud_operations(db_session):
    user_repository = UserRepository(db_session)
    user = await user_repository.create_user(
        UserCreate(username="owner", email="owner@example.com", password="hash")
    )

    repository = ContactRepository(db_session)
    contact = await repository.create_contact(
        ContactCreateSchema(
            first_name="Ivan",
            phone="+380501234567",
            email="ivan@example.com",
            second_name="Petrov",
            birthday=date.today() - timedelta(days=365),
            additional_info="test",
        ),
        user,
    )

    assert contact.id is not None
    assert contact.first_name == "Ivan"
    assert contact.user_id == user.id

    found = await repository.get_contact_by_id(contact.id, user)
    assert found is not None
    assert found.phone == "+380501234567"

    search_results = await repository.get_contacts(user, 0, 10, search="Ivan")
    assert any(contact.id == item.id for item in search_results)

    updated = await repository.update_contact(
        contact.id,
        ContactUpdateSchema(first_name="Ivanov", phone="+380501234567"),
        user,
    )
    assert updated is not None
    assert updated.first_name == "Ivanov"

    upcoming = await repository.get_upcoming_birthdays(user)
    assert isinstance(upcoming, list)

    deleted = await repository.remove_contact(contact.id, user)
    assert deleted is not None
    assert deleted.id == contact.id
    assert await repository.get_contact_by_id(contact.id, user) is None
