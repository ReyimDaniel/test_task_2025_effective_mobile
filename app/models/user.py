import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Enum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models import Post
    from app.models import EntryAccess


class RoleEnum(str, enum.Enum):
    admin = "Администратор"
    base_user = "Пользователь"
    moderator = "Модератор"
    premium_user = "ВИП"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    access_id: Mapped[int] = mapped_column(ForeignKey('entry_accesses.id'))

    access: Mapped["EntryAccess"] = relationship("EntryAccess", back_populates="users")
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="owners")
