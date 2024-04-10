import os
import sys
import unittest
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

sys.path.append(os.path.abspath('..'))

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.database.models import User
from src.repository.contacts import get_all_contacts
from src.repository.contacts import get_contacts


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(
            id=1, username="test_user", password="qwerty", confirmed="True"
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, name="test", lastname="test", user=self.user),
            Contact(id=2, name="test2", lastname="test2", user=self.user),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, name="test", lastname="test", user=self.user),
            Contact(id=2, name="test2", lastname="test2", user=self.user),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)


if __name__ == "__main__":
    unittest.main()
