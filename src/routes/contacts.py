from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/search", response_model=list[ContactResponse])
async def search_contacts(query: str, db: Session = Depends(get_db)):
    contacts = await repository_contacts.search_contacts(query, db)
    return contacts


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


@router.post("/", response_model=ContactResponse)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactModel)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return contact


@router.get("/{id}")
async def get_contact(
        id: int = Path(description="id of the contact", gt=0),
        db: Session = Depends(get_db),
):
    contact = await repository_contacts.get_contact(id, db)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact is not found"
        )

    return contact


@router.get("/contacts/upcoming_birthdays/", response_model=List[ContactModel])
def get_upcoming_birthdays_list(db: Session = Depends(get_db)):
    return repository_contacts.get_upcoming_birthdays(db=db)

