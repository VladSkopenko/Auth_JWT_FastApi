from unittest.mock import MagicMock
from src.conf.messages import ACCOUNT_EXIST
from main import app
from datetime import datetime
import pytest
from fastapi import HTTPException, status


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
    log.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - {client} is register successfully\n")
    assert "password" not in data
    assert "avatar" in data


# def test_repeat_signup(client, monkeypatch):
#     mock_send_email = MagicMock()
#     monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
#     with pytest.raises(HTTPException) as exc_info:
#         client.post("api/auth/signup", json=user_data)
#
#     assert exc_info.value.status_code == status.HTTP_409_CONFLICT
#     assert exc_info.value.detail == ACCOUNT_EXIST
