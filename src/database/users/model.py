from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Index, func, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.database.config import Base

if TYPE_CHECKING:
    from src.database.contacts.model import Contact


class User(Base):
    __tablename__ = "users"

    __table_args__ = (Index("ix_users_username", "username"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)