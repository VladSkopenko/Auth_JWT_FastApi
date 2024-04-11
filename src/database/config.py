from pydantic import EmailStr, ConfigDict
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    SECRET_KEY_JWT: str = "123213213123fgedgfdg"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "skopil123@meta.ua"
    MAIL_PASSWORD: str = "s1111"
    MAIL_FROM: str = "skopil123@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "example"
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "None"
    CLOUDINARY_NAME: str = "name"
    CLOUDINARY_API_KEY: int = 568222682695474123123
    CLOUDINARY_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        """
        The validate_algorithm function is a helper function that validates the algorithm used to sign the JWT.
        The validate_algorithm function takes in one argument, cls, which is an instance of the Auth0 class.
        The validate_algorithm function also takes in another argument, v, which represents a string value for
        the algorithm used to sign the JWT.

        :param cls: Pass the class object to the function
        :param v: Pass the value of the algorithm that is being validated
        :return: The value of the argument v
        :doc-author: Trelent
        """
        if v not in ["HS256", "HS512"]:
            raise ValueError("ALGORITHM must be HS256 or HS512")
        return v


    class Config:
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
