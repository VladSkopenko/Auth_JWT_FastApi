from typing import Type

from sqlalchemy.orm import Session
from src.database.models import Contact
from src.schemas.schemas import ContactModel
from sqlalchemy import or_, func, select

from datetime import datetime, timedelta


async def get_contacts(skip: int, limit: int, db: Session) -> list[Type[Contact]]:
    return db.query(Contact).offset(skip).limit(limit).all()


async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(name=body.name,
                      last_name=body.last_name,
                      email=body.email,
                      phone=body.phone,
                      birthday=body.birthday,
                      description=body.description)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.name = body.name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.description = body.description
        db.commit()
    return contact


async def delete_contact(contact_id: int, db: Session) -> None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_contact(id: int, db: Session):
    query = select(Contact).filter_by(id=id)
    contact = db.execute(query)
    return contact.scalar_one_or_none()


async def search_contacts(query: str, db: Session) -> list[Type[Contact]]:
    contacts = db.query(Contact).filter(
        or_(
            Contact.name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%"),
        )
    ).all()
    return contacts


def get_upcoming_birthdays(db: Session):
    today = datetime.now()
    end_date = today + timedelta(days=7)

    current_month = today.month
    current_day = today.day

    next_week_month = end_date.month
    next_week_day = end_date.day

    return db.query(Contact).filter(
        (
                (func.extract('month', Contact.birthday) == current_month) &
                (func.extract('day', Contact.birthday) >= current_day)
        ) | (
                (func.extract('month', Contact.birthday) == next_week_month) &
                (func.extract('day', Contact.birthday) <= next_week_day)
        )
    ).all()
