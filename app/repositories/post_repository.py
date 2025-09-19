from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status

from app.models import Post
from app.schemas.post import PostCreate


async def get_posts(session: AsyncSession, owner_id: int):
    try:
        result = await session.execute(select(Post).where(Post.owner_id == owner_id).order_by(Post.id))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_all_posts(session: AsyncSession):
    try:
        result = await session.execute(select(Post).order_by(Post.id))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_post_by_id(session: AsyncSession, post_id: int) -> Post | None:
    try:
        return await session.get(Post, post_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} not found. More detailed: {str(e)}")


async def create_post(session: AsyncSession, post_in: PostCreate, owner_id: int) -> Post:
    try:
        db_post = Post(
            tittle=post_in.tittle,
            description=post_in.description,
            required_access_id=post_in.required_access_id,
            owner_id=owner_id,
        )
        session.add(db_post)
        await session.commit()
        await session.refresh(db_post)
        return db_post
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_post(session: AsyncSession, post: Post) -> None:
    try:
        await session.delete(post)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
