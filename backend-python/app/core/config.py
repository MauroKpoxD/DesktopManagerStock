from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    ### API Conf. ###
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = True
    api_version: str = "0.1.1"

    ### Database URL ###
    database_url: str = "sqlite:///./stock.db"

    ### Security ###
    secret_key: str = "mikabezonatrolita"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    ### Stock ALERT ###
    stock_alert_threshold: int = 5

    ### Propiedades de rutas ###
    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    ### REPORT DIR ###
    @property
    def reports_dir(self) -> Path:
        return self.base_dir / "reports"

    ### LOGS DIR ###
    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"

    ### carpeta de configuracion de variables de entorno ###
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False   # esta func permite API_VERSION = api_version

settings = Settings()