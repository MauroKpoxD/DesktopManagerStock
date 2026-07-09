"""
Configuración centralizada de logging.
"""
import logging
import sys
from pathlib import Path
from app.core.config import settings

def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado para el módulo."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        log_file = settings.logs_dir / "app.log"
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)
        # Silenciar bibliotecas
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    return logger