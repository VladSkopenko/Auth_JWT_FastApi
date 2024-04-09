from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

router = APIRouter(prefix="/check_open", tags=["check_open"])


@router.get("/{username}")
async def check_open_f(
    username: str, response: Response, db: AsyncSession = Depends(get_db)
):
    """
    The check_open_f function is a function that checks if the user has opened the email.
        It takes in three parameters: username, response and db. The username parameter is
        used to identify which user we are checking for, while the response parameter is
        used to return an image file that will be displayed on screen when this endpoint
        gets called by our frontend application. The db parameter allows us to access our database.

    :param username: str: Get the username from the url
    :param response: Response: Return a response to the user
    :param db: AsyncSession: Get a database connection from the dependency
    :return: A png image
    :doc-author: Trelent
    """
    print("-" * 100)
    print(f"{username} відкрив email")
    print("-" * 100)
    return FileResponse(
        "src/static/open_check.png",
        media_type="image.png",
        content_disposition_type="inline",
    )
