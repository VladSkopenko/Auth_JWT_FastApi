import pickle
from datetime import datetime
from datetime import timedelta
from typing import Optional

import pytz
import redis
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import config
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and a hashed password as arguments.
        It then uses the pwd_context object to verify that the plain-text password matches the hashed
        password.

        :param self: Make the function a method of the user class
        :param plain_password: Pass in the password that is being verified
        :param hashed_password: Compare the hashed password in the database to a plain text password that is entered by a user
        :return: True if the password is correct, and false otherwise
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as an argument and returns the hashed version of that password.
        The hash is generated using the pwd_context object's hash method, which uses bcrypt to generate a secure hash.

        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is to be hashed
        :return: A hash of the password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a JWT token with the following claims:
            - iat: Issued At Time, when the token was created.
            - exp: Expiration Time, when the token will expire.
            - scope: The scope of this access_token (e.g., &quot;access_token&quot;).

        :param self: Access the class attributes and methods
        :param data: dict: Pass the data to be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A jwt token that contains the data passed to it
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(pytz.UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(pytz.UTC) + timedelta(minutes=10)
        to_encode.update(
            {"iat": datetime.now(pytz.UTC), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The time in seconds until the refresh token expires. Defaults to None, which is 7 days from creation date.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the user's id, username and email
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(pytz.UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(pytz.UTC) + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.now(pytz.UTC), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It will raise an exception if the token is invalid or has expired.

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            if it's valid, otherwise raises an HTTPException with status code 401.

        :param self: Access the class attributes and methods
        :param token: str: Pass the token from the authorization header
        :param db: AsyncSession: Get the database session
        :return: A user object
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user_hash: str = str(email)

        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
        The create_email_token function takes in a dictionary of data and returns a token.
        The function first creates an encoded copy of the data dictionary, then adds two keys to it: iat (issued at) and exp (expiration).
        It then uses the jwt library to encode this new dictionary with our SECRET_KEY and ALGORITHM.
        Finally, it returns this encoded token.

        :param self: Access the attributes and methods of the class
        :param data: dict: Pass in the data that will be encoded into the token
        :return: A token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.now(pytz.UTC) + timedelta(days=1)
        to_encode.update({"iat": datetime.now(pytz.UTC), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        It does this by decoding the JWT using our secret key and algorithm, then returning the subject (sub) field of the payload.

        :param self: Represent the instance of the class
        :param token: str: Pass the token as a string to the function
        :return: The email address from the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
