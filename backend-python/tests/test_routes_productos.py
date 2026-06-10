"""
ULTIMA MODIFICACION HECHA POR S4NDULOS 9/6/2025
TEST PARA USUARIOS Y ENDPOINTS DE PRODUCTOS
"""

import pytest
from app.services.producto_service import create_producto
from app.schemas.producto import ProductoCreate

def test_get_productos_empty(client, auth_headers):
    response = client.get("/api/v1/productos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_producto_authorized(client, auth_headers, db_session):
    payload = {
        "nombre": "Teclado",
        "precio": 123.67,
        "stock": 20,
        "stock_minimo": 3,
        "stock_maximo": 100
    }
    response = client.post("/api/v1/productos", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Teclado"
    assert data["precio"] == 123.67

def test_create_producto_unauthorized(client, db_session, test_user):
    response = client.post("/api/v1/productos", json={"nombre": "X", "precio": 10, "stock": 1})
    assert response.status_code == 401

def test_ajustar_stock(client, auth_headers, db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="Parlante", precio=80, stock=5))
    response = client.patch(f"/api/v1/productos/{producto.id}/stock?cantidad=3&tipo=entrada", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Stock actualizado. Nuevo stock: 8"
    db_session.commit()
    from app.services.producto_service import get_producto_by_id
    updated = get_producto_by_id(db_session, producto.id)
    assert updated.stock == 8

def test_rol_admin_required_for_delete(client, auth_headers, db_session, test_user):
    producto = create_producto(db_session, ProductoCreate(nombre="Borrar", precio=1, stock=1))
    response = client.delete(f"/api/v1/productos/{producto.id}", headers=auth_headers)
    assert response.status_code == 403

# -------------------- NUEVOS TESTS --------------------

def test_editor_can_update_producto(client, auth_headers, db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="EditorTest", precio=100, stock=5))
    payload = {"precio": 150}
    response = client.put(f"/api/v1/productos/{producto.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["precio"] == 150

def test_lector_cannot_create_producto(client, lector_headers, db_session):
    payload = {"nombre": "LectorCrear", "precio": 50, "stock": 3}
    response = client.post("/api/v1/productos", json=payload, headers=lector_headers)
    assert response.status_code == 403

def test_lector_cannot_update_producto(client, lector_headers, db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="LectorActualizar", precio=100, stock=2))
    response = client.put(f"/api/v1/productos/{producto.id}", json={"precio": 200}, headers=lector_headers)
    assert response.status_code == 403

def test_lector_cannot_delete_producto(client, lector_headers, db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="LectorBorrar", precio=100, stock=2))
    response = client.delete(f"/api/v1/productos/{producto.id}", headers=lector_headers)
    assert response.status_code == 403

def test_put_producto_no_modifica_stock(client, auth_headers, db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="StockFijo", precio=50, stock=10))
    payload = {"stock": 99}
    response = client.put(f"/api/v1/productos/{producto.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["stock"] == 10
    from app.services.producto_service import get_producto_by_id
    updated = get_producto_by_id(db_session, producto.id)
    assert updated.stock == 10

def test_get_productos_stock_bajo_endpoint(client, auth_headers, db_session):
    create_producto(db_session, ProductoCreate(nombre="Bajo", precio=1, stock=2, stock_minimo=5))
    create_producto(db_session, ProductoCreate(nombre="Normal", precio=1, stock=10, stock_minimo=5))
    response = client.get("/api/v1/productos/stock/bajo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Bajo"
    
    response_umbral = client.get("/api/v1/productos/stock/bajo?umbral=3", headers=auth_headers)
    assert response_umbral.status_code == 200
    assert len(response_umbral.json()) == 1