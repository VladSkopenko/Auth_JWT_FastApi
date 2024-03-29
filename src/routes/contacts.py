from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactModel, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/search", response_model=list[ContactResponse])
async def search_contacts(query: str, db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.search_contacts(query, db, current_user)
    return contacts


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 5, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, db, current_user)
    return contacts


@router.post("/read", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body, db, current_user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactModel)
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return contact


@router.get("/{id}")
async def get_contact(
        id: int = Path(description="id of the contact", gt=0),
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repository_contacts.get_contact(id, db)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact is not found"
        )

    return contact


@router.get("/contacts/upcoming_birthdays/", response_model=List[ContactModel])
def get_upcoming_birthdays_list(db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    return repository_contacts.get_upcoming_birthdays(db=db)
