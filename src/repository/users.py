from fastapi import Depends
from fastapi import HTTPException
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes in an email and returns the user associated with that email.
        If no user is found, it will return None.

    :param email: str: Get the email of a user
    :param db: AsyncSession: Get the database session
    :return: A user object, which is the result of a database query
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user whose token is being updated
    :param token: str | None: Update the user's refresh token
    :param db: AsyncSession: Commit the changes to the database
    :return: A user object
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Specify the email of the user whose avatar url is to be updated
    :param url: str | None: Set the avatar url for a user
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def reset_password(email: str, new_hashed_password: str, db: AsyncSession):
    """
    The reset_password function takes in an email and a new hashed password,
    and updates the user's password with the new one. It returns the updated user object.

    :param email: str: Get the user's email
    :param new_hashed_password: str: Pass in the new hashed password
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    if user:
        user.password = new_hashed_password
        await db.commit()
        await db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
