import ssl
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

# Raíz del proyecto backend (fitlife-backend-melo), donde suelen estar .env y ca.pem
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "fitlife_user"
    DB_PASSWORD: str = "fitlife_pass"
    DB_NAME: str = "fitlife_db"
    # Aiven / MySQL en la nube: True + ruta al CA PEM (p. ej. ca.pem en la raíz del backend)
    DB_USE_SSL: bool = False
    DB_SSL_CA: Optional[str] = None

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

    def _resolved_ssl_ca(self) -> Optional[str]:
        if not self.DB_SSL_CA or not str(self.DB_SSL_CA).strip():
            return None
        p = Path(self.DB_SSL_CA.strip())
        if p.is_absolute():
            return str(p.resolve())
        return str((_BACKEND_ROOT / p).resolve())

    def get_database_url(self) -> str:
        """URL async para SQLAlchemy (escapa user/password por @, :, etc.)."""
        u = quote_plus(self.DB_USER)
        p = quote_plus(self.DB_PASSWORD)
        return f"mysql+aiomysql://{u}:{p}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def mysql_connect_args(self) -> dict:
        """aiomysql + asyncio: exige ssl.SSLContext (no dict)."""
        if not self.DB_USE_SSL:
            return {}
        ctx = ssl.create_default_context()
        ca = self._resolved_ssl_ca()
        if ca:
            ctx.load_verify_locations(cafile=ca)
        return {"ssl": ctx}

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
