from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.service.jwt_service import get_current_user
from app.core.db_helper import db_helper
from app.models import User
from app.repositories import post_repository
from app.repositories import similar_repository
from app.schemas.post import PostRead, PostCreate, PostUpdate

router = APIRouter(tags=['posts'])


@router.get('/', response_model=list[PostRead],
            summary="Получить все посты из базы данных",
            description="Эндпоинт для получения всех постов из базы данных.")
async def get_all_posts(session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                        current_user: User = Depends(get_current_user)):
    return await post_repository.get_posts(session=session, owner_id=current_user.id,
                                           required_access=current_user.access_id)


async def get_post_by_id(post_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                         current_user: User = Depends(get_current_user)):
    post = await post_repository.get_post_by_id(session=session, post_id=post_id,
                                                required_access=current_user.access_id)
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post('/', response_model=PostRead, status_code=status.HTTP_201_CREATED,
             summary="Создать новый пост",
             description="Эндпоинт для создания нового поста. ")
async def create_post(
        post_in: PostCreate,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user: User = Depends(get_current_user)
):
    return await post_repository.create_post(session=session, post_in=post_in, required_access=current_user.access_id,
                                             owner_id=current_user.id)


@router.get('/{post_id}', response_model=PostRead,
            summary="Получить информацию о конкретном посте по его ID.",
            description="Эндпоинт для получения информации о существующем посте из базы данных. "
                        "Необходимо ввести ID поста.")
async def get_post(post: PostRead = Depends(get_post_by_id)):
    return post


@router.put('/{post_id}', response_model=PostRead,
            summary="Обновить всю информацию в посте",
            description="Эндпоинт для обновления всей информации в посте. ")
async def update_post(post_id: int, post_update: PostUpdate,
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                      current_user: User = Depends(get_current_user)):
    post = await post_repository.get_post_by_id(session=session, post_id=post_id,
                                                required_access=current_user.access_id)
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    return await similar_repository.update_entry(session=session, model=post, schema=post_update)


@router.patch("/{post_id}", response_model=PostRead,
              summary="Обновить информацию в посте частично",
              description="Эндпоинт для обновления некоторой информации в посте. ")
async def update_post(post_id: int, post_update: PostUpdate,
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                      current_user: User = Depends(get_current_user)):
    post = await post_repository.get_post_by_id(session=session, post_id=post_id,
                                                required_access=current_user.access_id)
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    return await similar_repository.update_entry(session=session, model=post, schema=post_update, partial=True)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удалить пост",
               description="Эндпоинт для удаления поста. "
                           "Необходимо ввести ID поста, который нужно удалить.")
async def delete_post(post_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency),
                      current_user: User = Depends(get_current_user)):
    post = await post_repository.get_post_by_id(session=session, post_id=post_id,
                                                required_access=current_user.access_id)
    if not post or post.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    await post_repository.delete_post(session=session, post=post)
    return None
