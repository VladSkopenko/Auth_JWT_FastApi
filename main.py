from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from ipaddress import ip_address
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.database.db import get_db
from src.routes import contacts, auth, check_open, users
from src.database.config import config

ALLOWED_IPS = [ip_address('192.168.1.0'), ip_address('172.16.0.0'), ip_address("127.0.0.1")]
banned_ips = [ip_address("190.235.111.156"), ip_address("82.220.71.77"), ip_address("45.100.28.227")]
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
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in banned_ips:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(users.router, prefix="/api")
app.include_router(check_open.router, prefix="/api")
app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def root():
    return {"message": "Contact Book"}


@app.get('/api/healthchecker')
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
