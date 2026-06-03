"""
ÚLTIMA MODIFICACIÓN: 28/5/2025 por S4NDULOS
PROPÓSITO: Configura la conexión a la base de datos (SQLite por defecto),
           crea el motor, las sesiones, y provee la dependencia get_db
           También incluye un seeder inicial (init_db) con datos por defecto
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker   # ← importación corregida
from app.core.config import settings

# -------------------------------------------------------------------
# Configuracion del motor segun el tipo de DB 
# -------------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = settings.database_url

connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=settings.db_echo,   # ← ahora sí existe en settings
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base()   # ← nueva forma (ya no desde sqlalchemy.ext.declarative)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
# SEEDER: Datos iniciales para desarrollo / primer uso 
# -------------------------------------------------------------------

def init_db():
    from app.models.usuario import UsuarioDB
    from app.core.security import get_password_hash
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin = db.query(UsuarioDB).filter(UsuarioDB.username == "admin").first()
    if not admin:
        admin_user = UsuarioDB(
            username="admin",
            email="admin@stock.com",
            hashed_password=get_password_hash("admin123"),
            rol="admin",
            activo=True
        )
        db.add(admin_user)
        db.commit()
    db.close()