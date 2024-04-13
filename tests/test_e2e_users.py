from unittest.mock import patch, MagicMock, AsyncMock
from src.database.models import User
from main import app
from src.services.auth import auth_service

app.user_middleware = []


def test__current_user(client, get_token, monkeypatch):

    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.get(
            "api/users/me",
            headers=headers,
        )
        assert response.status_code == 200, response.text

