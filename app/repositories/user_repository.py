from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.service.jwt_service import get_password_hash
from app.models import User
from app.schemas.user import UserCreate


async def get_users(session: AsyncSession) -> list[User]:
    try:
        stmt = select(User).where(User.is_active).order_by(User.id)
        result: Result = await session.execute(stmt)
        return list(result.scalars().all())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    try:
        return await session.get(User, user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {user_id} not found. More detailed {str(e)}")


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    try:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            password=hashed_password,
            role=user_in.role,
            is_active=user_in.is_active,
            access_id=user_in.access_id,
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    try:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


async def delete_user(session: AsyncSession, user: User) -> None:
    try:
        await session.delete(user)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def soft_delete_user(session: AsyncSession, user: User) -> User:
    try:
        user.is_active = False
        await session.commit()
        await session.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при мягком удалении пользователя: {str(e)}"
        )
