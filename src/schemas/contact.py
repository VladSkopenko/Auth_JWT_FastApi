from datetime import date
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import ConfigDict

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    lastname: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone: str
    birthday: date
    notes: str = Field(max_length=250)
    favourite: Optional[bool] = False


class ContactUpdateSchema(ContactSchema):
    favourite: bool


class ContactStatusUpdate(BaseModel):
    favourite: bool


class ContactResponse(BaseModel):
    id: int = 1
    name: str | None
    lastname: str | None
    email: EmailStr | None
    phone: str | None
    birthday: date | None
    notes: str | None
    favourite: bool | None
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    model_config = ConfigDict(from_attributes=True)


