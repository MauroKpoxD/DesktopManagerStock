"""
Configuración de base de datos y seeder inicial.
"""
import os
from sqlalchemy import create_engine, inspect, text
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

def ensure_schema_compat():
    inspector = inspect(engine)
    if "productos" not in inspector.get_table_names():
        return  # Tabla nueva, create_all ya la crea completa.

    columnas = {col["name"] for col in inspector.get_columns("productos")}
    if "activo" not in columnas:
        logger.warning("Migración ligera: agregando columna 'activo' a 'productos'")
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE productos ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE"))
    if "categoria" not in columnas:
        logger.warning("Migración ligera: agregando columna 'categoria' a 'productos'")
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE productos ADD COLUMN categoria VARCHAR NULL"))
    for columna in ("sku", "proveedor_nombre", "proveedor_contacto"):
        if columna not in columnas:
            logger.warning(f"Migración ligera: agregando columna '{columna}' a 'productos'")
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE productos ADD COLUMN {columna} VARCHAR NULL"))

def init_db():
    """Crea el usuario admin si no existe y ejecuta el seeder opcional."""
    from app.models.usuario import UsuarioDB
    from app.core.security import get_password_hash
    from app.core.roles import Rol

    ensure_schema_compat()

    db = SessionLocal()
    admin = db.query(UsuarioDB).filter(UsuarioDB.username == "admin").first()
    if not admin:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        default_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        admin_user = UsuarioDB(
            username="admin",
            email="admin@admin.com",
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
            try:
                # La contraseña queda en texto plano en disco: al menos
                # restringimos el archivo a que solo el dueño pueda leerlo.
                # Antes se creaba con los permisos por defecto del proceso,
                # que en muchos sistemas también son legibles por el grupo.
                os.chmod(password_file, 0o600)
            except OSError:
                pass  # En Windows chmod no aplica de la misma forma; no es crítico.

        if settings.environment == "development":
            logger.warning(f"Usuario 'admin' creado con contraseña: '{default_password}'")
        else:
            logger.warning(
                f"Usuario 'admin' creado. Contraseña guardada en {password_file}. "
                "Cámbiala cuanto antes con POST /api/v1/auth/me/password e idealmente borra ese archivo después."
            )

    if settings.run_seeder:
        logger.info("Seeder adicional activado - no hay datos demo implementados aún")

    # Limpiar tokens expirados al inicio
    from app.services.refresh_token_service import limpiar_tokens_expirados
    limpiar_tokens_expirados(db)

    db.close()