"""
Tests para el servicio de productos.
"""
import pytest
from pydantic import ValidationError as PydanticValidationError  # <-- Importar la de Pydantic
from app.services.producto_service import (
    crear_producto,
    listar_productos,
    obtener_producto_por_id,
    actualizar_producto,
    eliminar_producto,
    ajustar_stock,
    obtener_productos_con_stock_bajo
)
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.models.usuario import UsuarioDB
from app.core.security import get_password_hash
from app.core.exceptions import ConflictError, ValidationError  # Nuestra excepción personalizada

def test_crear_producto(db_session):
    producto_data = ProductoCreate(nombre="Laptop", precio=670000.50, stock=10, stock_minimo=2, stock_maximo=50)
    producto = crear_producto(db_session, producto_data)
    assert producto.id is not None
    assert producto.nombre == "Laptop"
    assert producto.precio == 670000.50
    assert producto.stock == 10

def test_crear_producto_duplicado(db_session):
    producto1 = ProductoCreate(nombre="Monitor", precio=67000, stock=5)
    crear_producto(db_session, producto1)
    with pytest.raises(ConflictError, match="Ya existe un producto con el nombre 'Monitor'"):
        crear_producto(db_session, producto1)

def test_ajustar_stock(db_session):
    user = UsuarioDB(
        username="testuser_ajuste",
        email="testajuste@example.com",
        hashed_password=get_password_hash("testpass"),
        rol="admin",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    producto = crear_producto(db_session, ProductoCreate(nombre="Mouse", precio=25, stock=5))
    ajustar_stock(db_session, producto.id, 3, es_entrada=True, usuario_id=user.id)
    updated = obtener_producto_por_id(db_session, producto.id)
    assert updated.stock == 8
    ajustar_stock(db_session, producto.id, 2, es_entrada=False, usuario_id=user.id)
    updated = obtener_producto_por_id(db_session, producto.id)
    assert updated.stock == 6
    with pytest.raises(ValidationError, match="Stock insuficiente"):
        ajustar_stock(db_session, producto.id, 10, es_entrada=False, usuario_id=user.id)

def test_obtener_productos_stock_bajo(db_session):
    crear_producto(db_session, ProductoCreate(nombre="A", precio=1, stock=2, stock_minimo=5))
    crear_producto(db_session, ProductoCreate(nombre="B", precio=1, stock=10, stock_minimo=5))
    crear_producto(db_session, ProductoCreate(nombre="C", precio=1, stock=5, stock_minimo=3))

    bajos = obtener_productos_con_stock_bajo(db_session)
    assert len(bajos) == 1
    assert bajos[0].nombre == "A"

    bajos_umbral = obtener_productos_con_stock_bajo(db_session, umbral=4)
    assert len(bajos_umbral) == 1

def test_crear_producto_stock_maximo_menor_que_minimo(db_session):
    # Esta validación ocurre en el schema de Pydantic, no en el servicio.
    with pytest.raises(PydanticValidationError, match="El stock máximo debe ser mayor o igual al mínimo"):
        crear_producto(db_session, ProductoCreate(nombre="Invalido", precio=10, stock=5, stock_minimo=10, stock_maximo=5))

def test_crear_producto_stock_inicial_supera_maximo(db_session):
    # Esta validación ocurre en el schema de Pydantic.
    with pytest.raises(PydanticValidationError, match="El stock inicial no puede superar el máximo de 100"):
        crear_producto(db_session, ProductoCreate(nombre="ExcedeMax", precio=10, stock=150, stock_maximo=100))