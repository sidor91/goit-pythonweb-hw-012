from typing import Sequence
from datetime import date, timedelta

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.contacts.model import Contact as ContactModel
from src.database.contacts.schemas import ContactCreateSchema, ContactUpdateSchema
from src.utils.next_birthday import get_next_birthday

from src.database.users.model import User


class ContactRepository:
    """Repository for CRUD operations on contact records."""

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        user: User,
        skip: int,
        limit: int,
        search: str | None = None,
    ) -> Sequence[ContactModel]:
        """Return a paginated list of contacts for the given user."""
        stmt = select(ContactModel)

        if search:
            stmt = stmt.where(
                or_(
                    ContactModel.first_name.ilike(f"%{search}%"),
                    ContactModel.second_name.ilike(f"%{search}%"),
                    ContactModel.email.ilike(f"%{search}%"),
                )
            )

        stmt = stmt.filter_by(user_id=user.id).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(
        self, contact_id: int, user: User
    ) -> ContactModel | None:
        """Return a single contact by ID for the authenticated user."""
        stmt = select(ContactModel).filter_by(id=contact_id, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(
        self, body: ContactCreateSchema, user: User
    ) -> ContactModel:
        """Create a new contact belonging to the provided user."""
        contact = ContactModel(**body.model_dump(), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdateSchema, user: User
    ) -> ContactModel | None:
        """Update an existing contact and return the modified record."""
        contact = await self.get_contact_by_id(contact_id, user)

        if not contact:
            return None

        update_data = body.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        await self.db.commit()
        await self.db.refresh(contact)

        return contact

    async def remove_contact(self, contact_id: int, user: User) -> ContactModel | None:
        """Delete a contact record if it belongs to the authenticated user."""
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_contacts_by_ids(
        self, contact_ids: list[int], user: User
    ) -> Sequence[ContactModel]:
        """Return a list of contacts filtered by a list of IDs for a user."""
        stmt = (
            select(ContactModel)
            .where(ContactModel.id.in_(contact_ids))
            .filter_by(user=user)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    from datetime import date, timedelta

    async def get_upcoming_birthdays(self, user: User):
        today = date.today()
        end_date = today + timedelta(days=7)

        stmt = select(ContactModel).filter_by(user=user)
        result = await self.db.execute(stmt)
        contacts = result.scalars().all()

        upcoming: list[ContactModel] = []

        for c in contacts:
            if not c.birthday:
                continue

            next_birthday = get_next_birthday(c.birthday, today)

            if today <= next_birthday <= end_date:
                upcoming.append(c)

        return upcoming
