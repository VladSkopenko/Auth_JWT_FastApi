from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas.user import RequestEmail
from src.schemas.user import TokenSchema
from src.schemas.user import UserResponse
from src.schemas.user import UserSchema
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages
router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserSchema,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The signup function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param bt: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Get the database session
    :param : Get the user's email
    :return: A userschema object
    :doc-author: Trelent

    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    The login function is used to authenticate a user.

    :param body: OAuth2PasswordRequestForm: Get the username and password
    :param db: AsyncSession: Get the database session
    :return: A dictionary with an access token, a refresh token and the type of token
    :doc-author: Trelent

    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns a new access_token,
        refresh_token, and the type of bearer.

    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the request header
    :param db: AsyncSession: Get the database session
    :param : Get the user's email from the token
    :return: A new access_token and refresh_token
    :doc-author: Trelent

    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do not exist,
        we raise an HTTPException with a status code of 400 (Bad Request) and detail message &quot;Verification error&quot;.

    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database session
    :return: A message to the user that their email has been confirmed
    :doc-author: Trelent

    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR
        )
    if user.confirmed:
        return {"message": messages.ALREADY_CONFIRMED}
    await repository_users.confirmed_email(email, db)
    return {"message": messages.EMAIL_CONFIRMED}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their email address. The function takes in a RequestEmail object, which contains the
    email of the user who wants to confirm their account. It then checks if there is already a confirmed
    user with that email address, and if so returns an error message saying as much. If not, it sends
    an asynchronous task (using FastAPI's BackgroundTasks) to send_email(), passing in the user's email, username and base url.

    :param body: RequestEmail: Get the email from the body of the request
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param db: AsyncSession: Get the database session
    :param : Send the email to the user
    :return: A message to the user
    :doc-author: Trelent

    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": messages.ALREADY_CONFIRMED}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": messages.CHECK_YOUR_EMAIL}


@router.patch(
    "/reset_pass",
    response_model=UserResponse,
)
async def reset_password(
    new_password: str,
    bt: BackgroundTasks,
    request: Request,
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The reset_password function is used to reset a user's password.

    :param new_password: str: Get the new password from the request body
    :param bt: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param user: User: Get the current user
    :param db: AsyncSession: Get a database session
    :param : Get the current user
    :return: The user object
    :doc-author: Trelent

    """
    hashed_password = auth_service.get_password_hash(new_password)
    user = await repository_users.reset_password(user.email, hashed_password, db)
    bt.add_task(send_email, user.email, user.username, str(request.base_url))
    return user
