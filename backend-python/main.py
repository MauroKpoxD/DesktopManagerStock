"""
PUNTO DE ENTRADA PRINCIPAL DE LA API
Este archivo se ejecuta para levantar el servidor FastAPI.
Configura la base de datos, importa las rutas y arranca el servidor.
"""



from fastapi import FastAPI
from app.api.routes import router
from app.api.auth_routes import router as auth_router  
from app.core.database import engine, Base
from app.core.config import settings

# Importar los modelos para que SQLAlchemy los detecte y cree las tablas
from app.models.producto import ProductoDB     
from app.models.usuario import UsuarioDB      

# Crear tablas en la base de datos (incluye productos y usuarios)
# Si no existen, las crea; si ya existen, no las modifica.
Base.metadata.create_all(bind=engine)

# Instancia de FastAPI (configuración básica)
app = FastAPI(
    title="DesktopManagerStock API",                     # titulo que se ve en /docs
    version=settings.api_version,                        # versión desde .env
    description="Sistema de gestión de inventario y stock"
)

# Incluir los routers (grupos de endpoints)
app.include_router(router)          # endpoints de productos (/api/v1/productos)
app.include_router(auth_router)     # endpoints de autenticación (/api/v1/auth/...)

# Punto de inicio cuando se ejecuta este script directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",                  # archivo:variable_app
        host=settings.api_host,      # dirección IP (del .env)
        port=settings.api_port,      # puerto (del .env)
        reload=settings.api_reload   # modo recarga automática (True/False)
    )