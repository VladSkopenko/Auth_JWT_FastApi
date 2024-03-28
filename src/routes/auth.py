from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status
from src.services.auth import auth_service
from src.database.db import get_db
from src.schemas.user import UserModel, UserResponse, TokenSchema
from src.repository import users as repositories_users
router = APIRouter(prefix='/auth', tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    return new_user


@router.post("/login")
async def login(body: UserModel, db: Session = Depends(get_db)):
    pass
    return {}


@router.get("/refresh_token")
async def refresh_token(body: UserModel, db: Session = Depends(get_db)):
    pass
    return {}