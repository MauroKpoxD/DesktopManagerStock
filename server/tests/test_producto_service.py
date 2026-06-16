"""
ULTIMA MODIFICACION HECHA POR S4NDULOS 8/6/2025
CREACION DE PRODUCTOS Y TODAS LAS CONSULTAS DE GET/UPDATE/DELETE STOCK
ACTUALIZADO: se agrega creación de usuario para probar ajuste de stock con movimiento
"""

import pytest
from app.services.producto_service import (
    create_producto,
    get_all_productos,
    get_producto_by_id,
    update_producto,
    delete_producto,
    ajustar_stock,
    get_productos_stock_bajo
)
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.models.usuario import UsuarioDB
from app.core.security import get_password_hash

def test_create_producto(db_session):
    producto_data = ProductoCreate(nombre="Laptop", precio=670000.50, stock=10, stock_minimo=2, stock_maximo=50)
    producto = create_producto(db_session, producto_data)
    assert producto.id is not None
    assert producto.nombre == "Laptop"
    assert producto.precio == 670000.50
    assert producto.stock == 10

def test_create_producto_duplicate_name(db_session):
    producto1 = ProductoCreate(nombre="Monitor", precio=67000, stock=5)
    create_producto(db_session, producto1)
    with pytest.raises(ValueError, match="Ya existe un producto con ese nombre"):
        create_producto(db_session, producto1)

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
    
    producto = create_producto(db_session, ProductoCreate(nombre="Mouse", precio=25, stock=5))
    ajustar_stock(db_session, producto.id, 3, es_entrada=True, usuario_id=user.id)
    updated = get_producto_by_id(db_session, producto.id)
    assert updated.stock == 8
    ajustar_stock(db_session, producto.id, 2, es_entrada=False, usuario_id=user.id)
    updated = get_producto_by_id(db_session, producto.id)
    assert updated.stock == 6
    with pytest.raises(ValueError, match="Stock insuficiente"):
        ajustar_stock(db_session, producto.id, 10, es_entrada=False, usuario_id=user.id)

def test_get_productos_stock_bajo(db_session):
    create_producto(db_session, ProductoCreate(nombre="A", precio=1, stock=2, stock_minimo=5))
    create_producto(db_session, ProductoCreate(nombre="B", precio=1, stock=10, stock_minimo=5))
    create_producto(db_session, ProductoCreate(nombre="C", precio=1, stock=5, stock_minimo=3))

    bajos = get_productos_stock_bajo(db_session)
    assert len(bajos) == 1
    assert bajos[0].nombre == "A"

    bajos_umbral = get_productos_stock_bajo(db_session, umbral=4)
    assert len(bajos_umbral) == 1

# -------------------- NUEVOS TESTS --------------------

def test_create_producto_stock_maximo_menor_que_minimo(db_session):
    with pytest.raises(ValueError, match="El stock máximo debe ser mayor o igual al mínimo"):
        create_producto(db_session, ProductoCreate(nombre="Invalido", precio=10, stock=5, stock_minimo=10, stock_maximo=5))

def test_create_producto_stock_inicial_supera_maximo(db_session):
    with pytest.raises(ValueError, match="no puede superar el máximo"):
        create_producto(db_session, ProductoCreate(nombre="ExcedeMax", precio=10, stock=150, stock_maximo=100))