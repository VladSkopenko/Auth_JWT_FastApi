from datetime import datetime
from datetime import timedelta

from sqlalchemy import extract
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.database.models import User
from src.schemas.contact import ContactSchema
from src.schemas.contact import ContactStatusUpdate
from src.schemas.contact import ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, current_user: User):
    """
    The get_contacts function returns a list of contacts for the current user.
        The limit and offset parameters are used to paginate the results.


    :param limit: int: Limit the number of results returned
    :param offset: int: Skip the first n rows of the database
    :param db: AsyncSession: Pass the database connection to the function
    :param current_user: User: Filter the contacts by user
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=current_user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_contacts function returns a list of all contacts in the database.
        The limit and offset parameters are used to paginate the results.


    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of rows to skip before starting to return rows
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of all contacts in the database
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contact = await db.execute(stmt)
    return contact.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the contact id to be returned
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Ensure that the user can only access their own contacts
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, current_user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body and convert it into a contact object
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=current_user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, current_user: User
):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Identify the contact to be updated
    :param body: ContactUpdateSchema: Validate the data sent in the request body
    :param db: AsyncSession: Access the database
    :param current_user: User: Check if the user is authenticated
    :return: A contact object, which is the same as what we get from the create_contact function
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.notes = body.notes
        contact.favourite = body.favourite
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Identify the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Ensure that the user is only deleting their own contacts
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def update_status_contact(
    contact_id: int, body: ContactStatusUpdate, db: AsyncSession, current_user: User
):
    """
    The update_status_contact function updates the status of a contact.

    :param contact_id: int: Identify the contact to update
    :param body: ContactStatusUpdate: Get the favourite status of a contact
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Ensure that the user is only able to update their own contacts
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.favourite = body.favourite
        await db.commit()
        await db.refresh(contact)
    return contact


async def search_contacts(search: str, db: AsyncSession, current_user: User):
    """
    The search_contacts function searches for contacts in the database.
        It takes a search string and returns all contacts that match the search criteria.


    :param search: str: Filter the contacts by name, lastname or email
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Filter the results by the user that is currently logged in
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = (
        select(Contact)
        .filter_by(user=current_user)
        .where(
            or_(
                Contact.name.ilike(f"%{search}%"),
                Contact.lastname.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_birthday_contacts(days: int, db: AsyncSession, current_user: User):
    """
    The get_birthday_contacts function returns a list of contacts whose birthday is within the next X days.

    :param days: int: Determine how many days in the future to look for birthdays
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Filter the contacts by user
    :return: A list of contacts
    :doc-author: Trelent
    """
    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    birthday_month = extract("month", Contact.birthday)
    birthday_day = extract("day", Contact.birthday)

    current_year_birthday = func.to_date(
        func.concat(
            func.to_char(today, "YYYY"),
            "-",
            func.to_char(birthday_month, "FM00"),
            "-",
            func.to_char(birthday_day, "FM00"),
        ),
        "YYYY-MM-DD",
    )

    next_year_birthday = func.to_date(
        func.concat(
            func.to_char(today + timedelta(days=365), "YYYY"),
            "-",
            func.to_char(birthday_month, "FM00"),
            "-",
            func.to_char(birthday_day, "FM00"),
        ),
        "YYYY-MM-DD",
    )

    stmt = (
        select(Contact)
        .filter_by(user=current_user)
        .where(
            or_(
                current_year_birthday.between(today, end_date),
                next_year_birthday.between(today, end_date),
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()
