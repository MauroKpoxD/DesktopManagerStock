"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Punto de entrada de la API. Crea la app FastAPI,
           inicializa la base de datos (tablas y seeder) mediante lifespan,
           e incluye los routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.core.database import engine, Base, init_db
from app.core.config import settings

# Importar los modelos para que SQLAlchemy los detecte
from app.models.producto import ProductoDB
from app.models.usuario import UsuarioDB

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crear tablas y ejecutar seeder
    Base.metadata.create_all(bind=engine)
    init_db()
    yield
    # Shutdown: aquí se pueden cerrar recursos si es necesario
    # (por ejemplo, engine.dispose() si se usa conexión asíncrona para mas adelante...)

app = FastAPI(
    title="DesktopManagerStock API",
    version=settings.api_version,
    description="Sistema de gestión de inventario y stock",
    lifespan=lifespan
)

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