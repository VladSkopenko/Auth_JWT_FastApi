import unittest
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.database.models import User
from src.repository.contacts import get_all_contacts
from src.repository.contacts import get_contact
from src.repository.contacts import get_contacts
from src.repository.contacts import create_contact
from src.repository.contacts import update_contact
from src.repository.contacts import delete_contact


from src.schemas.contact import ContactSchema
from src.schemas.contact import ContactUpdateSchema


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

    async def test_get_contact(self):
        id_ = 1
        contact = Contact(id=1, name="test", lastname="test", user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(id_, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactSchema(
            name="test",
            lastname="test2",
            email="test@example.com",
            phone="123456789",
            birthday="2000-01-01",
            notes="Some notes",
        )
        contact = Contact(**body.model_dump(exclude_unset=True), user=self.user)
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, type(contact))
        self.assertEqual(body.name, contact.name)
        self.assertEqual(body.email, contact.email)

    async def test_update_contact(self):
        body = ContactUpdateSchema(
            name="new",
            lastname="test2",
            email="test@example.com",
            phone="123456789",
            birthday="2000-01-01",
            notes="Some notes",
            favourite=True,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            name="new",
            lastname="test2",
            email="test@example.com",
            phone="123456789",
            birthday="2000-01-01",
            notes="Some notes",
            favourite=True,
        )
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, name="test")
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.execute.assert_called_once()
        self.assertIsInstance(result, Contact)


if __name__ == "__main__":
    unittest.main()
