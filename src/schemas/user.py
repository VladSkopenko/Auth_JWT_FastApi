from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=2, max_length=10)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

