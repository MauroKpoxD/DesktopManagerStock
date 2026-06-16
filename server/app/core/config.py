"""
ÚLTIMA MODIFICACIÓN: 9/6/2025 por S4NDULOS
PROPÓSITO: Carga variables de entorno y expone la configuración global
           Incluye validación de SECRET_KEY, control de seeder, CORS y rate limiting
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator, Field
from pathlib import Path

class Settings(BaseSettings):
# -------------------- API --------------------
    api_host: str = "127.0.0.1" # todavia en localhost
    api_port: int = 8000
    api_reload: bool = True
    api_version: str = "0.1.1"

# -------------------- Base de datos --------------------
    database_url: str = "sqlite:///./stock.db"
    db_echo: bool = False
    run_seeder: bool = False

# -------------------- Seguridad --------------------
    secret_key: str = Field(..., min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

# --------------------Stock --------------------
    stock_alert_threshold: int = 5

# -------------------- CORS --------------------
    cors_origins: str = "http://localhost:3000"

# -------------------- Rate limiting --------------------
    rate_limit_enabled: bool = True
    login_rate_limit: str = "5/minute"
    register_rate_limit: str = "2/minute"

# -------------------- Entorno --------------------
    environment: str = "production"

# --------------------Rutas de usuario --------------------
    users_data_dir: str = "./usuarios"

# -------------------- Propiedades derivadas --------------------
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
        user_path = self.users_root / username
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path

# -------------------- Validaciones --------------------
    @model_validator(mode='after')
    def validate_secret_key(self):
        if not self.secret_key or self.secret_key.strip() == "":
            raise ValueError(
                "SECRET_KEY no puede estar vacía. "
                "Genere una nueva con: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if self.secret_key == "F99NW4ztvIwuN1YDAEFKgMzYOQlhzuZn":
            raise ValueError(
                "SECRET_KEY no puede ser la del ejemplo. "
                "Genere una nueva con: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return self

    # --------------------
    @model_validator(mode='after')
    def validate_environment(self):
        if self.environment not in ["development", "production"]:
            raise ValueError("environment debe ser 'development' o 'production'")
        return self
    # --------------------
    @model_validator(mode='after')
    def ensure_directories(self):
        self.users_root.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        return self
    # --------------------
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()