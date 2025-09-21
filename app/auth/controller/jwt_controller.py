from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.model import Token
from app.auth.service.jwt_service import get_password_hash, verify_password, create_access_token
from app.core.db_helper import db_helper
from app.models import User
from app.schemas.user import UserCreate

router = APIRouter(tags=["JWT Auth"])


@router.post("/reg")
async def register(user: UserCreate, session: AsyncSession = Depends(db_helper.get_scoped_session)):
    result = await session.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
        role=user.role,
        is_active=user.is_active,
        access_id=user.access_id
    )
    session.add(new_user)
    await session.commit()
    return {"msg": "User registered successfully"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(db_helper.get_scoped_session)):
    result = await session.execute(select(User).where(User.email == form_data.username))
    db_user = result.scalars().first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
