from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import HTMLResponse

from app.core.config import settings
from app.core.db_helper import DataBaseHelper
from app.models import Base
from app.auth.controller.jwt_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.post_controller import router as post_router
from app.controllers.web_controller import router as web_router

db_helper = DataBaseHelper(
    url=settings.db_url,
    echo=settings.db_echo
)

app = FastAPI(title="FastAPI V1")
app.include_router(router=auth_router, prefix="/auth")
app.include_router(router=user_router, prefix="/user")
app.include_router(router=post_router, prefix="/post")
app.include_router(router=web_router)

BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.on_event("startup")
async def on_startup():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content="Ошибка базы данных")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    return JSONResponse(status_code=500, content="Внутренняя ошибка сервера")


# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
