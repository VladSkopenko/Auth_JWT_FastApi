from unittest.mock import MagicMock
from src.conf import messages
from main import app
from datetime import datetime
import pytest
from fastapi import HTTPException, status
from conftest import TestingSessionLocal
from sqlalchemy import select
from src.database.models import User

user_data = {
    "username": "testauth",
    "email": "testauth@gmail.com",
    "password": "111111",
}
app.user_middleware = []


def test_signup(client, monkeypatch, log):
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
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_not_user_login(client):
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
