from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import RoleEnum


class UserBase(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    role: RoleEnum | None = None
    is_active: bool | None = None
    access_id: int | None = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str | None = None
    is_active: bool | None = None
    access_id: int | None = None


class UserUpdatePartial(UserBase):
    username: str | None = None
    email: EmailStr | None = None
    role: RoleEnum | None = None
    is_active: bool | None = None
    access_id: int | None = None
    password: str | None = None


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
