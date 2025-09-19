from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models import User
    from app.models import EntryAccess


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tittle: Mapped[str] = mapped_column(String(70), nullable=False)
    description: Mapped[str] = mapped_column(String(250))

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    required_access_id: Mapped[int] = mapped_column(ForeignKey('entry_accesses.id'))

    owners: Mapped[List["User"]] = relationship("User", back_populates="posts")
    required_access: Mapped["EntryAccess"] = relationship("EntryAccess", back_populates="posts")
