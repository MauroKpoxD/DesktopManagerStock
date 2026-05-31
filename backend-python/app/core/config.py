"""
ÚLTIMA MODIFICACIÓN: 30/5/2025 por S4NDULOS
PROPÓSITO: Carga variables de entorno y expone la configuración global.
           Incluye rutas de directorios, datos de autenticación y umbrales de stock.
"""

from pydantic_settings import BaseSettings
from pydantic import model_validator
from pathlib import Path

class Settings(BaseSettings):
    # ---------- API ----------
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = True
    api_version: str = "0.1.1"

    # ---------- Base de datos ----------
    database_url: str = "sqlite:///./stock.db"

    # ---------- Seguridad ----------
    secret_key: str   
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ---------- Stock ----------
    stock_alert_threshold: int = 5

    # ---------- Rutas de usuario ----------
    users_data_dir: str = "./usuarios"

    # ---------- Propiedades derivadas ----------
    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @property
    def reports_dir(self) -> Path:
        return self.base_dir / "reports"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"

    @property
    def users_root(self) -> Path:
        return Path(self.users_data_dir).resolve()

    def get_user_dir(self, username: str) -> Path:
        """Carpeta personal del usuario (se crea si no existe)"""
        user_path = self.users_root / username
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path

    # ---------- Validaciones y creacion de carpetas ----------
    @model_validator(mode='after')
    def ensure_directories(self):
        self.users_root.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()