from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import User

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)


async def update_entry(session: AsyncSession, model: ModelType, schema: SchemaType,
                       partial: bool = False) -> User:
    try:
        for key, value in schema.model_dump(exclude_unset=partial).items():
            setattr(model, key, value)
        await session.commit()
        await session.refresh(model)
        return model
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
