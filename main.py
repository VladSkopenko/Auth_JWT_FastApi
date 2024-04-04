import re
from ipaddress import ip_address
from typing import Callable

import redis.asyncio as redis
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import config
from src.database.db import get_db
from src.routes import auth
from src.routes import check_open
from src.routes import contacts
from src.routes import users

ALLOWED_IPS = [
    ip_address("192.168.1.0"),
    ip_address("172.16.0.0"),
    ip_address("127.0.0.1"),
]
banned_ips = [
    ip_address("190.235.111.156"),
    ip_address("82.220.71.77"),
    ip_address("45.100.28.227"),
]
user_agent_ban_list = [r"bot-Yandex", r"Googlebot"]

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["AUTHORIZATION", "HOST", "Content-Type", "origin"],
)


@app.middleware("http")
async def limit_access_by_ip(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip not in ALLOWED_IPS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Not allowed IP address"},
        )
    response = await call_next(request)
    return response


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in banned_ips:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
        )
    response = await call_next(request)
    return response


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(users.router, prefix="/api")
app.include_router(check_open.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


template = Jinja2Templates(directory="src/templates")


@app.get(
    "/",
    response_class=HTMLResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
def root(request: Request):
    return template.TemplateResponse("index.html", context={"request": request})


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
