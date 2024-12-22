# core/config.py
from typing import Optional

from pydantic import BaseSettings
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_title: str = "Charity Project"
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = "SERCET_KEY"
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
