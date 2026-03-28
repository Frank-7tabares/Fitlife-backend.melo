import ssl
from pathlib import Path
from urllib.parse import quote_plus
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    DB_HOST: str = 'localhost'
    DB_PORT: int = 3306
    DB_USER: str = 'fitlife_user'
    DB_PASSWORD: str = 'fitlife_pass'
    DB_NAME: str = 'fitlife_db'
    DB_USE_SSL: bool = False
    DB_SSL_CA: Optional[str] = None
    JWT_SECRET_KEY: str = 'yoursecretkeyhere'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    FRONTEND_URL: str = 'http://localhost:4200'
    EMAIL_FROM: str = 'noreply@fitlife.app'
    EMAIL_HOST: str = 'smtp.gmail.com'
    EMAIL_PORT: int = 587
    EMAIL_USER: str = 'your-email@gmail.com'
    EMAIL_PASSWORD: str = 'your-app-password'
    DEBUG: bool = True
    API_VERSION: str = 'v1'
    CORS_ORIGINS: str = 'http://localhost:4200,http://localhost:5173,http://127.0.0.1:5173'
    ADMIN_REGISTER_CODE: str = 'fitlife-admin-2026'
    PASSWORD_RESET_EMAIL_SYNC: bool = False
    RESEND_API_KEY: Optional[str] = None
    RESEND_FROM: Optional[str] = None

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(',') if x.strip()]

    def _resolved_ssl_ca(self) -> Optional[str]:
        if not self.DB_SSL_CA or not str(self.DB_SSL_CA).strip():
            return None
        p = Path(self.DB_SSL_CA.strip())
        if p.is_absolute():
            return str(p.resolve())
        return str((_BACKEND_ROOT / p).resolve())

    def get_database_url(self) -> str:
        u = quote_plus(self.DB_USER)
        p = quote_plus(self.DB_PASSWORD)
        return f'mysql+aiomysql://{u}:{p}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    def mysql_connect_args(self) -> dict:
        if not self.DB_USE_SSL:
            return {}
        ctx = ssl.create_default_context()
        ca = self._resolved_ssl_ca()
        if ca:
            ctx.load_verify_locations(cafile=ca)
        return {'ssl': ctx}
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
settings = Settings()
