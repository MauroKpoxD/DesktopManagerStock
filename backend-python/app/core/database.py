"""
Configuracion de la base de datos y funciones de inicializacion (Seeders)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# -------------------------------------------------------------------
# Configuracion del motor segun el tipo de DB 
# -------------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = settings.database_url # usar la URL de los .env

connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=getattr(settings, "db_echo", False), # VARIABLE EN .ENV
    pool_size=5,                             # solo para otras base de datos como mysqlazo
    max_overflow=10,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base()

def get_db():
    """Dependencias para obtener sesion de BD (se cierra automaticamente)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
# SEEDER: Datos iniciales para desarrollo / primer uso 
# -------------------------------------------------------------------

def init_db():
    """
    Crea las tablas dsi no existen e inserta datos por defecto
    - Usuario administrador (atlas/software_2026_123)
    - Productos de ejemplo
    Solo se ejecuta una vez al iniciar la app
    """

    # importacion de usuarios, producto y hash para evitar circular imports
    from app.models.usuario import UsuarioDB
    from app.models.producto import ProductoDB
    from app.core.security import get_password_hash

    # CREAR TABLAS SI NO EXISTEN
    Base.metadata.create_all(bind=engine)
    
    # CREAR SESION
    db = SessionLocal()

    """
    al proximo desarrollador porfavor seguir con la creacion de datos
    """

    # guardar y cerrar
    db.commit()
    db.close()