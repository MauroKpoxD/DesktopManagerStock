"""
Configuración de la aplicación vía variables de entorno.
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator, Field
from pathlib import Path

class Settings(BaseSettings):
    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = True
    api_version: str = "0.3.2"

    # Base de datos - PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"    
    db_name: str = "desktopmanager"    
    db_echo: bool = False
    run_seeder: bool = False

    @property
    def database_url(self) -> str:
        """Construye la URL de conexión sin caracteres no ASCII."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Seguridad
    secret_key: str = Field(..., min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
<<<<<<< HEAD
=======
    # Antes se usaba una constante fija de 7 días en refresh_token_service.py,
    # ignorando esta variable pese a que ya existía en .env.example.
    refresh_token_expire_days: int = 7
>>>>>>> feature/interfaz-y-reconstruccion

    # Stock
    stock_alert_threshold: int = 5

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Rate limiting
    rate_limit_enabled: bool = True
    login_rate_limit: str = "5/minute"
    register_rate_limit: str = "2/minute"

    # Entorno
    environment: str = "production"

    # Rutas de usuario
    users_data_dir: str = "./usuarios"

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

    @model_validator(mode='after')
    def validate_environment(self):
        if self.environment not in ["development", "production"]:
            raise ValueError("environment debe ser 'development' o 'production'")
        return self

    @model_validator(mode='after')
<<<<<<< HEAD
=======
    def validate_cors(self):
        # Con allow_credentials=True (ver main.py), los navegadores rechazan
        # el origen comodín "*". Falla rápido en el arranque en vez de dejar
        # que el frontend reciba errores de CORS difíciles de diagnosticar.
        origenes = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if "*" in origenes:
            raise ValueError(
                "CORS_ORIGINS no puede ser '*' porque la API usa allow_credentials=True "
                "(los navegadores bloquean esa combinación). Especifique orígenes concretos, "
                "separados por comas."
            )
        return self

    @model_validator(mode='after')
>>>>>>> feature/interfaz-y-reconstruccion
    def ensure_directories(self):
        self.users_root.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        return self

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()