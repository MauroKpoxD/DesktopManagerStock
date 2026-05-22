from fastapi import FastAPI
from app.api.routes import router
from app.core.database import engine, Base
from app.core.config import settings

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Instancia de FastAPI con versión dinámica
app = FastAPI(
    title="DesktopManagerStock API",
    version=settings.api_version,   # importar version desde la variable de entorno
    description="Sistema de gestión de inventario y stock"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,    # ip de la api
        port=settings.api_port,    # entero
        reload=settings.api_reload # bool
    )