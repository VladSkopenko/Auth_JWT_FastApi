from unittest.mock import MagicMock
from src.middlewares.ip_middleware import ban_ips
from main import app

user_data = {
    "username": "testauth",
    "email": "testauth@gmail.com",
    "password": "111111",
}
app.user_middleware = []

def test_signup(client, monkeypatch):
    # Працюэ лише якщо ігнорити мідлвари
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data
