import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

from main import app
from src.database.db import get_db
from src.database.models import Base
from src.database.models import User
from src.services.auth import auth_service

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    """
    The init_models_wrap function is used to initialize the database with a test user.
    It will drop all tables and recreate them, then add a test user to the database.


    :return: A tuple of the test_user and the current_user
    :doc-author: Trelent
    """

    async def init_models():
        """
        The init_models function is used to initialize the database with a test user.
        It will drop all tables and recreate them, then add a test user to the database.

        :return: A tuple of the test_user and the current_user
        :doc-author: Trelent
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                password=hash_password,
                confirmed=True,
                role="admin",
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    """
    The client function is a fixture that will be called once per test function.
    It returns a TestClient instance, which provides an API to make HTTP requests.
    The client can also be used as an asynchronous context manager, in which case it will close the session after exiting the block.

    :return: A test client, which is a python object that acts like your application
    :doc-author: Trelent
    """

    async def override_get_db():
        """
        The override_get_db function is a fixture that allows us to override the get_db function.
        This is useful for testing purposes, as we can use this fixture to create a new database session
        for each test case, and then close it after the test has run. This helps ensure that each test
        case runs in complete isolation from one another.

        :return: A session object
        :doc-author: Trelent
        """
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    """
    The get_token function is used to create a token for the test user.
        This function will be called in the tests below.

    :return: A token which is used by the test_user_login function to log in
    :doc-author: Trelent
    """
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token
