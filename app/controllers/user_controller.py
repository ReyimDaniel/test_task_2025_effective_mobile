from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.db_helper import db_helper
from app.schemas.user import User, UserUpdatePartial
from app.repositories import user_repository
from app.repositories import similar_repository
from app.schemas.user import UserRead, UserCreate, UserUpdate

router = APIRouter(tags=['users'])


@router.get('/', response_model=list[User], summary="Получить список всех пользователей",
            description="Эндпоинт для получения списка всех пользователей из базы данных.")
async def get_users(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.get_users(session=session)


@router.post('/', response_model=UserRead, status_code=status.HTTP_201_CREATED,
             summary="Создать нового пользователя",
             description="Эндпоинт для создания нового пользователя. "
                         "Необходимо ввести имя, почту и пароль.")
async def create_user(user_in: UserCreate,
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.create_user(session=session, user_in=user_in)


async def get_user_by_id(user_id: Annotated[int, Path],
                         session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> User:
    user = await user_repository.get_user_by_id(session=session, user_id=user_id)
    if user is not None:
        return user


@router.get('/{user_id}', response_model=User,
            summary="Получить информацию о конкретном пользователе по его ID.",
            description="Эндпоинт для получения информации о существующем пользователе из базы данных. "
                        "Необходимо ввести ID пользователя.")
async def get_user(user: User = Depends(get_user_by_id)):
    return user


@router.put('/{user_id}', response_model=User,
            summary="Обновить все данные о пользователе",
            description="Эндпоинт для обновления всей информации пользователя, существующего в базе данных. "
                        "Необходимо ввести все поля: имя, почту и пароль.")
async def update_user(user_update: UserUpdate,
                      user: User = Depends(get_user_by_id),
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await similar_repository.update_entry(session=session, model=user, schema=user_update)


@router.patch("/{user_id}", response_model=User,
              summary="Обновить данные о пользователе частично",
              description="Эндпоинт для обновления некоторой информации пользователя, существующего в базе данных. "
                          "Необходимо ввести те поля, которые нужно обновить: имя, почта или пароль.")
async def update_user_partial(user_update: UserUpdatePartial,
                              user: User = Depends(get_user_by_id),
                              session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await similar_repository.update_entry(session=session, model=user, schema=user_update, partial=True)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удалить пользователя",
               description="Эндпоинт для удаления пользователя, существующего в базы данных. "
                           "Необходимо ввести ID пользователя, которого нужно удалить.")
async def delete_user(user: User = Depends(get_user_by_id),
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.delete_user(session=session, user=user)


@router.patch("/{user_id}/deactivate", response_model=User,
              summary="Мягкое удаление пользователя(Блокировка)",
              description="Эндпоинт для мягкого удаления пользователя, существующего в базы данных. "
                          "Удаление записи не происходит. Статус пользователя становится неактивным. "
                          "Неактивный пользователь не может авторизоваться."
                          "Необходимо ввести ID пользователя, которого нужно удалить.")
async def soft_delete_user(user: User = Depends(get_user_by_id),
                           session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.soft_delete_user(session=session, user=user)
