from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "fitlife_user"
    DB_PASSWORD: str = "fitlife_pass"
    DB_NAME: str = "fitlife_db"

    # JWT
    JWT_SECRET_KEY: str = "yoursecretkeyhere"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Email (RF-012 a RF-014)
    FRONTEND_URL: str = "http://localhost:4200"
    EMAIL_FROM: str = "noreply@fitlife.app"
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = "your-email@gmail.com"
    EMAIL_PASSWORD: str = "your-app-password"

    # App
    DEBUG: bool = True
    API_VERSION: str = "v1"
    CORS_ORIGINS: str = "http://localhost:4200,http://localhost:5173,http://127.0.0.1:5173"
    # Código para registrarse como admin (poner en .env: ADMIN_REGISTER_CODE=fitlife-admin-2026)
    ADMIN_REGISTER_CODE: str = "fitlife-admin-2026"

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
