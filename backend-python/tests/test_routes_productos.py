"""
ULTIMA MODIFICACION HECHA POR S4NDULOS 30/5/2025
TEST PARA USUARIOS 
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
    db_session.commit()  # Forzar que la sesión vea los cambios de otras conexiones
    from app.services.producto_service import get_producto_by_id
    updated = get_producto_by_id(db_session, producto.id)
    assert updated.stock == 8

def test_rol_admin_required_for_delete(client, auth_headers, db_session, test_user):
    producto = create_producto(db_session, ProductoCreate(nombre="Borrar", precio=1, stock=1))
    response = client.delete(f"/api/v1/productos/{producto.id}", headers=auth_headers)
    assert response.status_code == 403