from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, EmailStr
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str

    PORT: int = 8000

    ORIGINS: List[str] = []

    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_SECONDS: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()  # type: ignore
