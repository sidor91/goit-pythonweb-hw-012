from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar  # type: ignore

from src.users.repository import UserRepository
from src.database.users.schemas import UserCreate
from src.services.cache.service import cache_service


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        user = await self.repository.update_avatar_url(email, url)
        # Invalidate cached user data after avatar update
        try:
            if user and user.username:
                await cache_service.delete_user_by_username(user.username)
                await cache_service.delete_user(user.id)
        except Exception:
            # Do not block the operation on cache failures
            pass
        return user
