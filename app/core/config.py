from typing import Optional

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_title: str = "Charity Project"
    database_url: str = "sqlite+aiosqlite:///./cat_charities.db"
    secret: str = "SERCET_KEY"
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    VALIDATION_ERROR: int = 422
    BAD_REQUEST_ERROR: int = 400

    class Config:
        env_file = ".env"


settings = Settings()
