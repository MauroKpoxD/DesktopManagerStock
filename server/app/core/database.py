"""
Configuración de base de datos y seeder inicial.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import secrets
import string
from app.core.logging_config import get_logger

logger = get_logger(__name__)
SQLALCHEMY_DATABASE_URL = settings.database_url

# Configuración de pool para PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.db_echo,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Crea el usuario admin si no existe y ejecuta el seeder opcional."""
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

        # Guardar contraseña solo si no existe el archivo
        password_file = settings.logs_dir / ".admin_password.txt"
        if not password_file.exists():
            password_file.write_text(f"admin:{default_password}")

        if settings.environment == "development":
            logger.warning(f"Usuario 'admin' creado con contraseña: '{default_password}'")
        else:
            logger.warning(f"Usuario 'admin' creado. Contraseña guardada en {password_file}")

    if settings.run_seeder:
        logger.info("Seeder adicional activado - no hay datos demo implementados aún")

    # Limpiar tokens expirados al inicio
    from app.services.refresh_token_service import limpiar_tokens_expirados
    limpiar_tokens_expirados(db)

    db.close()