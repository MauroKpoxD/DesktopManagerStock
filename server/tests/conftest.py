"""
Fixtures globales para pytest.
"""
import os
import sys
import pytest
import tempfile
import atexit

# ============================================================
# 1. Establecer variables de entorno ANTES de importar config
# ============================================================
os.environ["SECRET_KEY"] = os.getenv("SECRET_KEY", "test_secret_key_32chars_1234567890abcdef")

# Desactivar rate limiting
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["REGISTER_RATE_LIMIT"] = "1000/minute"
os.environ["LOGIN_RATE_LIMIT"] = "1000/minute"

# Credenciales PostgreSQL (no se usarán en pruebas, pero se requieren para config)
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "postgres"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "desktopmanager"

# ============================================================
# 2. Asegurar sys.path
# ============================================================
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# 3. Importar configuración y forzar valores
# ============================================================
from app.core.config import settings
settings.rate_limit_enabled = False
settings.register_rate_limit = "1000/minute"
settings.login_rate_limit = "1000/minute"

# ============================================================
# 4. Importar modelos ANTES de crear las tablas
#    Incluir RefreshTokenDB para que se cree la tabla
# ============================================================
from app.core.database import Base, get_db
from app.models.usuario import UsuarioDB
from app.models.producto import ProductoDB
from app.models.movimiento import MovimientoDB
from app.models.refresh_token import RefreshTokenDB

# ============================================================
# 5. Crear motor SQLite y sobrescribir el engine global
# ============================================================
import app.core.database as database
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
temp_db_path = temp_db_file.name
temp_db_file.close()

_test_engine = create_engine(f"sqlite:///{temp_db_path}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=_test_engine)  # Ahora crea todas las tablas, incluyendo refresh_tokens

# Sobrescribir el engine y SessionLocal
database.engine = _test_engine
database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# 6. Importar main y sobrescribir dependencia
# ============================================================
from main import app
from fastapi.testclient import TestClient

app.dependency_overrides[get_db] = override_get_db

def cleanup():
    _test_engine.dispose()
    os.unlink(temp_db_path)
atexit.register(cleanup)

# ============================================================
# 7. Fixtures
# ============================================================
@pytest.fixture(scope="function", autouse=True)
def clean_tables():
    with _test_engine.connect() as conn:
        # Desactivar restricciones FK usando text()
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            try:
                conn.execute(table.delete())
            except Exception:
                pass  # Si alguna tabla no existe, la ignoramos
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def test_user(db_session):
    from app.core.security import get_password_hash
    db_session.query(UsuarioDB).filter(UsuarioDB.username == "testuser").delete()
    db_session.commit()
    user = UsuarioDB(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        rol="editor",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def test_lector(db_session):
    from app.core.security import get_password_hash
    db_session.query(UsuarioDB).filter(UsuarioDB.username == "lector").delete()
    db_session.commit()
    user = UsuarioDB(
        username="lector",
        email="lector@example.com",
        hashed_password=get_password_hash("lectorpass"),
        rol="lector",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def lector_headers(test_lector):
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": test_lector.username})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def productos_demo(db_session):
    p1 = ProductoDB(nombre="Producto A", precio=100, stock=10, stock_minimo=5, stock_maximo=50)
    p2 = ProductoDB(nombre="Producto B", precio=200, stock=2, stock_minimo=5, stock_maximo=30)
    p3 = ProductoDB(nombre="Producto C", precio=150, stock=20, stock_minimo=10, stock_maximo=100)
    db_session.add_all([p1, p2, p3])
    db_session.commit()
    return [p1, p2, p3]

@pytest.fixture(scope="function")
def movimientos_demo(db_session, productos_demo, test_user):
    from app.services.movimiento_service import registrar_movimiento
    from app.schemas.movimiento import MovimientoBase
    usuario_id = test_user.id
    mov1 = MovimientoBase(
        producto_id=productos_demo[0].id,
        tipo="entrada",
        cantidad=5,
        stock_resultante=15,
        usuario_id=usuario_id
    )
    mov2 = MovimientoBase(
        producto_id=productos_demo[0].id,
        tipo="salida",
        cantidad=3,
        stock_resultante=12,
        usuario_id=usuario_id
    )
    mov3 = MovimientoBase(
        producto_id=productos_demo[1].id,
        tipo="salida",
        cantidad=1,
        stock_resultante=1,
        usuario_id=usuario_id
    )
    registrar_movimiento(db_session, mov1)
    registrar_movimiento(db_session, mov2)
    registrar_movimiento(db_session, mov3)
    db_session.commit()