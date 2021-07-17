from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from db import database
from users.router import router as users_router
from answer.router import router as answer_router
from problems.router import router as problem_router


DEBUG_MODE = False

app = FastAPI(
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
)

# 起動時にDatabaseに接続する。
@app.on_event("startup")
async def startup():
    await database.connect()


# 終了時にDatabaseを切断する。
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# users routerを登録する。
app.include_router(users_router)
# answer routerを登録する。
app.include_router(answer_router)
# problem routerを登録する。
app.include_router(problem_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# middleware state.connectionにdatabaseオブジェクトをセットする。
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.connection = database
    response = await call_next(request)
    return response
