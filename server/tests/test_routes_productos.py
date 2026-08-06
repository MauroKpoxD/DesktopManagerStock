"""
Tests para endpoints de productos.
"""
import pytest
from app.services.producto_service import crear_producto
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
    producto = crear_producto(db_session, ProductoCreate(nombre="Parlante", precio=80, stock=5))
    response = client.patch(f"/api/v1/productos/{producto.id}/stock?cantidad=3&tipo=entrada", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Stock actualizado. Nuevo stock: 8"
    db_session.commit()
    from app.services.producto_service import obtener_producto_por_id
    updated = obtener_producto_por_id(db_session, producto.id)
    assert updated.stock == 8

def test_rol_admin_required_for_delete(client, auth_headers, db_session, test_user):
    producto = crear_producto(db_session, ProductoCreate(nombre="Borrar", precio=1, stock=1))
    response = client.delete(f"/api/v1/productos/{producto.id}", headers=auth_headers)
    assert response.status_code == 403

def test_editor_can_update_producto(client, auth_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="EditorTest", precio=100, stock=5))
    payload = {"precio": 150}
    response = client.put(f"/api/v1/productos/{producto.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["precio"] == 150

def test_lector_cannot_create_producto(client, lector_headers, db_session):
    payload = {"nombre": "LectorCrear", "precio": 50, "stock": 3}
    response = client.post("/api/v1/productos", json=payload, headers=lector_headers)
    assert response.status_code == 403

def test_lector_cannot_update_producto(client, lector_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="LectorActualizar", precio=100, stock=2))
    response = client.put(f"/api/v1/productos/{producto.id}", json={"precio": 200}, headers=lector_headers)
    assert response.status_code == 403

def test_lector_cannot_delete_producto(client, lector_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="LectorBorrar", precio=100, stock=2))
    response = client.delete(f"/api/v1/productos/{producto.id}", headers=lector_headers)
    assert response.status_code == 403

def test_put_producto_no_modifica_stock(client, auth_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="StockFijo", precio=50, stock=10))
    payload = {"stock": 99}
    response = client.put(f"/api/v1/productos/{producto.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["stock"] == 10
    from app.services.producto_service import obtener_producto_por_id
    updated = obtener_producto_por_id(db_session, producto.id)
    assert updated.stock == 10

def test_get_productos_stock_bajo_endpoint(client, auth_headers, db_session):
    crear_producto(db_session, ProductoCreate(nombre="Bajo", precio=1, stock=2, stock_minimo=5))
    crear_producto(db_session, ProductoCreate(nombre="Normal", precio=1, stock=10, stock_minimo=5))
    response = client.get("/api/v1/productos/stock/bajo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Bajo"
    
    response_umbral = client.get("/api/v1/productos/stock/bajo?umbral=3", headers=auth_headers)
    assert response_umbral.status_code == 200
    assert len(response_umbral.json()) == 1

def test_crear_producto_con_categoria(client, auth_headers):
    payload = {"nombre": "Yerba", "precio": 5, "stock": 10, "categoria": "Almacén"}
    response = client.post("/api/v1/productos", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["categoria"] == "Almacén"

def test_filtrar_productos_por_categoria(client, auth_headers, db_session):
    crear_producto(db_session, ProductoCreate(nombre="Fideos", precio=2, stock=5, categoria="Almacén"))
    crear_producto(db_session, ProductoCreate(nombre="Detergente", precio=3, stock=5, categoria="Limpieza"))
    response = client.get("/api/v1/productos?categoria=Almacén", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Fideos"

def test_listar_categorias(client, auth_headers, db_session):
    crear_producto(db_session, ProductoCreate(nombre="Lavandina", precio=2, stock=5, categoria="Limpieza"))
    crear_producto(db_session, ProductoCreate(nombre="Arroz", precio=2, stock=5, categoria="Almacén"))
    crear_producto(db_session, ProductoCreate(nombre="SinCategoria", precio=2, stock=5))
    response = client.get("/api/v1/productos/categorias", headers=auth_headers)
    assert response.status_code == 200
    assert set(response.json()) == {"Limpieza", "Almacén"}

def test_crear_producto_con_sku_y_proveedor(client, auth_headers):
    payload = {
        "nombre": "Mouse Inalambrico",
        "precio": 15,
        "stock": 8,
        "sku": "MOU-001",
        "proveedor_nombre": "Distribuidora XYZ",
        "proveedor_contacto": "011-4444-5555",
    }
    response = client.post("/api/v1/productos", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "MOU-001"
    assert data["proveedor_nombre"] == "Distribuidora XYZ"
    assert data["proveedor_contacto"] == "011-4444-5555"

def test_importar_csv_requiere_rol(client, lector_headers):
    csv_contenido = "nombre,precio,stock\nTeclado,10,5\n"
    response = client.post(
        "/api/v1/productos/importar-csv",
        files={"archivo": ("productos.csv", csv_contenido, "text/csv")},
        headers=lector_headers,
    )
    assert response.status_code == 403

def test_importar_csv_crea_productos(client, auth_headers):
    csv_contenido = (
        "nombre,categoria,precio,stock,stock_minimo,stock_maximo\n"
        "Teclado,Electrónica,10,5,2,20\n"
        "Mouse,Electrónica,8,3,1,15\n"
    )
    response = client.post(
        "/api/v1/productos/importar-csv",
        files={"archivo": ("productos.csv", csv_contenido, "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["creados"] == 2
    assert data["total_filas"] == 2
    assert set(data["productos_creados"]) == {"Teclado", "Mouse"}
    assert data["omitidos"] == []

    response = client.get("/api/v1/productos?categoria=Electrónica", headers=auth_headers)
    assert len(response.json()) == 2

def test_importar_csv_omite_filas_invalidas_sin_abortar(client, auth_headers, productos_demo):
    nombre_existente = productos_demo[0].nombre
    csv_contenido = (
        f"nombre,precio,stock\n"
        f"{nombre_existente},10,5\n"  # duplicado, se omite
        f"ProductoValido,15,3\n"
        f",20,1\n"  # sin nombre, se omite
    )
    response = client.post(
        "/api/v1/productos/importar-csv",
        files={"archivo": ("productos.csv", csv_contenido, "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["creados"] == 1
    assert data["productos_creados"] == ["ProductoValido"]
    assert len(data["omitidos"]) == 2

def test_importar_csv_rechaza_archivo_no_csv(client, auth_headers):
    response = client.post(
        "/api/v1/productos/importar-csv",
        files={"archivo": ("productos.txt", "nombre,precio,stock\nX,1,1\n", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 400