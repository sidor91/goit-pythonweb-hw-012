import contextlib

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.utils.env_variables import settings
from sqlalchemy.orm import DeclarativeBase

class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(settings.DATABASE_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session


class Base(DeclarativeBase):
    pass
