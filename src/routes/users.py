from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from src.schemas.user import UserResponse
from src.database.models import User
from src.services.auth import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user
