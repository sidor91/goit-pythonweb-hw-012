from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.users.model import User
from src.database.users.schemas import UserCreate


class UserRepository:
    """Repository for database access and persistence of user records."""

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Return a user by primary key or None if not found."""
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Return a user matching the given username."""
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Return a user matching the given email address."""
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str | None = None) -> User:
        """Create and persist a new user record with hashed password and avatar."""
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """Mark a user's email as confirmed in the database."""
        user = await self.get_user_by_email(email)
        if user:
            user.confirmed = True
            await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """Update the stored avatar URL for a given user email."""
        user = await self.get_user_by_email(email)
        user.avatar = url  # type: ignore
        await self.db.commit()
        await self.db.refresh(user)
        return user  # type: ignore

    async def update_password(self, email: str, hashed_password: str) -> User:
        """Update user's hashed password and return updated user."""
        user = await self.get_user_by_email(email)
        if user:
            user.hashed_password = hashed_password  # type: ignore
            await self.db.commit()
            await self.db.refresh(user)
        return user  # type: ignore
