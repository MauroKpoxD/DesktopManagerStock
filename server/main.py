"""
Punto de entrada de la API.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.api.reportes_routes import router as reportes_router
from app.api.usuarios_routes import router as usuarios_router
from app.core.database import engine, Base, init_db, get_db
from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.rate_limiter import limiter
from app.core.exceptions import (
    AppException,
    NotFoundError,
    ValidationError,
    ConflictError,
    BusinessError,
    AuthenticationError,
    AuthorizationError,
)

# Importar modelos para que SQLAlchemy los detecte
from app.models.refresh_token import RefreshTokenDB
from app.models.producto import ProductoDB
from app.models.usuario import UsuarioDB
from app.models.movimiento import MovimientoDB

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    init_db()
    if settings.run_seeder:
        logger.info("Seeder adicional activado (run_seeder=True)")
    yield

app = FastAPI(
    title="DesktopManagerStock API",
    version=settings.api_version,
    description="Sistema de gestión de inventario y stock",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    openapi_url="/openapi.json" if settings.environment == "development" else None,
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

# Rate limiting
if settings.rate_limit_enabled:
    app.state.limiter = limiter._limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting activado")
else:
    logger.info("Rate limiting desactivado")

# Manejo global de excepciones de dominio
#
# Antes, cada endpoint envolvía manualmente las llamadas a los servicios en
# try/except para traducir excepciones de negocio (NotFoundError, ValidationError,
# etc.) a HTTPException. Eso es repetitivo y frágil: si un desarrollador agrega
# un endpoint nuevo y olvida el try/except, la excepción se convierte en un 500
# sin detalle útil para el cliente. Centralizarlo aquí evita ese problema y
# mantiene los mismos códigos de estado que ya usaba la app.
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(BusinessError)
async def business_handler(request: Request, exc: BusinessError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(AuthenticationError)
async def authentication_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})

@app.exception_handler(AuthorizationError)
async def authorization_handler(request: Request, exc: AuthorizationError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    # Red de seguridad para cualquier subclase de AppException no mapeada arriba.
    logger.warning(f"AppException no mapeada explícitamente: {type(exc).__name__}: {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})

# Routers
app.include_router(router)
app.include_router(auth_router)
app.include_router(reportes_router)
app.include_router(usuarios_router)

@app.get("/api/v1/health", tags=["health"])
def health_check():
    """
    Healthcheck real: además de confirmar que el proceso responde, verifica
    que puede hablar con la base de datos. Antes el healthcheck de Docker
    apuntaba a '/api/v1/' (la ruta de bienvenida), que responde 200 aunque
    la base de datos esté caída, dando una falsa sensación de salud.
    """
    from sqlalchemy import text
    db_status = "ok"
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Healthcheck: fallo la conexión a la base de datos: {e}")
        db_status = "error"
    finally:
        try:
            db.close()
        except Exception:
            pass
    payload = {"status": "ok" if db_status == "ok" else "degraded", "database": db_status, "version": settings.api_version}
    return JSONResponse(status_code=200 if db_status == "ok" else 503, content=payload)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )