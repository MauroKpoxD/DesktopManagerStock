"""
ÚLTIMA MODIFICACIÓN: 4/6/2025 por S4NDULOS
PROPÓSITO: Punto de entrada de la API. Crea la app FastAPI,
           inicializa la base de datos (tablas y seeder condicional) mediante lifespan,
           e incluye los routers. Añade CORS y rate limiting condicional.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.core.database import engine, Base, init_db
from app.core.config import settings
from app.core.logging_config import setup_logging

# Importar los modelos para que SQLAlchemy los detecte
from app.models.producto import ProductoDB
from app.models.usuario import UsuarioDB
from app.models.movimiento import MovimientoDB

# Configurar logging
logger = setup_logging()

# Rate limiter (se crea pero solo se activa si está habilitado en configuración)
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.run_seeder:
        logger.info("Ejecutando seeder de base de datos (RUN_SEEDER=true)")
        init_db()
    else:
        logger.info("Seeder deshabilitado (RUN_SEEDER=false)")
    yield

app = FastAPI(
    title="DesktopManagerStock API",
    version=settings.api_version,
    description="Sistema de gestión de inventario y stock",
    lifespan=lifespan
)

# CORS
allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting condicional
if settings.rate_limit_enabled:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting activado")
else:
    logger.info("Rate limiting desactivado")

# Incluir routers
app.include_router(router)
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )