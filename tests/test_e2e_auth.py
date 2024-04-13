from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import select

from conftest import TestingSessionLocal
from main import app
from src.conf import messages
from src.database.models import User

user_data = {
    "username": "testauth",
    "email": "testauth@gmail.com",
    "password": "111111",
}
app.user_middleware = []


def test_signup(client, monkeypatch, log):
    """
    The test_signup function tests the signup endpoint.
    It does so by:
        1. Creating a mock for the send_email function, which is used in the signup endpoint to send an email to new users.
           This is done using monkeypatching, which allows us to replace functions with mocks during testing (see https://docs.pytest.org/en/latest/monkeypatch).
           The mock will be called later on in this test case and we can assert that it was called correctly (i.e., with correct arguments).

    :param client: Make requests to the application
    :param monkeypatch: Replace the send_email function with a mock object
    :param log: Write the log file
    :return: 201
    :doc-author: Trelent
    """
    # Працюэ лише якщо ігнорити мідлвари
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    log.write(
        f"{datetime.now():%Y-%m-%d %H:%M:%S} - {client} is register successfully\n"
    )
    assert "password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    """
    The test_repeat_signup function tests that a user cannot sign up twice with the same email address.
        It does this by first creating a mock send_email function, which is used in the signup route to send an email to
        new users. The test then posts data for a new user and asserts that it receives back an HTTP status code of 409,
        indicating conflict (i.e., there is already an account associated with this email address). Finally, it asserts that
        the response contains detail text explaining why the request failed.

    :param client: Make requests to the flask application
    :param monkeypatch: Mock the send_email function
    :return: The status code 409 and the message account_exist
    :doc-author: Trelent
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_not_email_login(client):
    """
    The test_not_email_login function tests that the login endpoint returns a 401 status code and an error message when
    the user attempts to log in with a username that is not an email address. The test_not_email_login function takes one
    parameter, client, which is the Flask test client. The response variable stores the result of calling post on
    client with &quot;api/auth/login&quot; as its first argument and data as its second argument. data contains two key-value pairs:
    username has &quot;Invalid email&quot; as its value and password has &quot;nothing&quot; as its value. Assert checks whether response's
    status code

    :param client: Test the api
    :return: A 401 status code and a message that the email is invalid
    :doc-author: Trelent
    """

    response = client.post(
        "api/auth/login",
        data={
            "username": "Invalid email",
            "password": "nothing",
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


def test_not_confirmed_login(client):
    """
    The test_not_confirmed_login function tests that a user cannot login if their email is not confirmed.
      The test_not_confirmed_login function uses the client fixture to make a POST request to the /api/auth/login endpoint with valid credentials for an unconfirmed user.
      The test asserts that the response status code is 401, and then asserts that the response JSON contains an error message indicating that email confirmation is required.

    :param client: Make requests to the application
    :return: A 401 status code and a message
    :doc-author: Trelent
    """

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.EMAIL_NOT_CONFIRMED


@pytest.mark.asyncio
async def test_login(client):
    """
    The test_login function tests the login endpoint.

    :param client: Make a request to the api
    :return: A response object, which is a dictionary
    :doc-author: Trelent
    """

    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_not_password_login(client):
    """
    The test_not_password_login function tests that a user cannot login with an incorrect password.

    :param client: Make requests to the api
    :return: A 401 status code and a message that the password is invalid
    :doc-author: Trelent
    """
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("email"),
            "password": "wrong",
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


def test_validation_error_login(client):
    """
    The test_validation_error_login function tests that the login endpoint returns a 422 status code when an invalid username is provided.
    It also checks that the response contains a detail key in its JSON body.

    :param client: Make requests to the flask application
    :return: A 422 error code and a detail message
    :doc-author: Trelent
    """

    response = client.post(
        "api/auth/login",
        data={
            "password": "wrong",
        },
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data
