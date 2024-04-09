from pathlib import Path

import redis.asyncio as redis
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import config
from src.database.db import get_db
from src.middlewares import ip_middleware
from src.middlewares import user_agent_middleware
from src.routes import auth
from src.routes import check_open
from src.routes import contacts
from src.routes import users

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["AUTHORIZATION", "HOST", "Content-Type", "origin"],
)
app.middleware("http")(ip_middleware.limit_access_by_ip)
app.middleware("http")(ip_middleware.ban_ips)
app.middleware("http")(user_agent_middleware.user_agent_ban_middleware)

BASE_DIR = Path(__file__).parent
directory = BASE_DIR.joinpath("src").joinpath("static")
app.mount("/static", StaticFiles(directory=directory), name="static")


app.include_router(users.router, prefix="/api")
app.include_router(check_open.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like database connections or external APIs.

    :return: A dictionary with a key called &quot;app&quot;
    :doc-author: Trelent
    """
    redi = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(redi)


template = Jinja2Templates(directory="src/templates")


@app.get(
    "/",
    response_class=HTMLResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
def root(request: Request):
    """
    The root function is the entry point for the web application.
    It returns a TemplateResponse object, which contains an HTML template and data to be rendered by Jinja2.
    The template file is located in `templates/index.html`.


    :param request: Request: Pass the request object into the function
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return template.TemplateResponse("index.html", context={"request": request})


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by executing a SQL query and checking if it returns any results. If it doesn't,
    then we know something is wrong with our database connection.

    :param db: AsyncSession: Inject the database session into the function
    :return: A dictionary with a message
    :doc-author: Trelent
    """
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
