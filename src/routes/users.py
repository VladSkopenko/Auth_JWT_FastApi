from fastapi import APIRouter, Depends

from src.schemas.user import UserResponse
from src.database.models import User
from src.services.auth import auth_service

router = APIRouter(prefix="users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_service.get_current_user())):
    return user
