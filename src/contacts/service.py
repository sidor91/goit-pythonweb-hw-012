from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from src.contacts.repository import ContactRepository
from src.database.contacts.schemas import ContactCreateSchema, ContactUpdateSchema
from src.utils.error_handlers import handle_integrity_error

from src.database.users.model import User

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreateSchema, user: User):
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            message = handle_integrity_error(e)
            raise HTTPException(400, detail=message)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    async def get_contacts(self, skip: int, limit: int, user: User, search: str | None = None):
        try:
            return await self.repository.get_contacts(user, skip, limit, search)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    async def get_contact(self, contact_id: int, user: User):
        try:
            contact = await self.repository.get_contact_by_id(contact_id, user)
            return contact
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    async def update_contact(
        self, contact_id: int, body: ContactUpdateSchema, user: User
    ):
        try:
            contact = await self.repository.update_contact(contact_id, body, user)
            return contact
        except IntegrityError as e:
            message = handle_integrity_error(e)
            raise HTTPException(400, detail=message)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    async def remove_contact(self, contact_id: int, user: User):
        try:
            contact = await self.repository.remove_contact(contact_id, user)
            return contact
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    async def get_upcoming_birthdays(self, user: User):
        try:
            return await self.repository.get_upcoming_birthdays(user)
        except SQLAlchemyError:
            raise HTTPException(500, "Database error")
