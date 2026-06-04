"""
ÚLTIMA MODIFICACIÓN: 4/6/2025 por S4NDULOS
PROPÓSITO: Configuración de logging para toda la aplicación.
"""
import logging
import sys
from pathlib import Path
from app.core.config import settings

def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file = settings.logs_dir / "app.log"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )
    
    # Silenciar logs excesivos de bibliotecas
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger("desktop-stock")