from pydantic import BaseModel, Field, EmailStr
from datetime import date


class ContactModel(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    phone: str = Field(max_length=10)
    birthday: date
    description: str


class ContactResponse(ContactModel):
    id: int

    class Config:
        from_attributes = True

