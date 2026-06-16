"""
ÚLTIMA MODIFICACIÓN: 12/6/2025 por S4NDULOS
PROPÓSITO: Fixtures globales para pytest.
"""

import os
import sys
import pytest
import tempfile
import atexit

# Asegurar que el directorio padre (raíz del backend) esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Desactivar rate limiting por completo
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["REGISTER_RATE_LIMIT"] = "1000/minute"
os.environ["LOGIN_RATE_LIMIT"] = "1000/minute"

# Importar configuración después de establecer variables
from app.core.config import settings
settings.rate_limit_enabled = False
settings.register_rate_limit = "1000/minute"
settings.login_rate_limit = "1000/minute"

# Ahora importar el resto
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
import app.core.database as database
from main import app
from app.core.security import create_access_token, get_password_hash
from app.models.usuario import UsuarioDB
from app.models.producto import ProductoDB

# Base de datos temporal
temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
temp_db_path = temp_db_file.name
temp_db_file.close()

_test_engine = create_engine(f"sqlite:///{temp_db_path}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=_test_engine)
database.engine = _test_engine

def cleanup():
    _test_engine.dispose()
    os.unlink(temp_db_path)
atexit.register(cleanup)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------
@pytest.fixture(scope="function", autouse=True)
def clean_tables():
    with _test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
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
    access_token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def test_lector(db_session):
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