from pathlib import Path

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.templating import Jinja2Templates

from app.auth.service.jwt_service import verify_password, create_access_token, decode_jwt_token
from app.core.db_helper import db_helper
from app.models import User, Post
from app.models.user import RoleEnum
from app.repositories import user_repository, post_repository, similar_repository
from app.schemas.post import PostCreate, PostUpdate
from app.schemas.user import UserCreate

router = APIRouter()
BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/login")
async def login_submit(
        email: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    db_user = await user_repository.get_user_by_email(session, email)
    if not db_user or not verify_password(password, db_user.password):
        return RedirectResponse("/login?msg=Неверные данные", status_code=HTTP_303_SEE_OTHER)
    token = create_access_token({"sub": db_user.email})
    response = RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@router.post("/register")
async def register_user(
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        role: RoleEnum = Form(...),
        access_id: int = Form(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    exists = await user_repository.get_user_by_email(session, email)
    if exists:
        return RedirectResponse("/register?msg=Email уже зарегистрирован", status_code=HTTP_303_SEE_OTHER)
    await user_repository.create_user(
        session=session,
        user_in=UserCreate(username=username,
                           email=email,
                           password=password,
                           role=role,
                           is_active=True,
                           access_id=access_id)
    )
    return RedirectResponse("/login?msg=Регистрация успешна!", status_code=HTTP_303_SEE_OTHER)


async def get_current_user_from_cookie(request: Request, session: AsyncSession):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_jwt_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def get_current_user_from_cookie_optional(request: Request, session: AsyncSession, ):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = decode_jwt_token(token)
    except Exception:
        return None
    email = payload.get("sub")
    if not email:
        return None
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    return user


# @router.get("/index")
# async def index(request: Request, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
#     user = await get_current_user_from_cookie(request=request, session=session)
#     if not user:
#         return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
#     posts = await post_repository.get_posts(session=session, owner_id=user.id)
#     return templates.TemplateResponse("index.html", {"request": request, "user": user, "posts": posts})
@router.get("/index")
async def index(
        request: Request,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie_optional(request, session)
    posts = await post_repository.get_all_posts(session=session)
    if not user:
        return templates.TemplateResponse(
            "index.html", {"request": request, "posts": posts}
        )
    return templates.TemplateResponse(
        "index_auth.html", {"request": request, "user": user, "posts": posts}
    )


@router.post("/create_post")
async def create_post(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        required_access_id: int = Form(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    await post_repository.create_post(session, PostCreate(tittle=title, description=description,
                                                          required_access_id=required_access_id), owner_id=user.id)
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.post("/delete_post/{post_id}")
async def delete_post(post_id: int, request: Request,
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    post = await post_repository.get_post_by_id(session=session, post_id=post_id)
    if post and post.owner_id == user.id:
        await post_repository.delete_post(session=session, post=post)
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.post("/update_post")
async def update_post(
        post_id: int = Form(...),
        title: str = Form(...),
        description: str = Form(...),
        required_access_id: int = Form(...),
        request: Request = None,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)

    post = await post_repository.get_post_by_id(session=session, post_id=post_id)
    if post and post.owner_id == user.id:
        schema = PostUpdate(tittle=title, description=description, required_access_id=required_access_id)
        await similar_repository.update_entry(session=session, model=post, schema=schema)

    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.post("/update_post_partial")
async def update_post_partial(
        post_id: int = Form(...),
        title: str | None = Form(None),
        description: str | None = Form(None),
        request: Request = None,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    user = await get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    post = await post_repository.get_post_by_id(session, post_id)
    if not post or post.owner_id != user.id:
        raise HTTPException(status_code=404, detail="post not found")
    update_data = {
        "title": title if title and title.strip() else None,
        "description": description if description and description.strip() else None,
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}
    if update_data:
        post_update = PostUpdate(**update_data)
        await similar_repository.update_entry(session, post, post_update, partial=True)
    return RedirectResponse("/index", status_code=HTTP_303_SEE_OTHER)


@router.get("/post/{post_id}")
async def get_post(post_id: int, request: Request,
                   session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    post = await post_repository.get_post_by_id(session=session, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    user = await get_current_user_from_cookie(request, session)

    if not user:
        return RedirectResponse("/login", status_code=303)

    if user.access_id < post.required_access_id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    return templates.TemplateResponse("post_detail.html", {"request": request, "post": post, "user": user})


@router.get("/my_posts")
async def my_posts(request: Request, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    user = await get_current_user_from_cookie(request=request, session=session)
    if not user:
        return RedirectResponse("/login?msg=Для доступа авторизуйтесь", status_code=HTTP_303_SEE_OTHER)

    posts = await post_repository.get_posts(session=session, owner_id=user.id)
    return templates.TemplateResponse("my_posts.html", {"request": request, "user": user, "posts": posts})
