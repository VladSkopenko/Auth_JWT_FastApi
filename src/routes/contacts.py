from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from fastapi import status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import Role
from src.database.models import User
from src.repository import contacts as repository_contact
from src.schemas.contact import ContactResponse
from src.schemas.contact import ContactSchema
from src.schemas.contact import ContactStatusUpdate
from src.schemas.contact import ContactUpdateSchema
from src.services.auth import auth_service
from src.services.role import RoleAccess

router = APIRouter(prefix="/contacts", tags=["contacts"])
access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Specify the number of records to skip
    :param ge: Set a minimum value for the limit and offset parameters
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :param : Get the contact by id
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contact.get_contacts(limit, offset, db, current_user)
    return contacts


@router.get(
    "/all",
    response_model=list[ContactResponse],
    dependencies=[Depends(access_to_route_all)],
)
async def get_all_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_all_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Specify the minimum value of the parameter
    :param le: Limit the number of contacts returned
    :param offset: int: Skip the first n records
    :param ge: Specify a lower limit for the value of the parameter
    :param db: AsyncSession: Pass in the database connection
    :param current_user: User: Get the current user from the database
    :param : Limit the number of contacts returned
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contact.get_all_contacts(limit, offset, db)
    return contacts


@router.post(
    "/",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Get a database session
    :param current_user: User: Get the current user from the database
    :param : Get the contact id
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contact.create_contact(body, db, current_user)
    return contact


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(
    search: str = Query(min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The search_contacts function searches for contacts in the database.

    :param search: str: Get the search string from the query params
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :param : Search the contacts in the database
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contacts = await repository_contact.search_contacts(search, db, current_user)
    return contacts


@router.get("/birthdays/", response_model=list[ContactResponse])
async def get_birthday_contacts(
    days: int = Query(7, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_birthday_contacts function returns a list of contacts that have birthdays within the next 7 days.

    :param days: int: Specify how many days in the future to look for birthdays
    :param ge: Specify that the value of days must be greater than or equal to 1
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :param : Specify the number of days to look ahead for birthdays
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contacts = await repository_contact.get_birthday_contacts(days, db, current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The get_contact function returns a contact by its id.

    :param contact_id: int: Get the contact id from the path
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :param : Get the contact id from the url
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contact.get_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.put("/{contact_id}")
async def update_contact(
    body: ContactUpdateSchema,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_contact function updates a contact in the database.
        It takes an id, body and db as arguments. The body is validated using ContactUpdateSchema
        and then passed to repository_contact's update_contact function along with the id, db and current user.

    :param body: ContactUpdateSchema: Validate the request body
    :param contact_id: int: Get the id of the contact to be deleted
    :param db: AsyncSession: Get a database session
    :param current_user: User: Get the current user from the auth_service
    :param : Get the contact id from the url
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contact.update_contact(
        contact_id, body, db, current_user
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact id to delete
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :param : Get the contact id from the url
    :return: A contact model
    :doc-author: Trelent
    """
    contact = await repository_contact.delete_contact(contact_id, db, current_user)
    return contact


@router.patch(
    "/{contact_id}", response_model=ContactResponse, status_code=status.HTTP_200_OK
)
async def update_status_contact(
    body: ContactStatusUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_status_contact function updates the status of a contact.

    :param body: ContactStatusUpdate: Get the status of the contact
    :param contact_id: int: Find the contact in the database
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user information
    :param : Get the contact id
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contact.update_status_contact(
        contact_id, body, db, current_user
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return contact
