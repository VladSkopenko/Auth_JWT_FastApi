from pydantic import EmailStr
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ["HS256", "HS512"]:
            raise ValueError("ALGORITHM must be HS256 or HS512")
        return v

    class Config:
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
