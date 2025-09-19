import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models import User
    from app.models import Post


class AccessRoleEnum(str, enum.Enum):
    premium_role = "Премиум"
    vip_role = "ВИП"
    default_role = "Стандартный"


class EntryAccess(Base):
    __tablename__ = "entry_accesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    access_tittle: Mapped[AccessRoleEnum] = mapped_column(Enum(AccessRoleEnum), nullable=False)
    description: Mapped[str] = mapped_column(String(250))

    users: Mapped[List["User"]] = relationship("User", back_populates="access")
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="required_access")
