from src.database.db import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.models import User
from sqlalchemy import select
from libgravatar import Gravatar
from src.schemas.user import UserModel


async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    query = select(User).filter_by(email=email)
    user = db.execute(query)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserModel, db: Session = Depends(get_db)):
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str, db: Session):
    user.refresh_token = token
    db.commit()