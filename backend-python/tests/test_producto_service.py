"""
ULTIMA MODIFICACION HECHA POR S4NDULOS 30/5/2025
CREACION DE PRODUCTOS Y TODAS LAS CONSULTAS DE GET/UPDATE/DELETE STOCK
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
    producto = create_producto(db_session, ProductoCreate(nombre="Mouse", precio=25, stock=5))
    ajustar_stock(db_session, producto.id, 3, es_entrada=True)
    updated = get_producto_by_id(db_session, producto.id)
    assert updated.stock == 8
    ajustar_stock(db_session, producto.id, 2, es_entrada=False)
    updated = get_producto_by_id(db_session, producto.id)
    assert updated.stock == 6
    with pytest.raises(ValueError, match="Stock insuficiente"):
        ajustar_stock(db_session, producto.id, 10, es_entrada=False)

def test_get_productos_stock_bajo(db_session):
    create_producto(db_session, ProductoCreate(nombre="A", precio=1, stock=2, stock_minimo=5))
    create_producto(db_session, ProductoCreate(nombre="B", precio=1, stock=10, stock_minimo=5))
    # Cambiamos stock de C a 5 para que no sea bajo (stock_minimo=3 -> 5 > 3)
    create_producto(db_session, ProductoCreate(nombre="C", precio=1, stock=5, stock_minimo=3))

    bajos = get_productos_stock_bajo(db_session)
    assert len(bajos) == 1
    assert bajos[0].nombre == "A"

    bajos_umbral = get_productos_stock_bajo(db_session, umbral=4)
    # Ahora solo A (2 <=4) y quizás C? C stock=5 no, solo A
    assert len(bajos_umbral) == 1