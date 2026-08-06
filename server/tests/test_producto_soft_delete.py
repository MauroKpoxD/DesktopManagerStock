"""
Tests del comportamiento de soft-delete en productos.

Antes, eliminar un producto lo borraba físicamente y, por el ondelete=CASCADE
en movimientos.producto_id, se llevaba puesto todo su historial. Estos tests
verifican que ahora "eliminar" solo desactiva el producto y conserva sus
movimientos.
"""
from app.services.producto_service import crear_producto, ajustar_stock
from app.schemas.producto import ProductoCreate


def test_eliminar_producto_es_soft_delete(client, auth_headers, admin_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="Cable HDMI", precio=10, stock=5))
    db_session.commit()

    response = client.delete(f"/api/v1/productos/{producto.id}", headers=admin_headers)
    assert response.status_code == 204

    # Ya no aparece en el listado por defecto...
    response = client.get("/api/v1/productos", headers=auth_headers)
    assert all(p["nombre"] != "Cable HDMI" for p in response.json())

    # ...pero sigue existiendo (soft delete) y puede consultarse por ID.
    response = client.get(f"/api/v1/productos/{producto.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["activo"] is False

    # Y aparece si se piden explícitamente los inactivos.
    response = client.get("/api/v1/productos?incluir_inactivos=true", headers=auth_headers)
    assert any(p["nombre"] == "Cable HDMI" for p in response.json())


def test_eliminar_producto_conserva_historial_de_movimientos(client, auth_headers, admin_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="Mouse Gamer", precio=50, stock=5))
    db_session.commit()
    from app.core.security import get_password_hash
    from app.models.usuario import UsuarioDB
    user = db_session.query(UsuarioDB).filter(UsuarioDB.username == "testuser").first()
    ajustar_stock(db_session, producto.id, 3, es_entrada=True, usuario_id=user.id)
    db_session.commit()

    response = client.delete(f"/api/v1/productos/{producto.id}", headers=admin_headers)
    assert response.status_code == 204

    response = client.get(f"/api/v1/movimientos?producto_id={producto.id}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_no_se_puede_ajustar_stock_de_producto_inactivo(client, auth_headers, admin_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="Webcam", precio=30, stock=5))
    db_session.commit()
    client.delete(f"/api/v1/productos/{producto.id}", headers=admin_headers)

    response = client.patch(f"/api/v1/productos/{producto.id}/stock?cantidad=1&tipo=entrada", headers=auth_headers)
    assert response.status_code == 400


def test_reactivar_producto(client, auth_headers, admin_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="Auriculares", precio=20, stock=5))
    db_session.commit()
    client.delete(f"/api/v1/productos/{producto.id}", headers=admin_headers)

    response = client.patch(f"/api/v1/productos/{producto.id}/reactivar", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["activo"] is True

    response = client.get("/api/v1/productos", headers=auth_headers)
    assert any(p["nombre"] == "Auriculares" for p in response.json())


def test_reactivar_requiere_admin(client, auth_headers, db_session):
    producto = crear_producto(db_session, ProductoCreate(nombre="Alfombrilla", precio=5, stock=5))
    db_session.commit()
    response = client.patch(f"/api/v1/productos/{producto.id}/reactivar", headers=auth_headers)
    assert response.status_code == 403


def test_total_count_header_en_listado_de_productos(client, auth_headers, productos_demo):
    response = client.get("/api/v1/productos", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["X-Total-Count"] == str(len(productos_demo))


def test_editor_no_puede_cambiar_activo_via_put(client, auth_headers, db_session):
    """auth_headers pertenece a un usuario con rol 'editor' (ver conftest.py)."""
    producto = crear_producto(db_session, ProductoCreate(nombre="Teclado Mecanico", precio=40, stock=5))
    db_session.commit()
    response = client.put(f"/api/v1/productos/{producto.id}", json={"activo": False}, headers=auth_headers)
    assert response.status_code == 400
