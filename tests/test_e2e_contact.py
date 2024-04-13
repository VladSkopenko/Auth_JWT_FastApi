from unittest.mock import patch
from unittest.mock import patch, MagicMock, AsyncMock
from main import app
from src.services.auth import auth_service

app.user_middleware = []


def test_get_contacts(client, get_token):
    """
    The test_get_contacts function tests the get_contacts function in the contacts.py file.
    It does this by using a client to make a GET request to /api/contacts, and then asserts that
    the response status code is 200.

    :param client: Make the request to the api
    :param get_token: Get the token from the fixture
    :return: A 200 response code and a list of contacts
    :doc-author: Trelent
    """
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 200, response.text


def test_create_contacts(client, get_token, monkeypatch):
    """
    The test_create_contacts function tests the creation of a new contact.
    It does so by first mocking the redis cache, and then sending a POST request to
    the api/contacts endpoint with an Authorization header containing a valid JWT token.
    The response is checked for status code 201 (Created), and its JSON data is checked for correctness.

    :param client: Make requests to the flask application
    :param get_token: Get the token from the fixture
    :return: A 201 status code and a json object with the created contact
    :doc-author: Trelent
    """
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.post(
            "api/contacts",
            headers=headers,
            json={
                "name": "test",
                "lastname": "testovich",
                "email": "example@example.com",
                "phone": "123456789",
                "birthday": "1990-01-01",
                "notes": "Some notes here",
            },
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "test"
        assert data["lastname"] == "testovich"
        assert "password" not in data
