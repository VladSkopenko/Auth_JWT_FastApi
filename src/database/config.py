from pydantic_settings import BaseSettings
from pydantic import validators, ConfigDict, EmailStr, field_validator


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: str
    REDIS_PASSWORD: str

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ["HS256", "HS512"]:
            raise ValueError("Not like it")
        return v

    model_config = ConfigDict(env_file=".env",
                              env_file_encoding="utf-8")


config = Settings()
