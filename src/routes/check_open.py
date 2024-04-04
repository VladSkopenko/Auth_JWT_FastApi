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
    print("-" * 100)
    print(f"{username} відкрив email")
    print("-" * 100)
    return FileResponse(
        "src/static/open_check.png",
        media_type="image.png",
        content_disposition_type="inline",
    )
