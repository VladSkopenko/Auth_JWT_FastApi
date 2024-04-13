from unittest.mock import AsyncMock
from unittest.mock import patch

from main import app
from src.services.auth import auth_service

app.user_middleware = []


def test__current_user(client, get_token, monkeypatch):
    """
    The test__current_user function tests the /api/users/me endpoint.
    It does this by first patching the auth_service's cache with a mock object, and then setting up mocks for FastAPILimiter's redis, identifier, and http_callback functions.
    Then it makes a GET request to /api/users/me with an Authorization header containing a valid JWT token (obtained from get_token).
    Finally it asserts that the response status code is 200.

    :param client: Make requests to the api
    :param get_token: Get a token for the user
    :param monkeypatch: Replace the redis and identifier functions with asyncmock
    :return: The current user
    :doc-author: Trelent
    """
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
