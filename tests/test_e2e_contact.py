from unittest.mock import patch

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
        assert response.status_code == 200
