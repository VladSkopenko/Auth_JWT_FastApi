import unittest
from datetime import datetime
from datetime import timedelta
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.database.models import User
from src.repository.contacts import create_contact
from src.repository.contacts import delete_contact
from src.repository.contacts import get_all_contacts
from src.repository.contacts import get_birthday_contacts
from src.repository.contacts import get_contact
from src.repository.contacts import get_contacts
from src.repository.contacts import search_contacts
from src.repository.contacts import update_contact
from src.repository.contacts import update_status_contact
from src.schemas.contact import ContactSchema
from src.schemas.contact import ContactStatusUpdate
from src.schemas.contact import ContactUpdateSchema


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        """
        The setUp function is called before each test function.
        It creates a new user and session object for each test.

        :param self: Represent the instance of the class
        :return: None, so the test case is not going to fail
        :doc-author: Trelent
        """
        self.user = User(
            id=1, username="test_user", password="qwerty", confirmed="True"
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        """
        The test_get_all_contacts function tests the get_all_contacts function.
        It does this by creating a mock session object, and then mocking the return value of
        the execute method on that session object. The mocked return value is a MagicMock object,
        which has its own scalars method mocked to return another MagicMock object with an all method
        mocked to return a list of Contact objects.

        :param self: Represent the instance of the class
        :return: A list of contacts
        :doc-author: Trelent
        """
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
        """
        The test_get_contacts function tests the get_contacts function.
        It does this by mocking a session object and a user object, then calling the get_contacts function with these mocked objects as arguments.
        The test asserts that the result of calling get_contacts is equal to an expected list of contacts.

        :param self: Refer to the instance of the class
        :return: Contacts
        :doc-author: Trelent
        """
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
        """
        The test_get_contact function tests the get_contact function.
            It does so by creating a mocked contact object, and then passing it to the
            get_contact function. The result is compared with the expected value.

        :param self: Represent the instance of the class
        :return: The contact object
        :doc-author: Trelent
        """
        id_ = 1
        contact = Contact(id=1, name="test", lastname="test", user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(id_, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        """
        The test_create_contact function tests the create_contact function.
        It creates a ContactSchema object with some data, and then uses that to create a Contact object.
        Then it calls the create_contact function with those objects as arguments, and checks if the result is an instance of type(Contact).
        It also checks if all fields are equal between body (the schema) and contact (the model).

        :param self: Access the attributes and methods of the class in python
        :return: An instance of the contact class
        :doc-author: Trelent
        """
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
        self.session.refresh.assert_called_once()
        self.session.commit.assert_called_once()

    async def test_update_contact(self):
        """
        The test_update_contact function tests the update_contact function.
        It does so by creating a ContactUpdateSchema object, which is used as the body of an HTTP request to update a contact.
        The mocked_contact object is created using MagicMock and returns a Contact object with id=2, name=&quot;new&quot;, lastname=&quot;test2&quot;, email=&quot;test@example.com&quot;, phone=&quot;123456789&quot;, birthday=2000-01-01, notes = &quot;Some notes&quot; and favourite = True when its scalar_one_or_none method is called (which it will be). The session's execute method then returns this

        :param self: Represent the instance of the class
        :return: An instance of the contact class
        :doc-author: Trelent
        """
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
        self.session.refresh.assert_called_once()
        self.session.commit.assert_called_once()

    async def test_delete_contact(self):
        """
        The test_delete_contact function tests the delete_contact function in the contacts.py file.
        It does this by creating a mocked contact object, and then setting its scalar_one_or_none method to return a Contact object with an id of 1 and name &quot;test&quot;.
        Then it sets self.session's execute method to return that mocked contact object, which is what delete_contact would do when called on that session with an id of 1 (and user).
        The test then calls delete_contact on those parameters, and asserts that self.session's methods were called once each as expected.

        :param self: Represent the instance of the class
        :return: An instance of the contact class
        :doc-author: Trelent
        """
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, name="test")
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.execute.assert_called_once()
        self.assertIsInstance(result, Contact)

    async def test_update_status_contact(self):
        """
        The test_update_status_contact function tests the update_status_contact function.
        It does so by creating a ContactStatusUpdate object, which is passed to the update_status_contact function.
        The mocked contact object is then returned from the database and compared with an expected result.

        :param self: Refer to the class itself
        :return: A contact object
        :doc-author: Trelent
        """
        body = ContactStatusUpdate(favourite=True)

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
        result = await update_status_contact(1, body, self.session, self.user)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertIsInstance(result, Contact)

    async def test_search_contacts(self):
        """
        The test_search_contacts function tests the search_contacts function.
        It creates a list of two contacts, and then mocks the session object to return that list when it is called.
        The test then calls search_contacts with &quot;test&quot; as an argument, which should return both contacts in the mocked list.

        :param self: Represent the instance of the class
        :return: A list of contacts
        :doc-author: Trelent
        """
        contacts = [
            Contact(id=1, name="test", lastname="test", user=self.user),
            Contact(id=2, name="test2", lastname="test2", user=self.user),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts("test", self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_birthday_contacts(self):
        """
        The test_get_birthday_contacts function tests the get_birthday_contacts function.
        It creates a list of contacts with birthdays within 7 days, and then calls the
        get_birthday_contacts function to retrieve those contacts. It then asserts that
        the returned list is equal to the created list.

        :param self: Refer to the class instance itself
        :return: A list of contacts that have a birthday within the next 7 days
        :doc-author: Trelent
        """
        today = datetime.now().date()
        days = 7
        contacts = [
            Contact(
                name="John",
                lastname="Doe",
                birthday=today + timedelta(days=days),
                user=self.user,
            ),
            Contact(
                name="Jane",
                lastname="Smith",
                birthday=today + timedelta(days=days),
                user=self.user,
            ),
        ]

        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result_days = await get_birthday_contacts(days, self.session, self.user)
        self.assertEqual(result_days, contacts)
        if len(result_days) >= 2:
            self.assertEqual(result_days[0].user, result_days[1].user)
        for res in result_days:
            self.assertTrue((res.birthday - today).days <= days)


if __name__ == "__main__":
    unittest.main()
