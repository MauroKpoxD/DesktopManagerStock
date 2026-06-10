"""
ÚLTIMA MODIFICACIÓN: 9/6/2025 por S4NDULOS
PROPÓSITO: Configura la conexión a la base de datos (SQLite por defecto),
           crea el motor, las sesiones, y provee la dependencia get_db
           También incluye un seeder inicial (init_db) con datos por defecto
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker   
from app.core.config import settings
import secrets
import string
import logging

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
    echo=settings.db_echo,  
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base()   

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
    from app.core.roles import Rol
    
    db = SessionLocal()
    admin = db.query(UsuarioDB).filter(UsuarioDB.username == "admin").first()
    if not admin:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        default_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        admin_user = UsuarioDB(
            username="admin",
            email="s4ndulos@help.com",
            hashed_password=get_password_hash(default_password),
            rol=Rol.ADMIN.value,
            activo=True
        )
        db.add(admin_user)
        db.commit()

        # --------------------------
        if settings.environment == "development":
            logging.warning(f"Usuario 'admin' creado con contraseña: '{default_password}'")
        else:
            password_file = settings.logs_dir / ".admin_password.txt"
            password_file.write_text(f"admin:{default_password}")
            logging.warning(f"Usuario 'admin' creado. Contraseña guardada en {password_file}")
    db.close()