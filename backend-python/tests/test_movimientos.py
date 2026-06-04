"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Tests para el servicio y endpoints de movimientos de stock
"""

import pytest
from app.services.movimiento_service import (
    registrar_movimiento,
    get_movimiento_by_id,
    get_movimientos,
    get_movimientos_por_rango_ids
)
from app.schemas.movimiento import MovimientoBase
from app.services.producto_service import create_producto, ajustar_stock
from app.schemas.producto import ProductoCreate
from app.models.usuario import UsuarioDB
from app.core.security import get_password_hash

# ------------------------------------------------------------------------------
# TESTS DEL SERVICIO DE MOVIMIENTOS
# ------------------------------------------------------------------------------

def test_registrar_movimiento(db_session):
    # Crear producto y usuario de prueba
    producto = create_producto(db_session, ProductoCreate(nombre="ProdMov", precio=10, stock=5))
    user = UsuarioDB(
        username="movuser",
        email="mov@test.com",
        hashed_password=get_password_hash("pass"),
        rol="editor",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    movimiento_data = MovimientoBase(
        producto_id=producto.id,
        tipo="entrada",
        cantidad=3,
        stock_resultante=8,
        usuario_id=user.id
    )
    mov = registrar_movimiento(db_session, movimiento_data)
    assert mov.id is not None
    assert mov.producto_id == producto.id
    assert mov.tipo == "entrada"
    assert mov.cantidad == 3
    assert mov.stock_resultante == 8
    assert mov.usuario_id == user.id
    assert mov.fecha_hora is not None

def test_get_movimiento_by_id(db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="ProdGet", precio=20, stock=0))
    user = UsuarioDB(
        username="getuser",
        email="get@test.com",
        hashed_password=get_password_hash("pass"),
        rol="lector",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    mov_data = MovimientoBase(
        producto_id=producto.id,
        tipo="salida",
        cantidad=0,  # salida sin stock? En realidad mejor crear con entrada primero
        stock_resultante=0,
        usuario_id=user.id
    )
    # Ajustamos para que tenga sentido: creamos una entrada
    mov_data_entrada = MovimientoBase(
        producto_id=producto.id,
        tipo="entrada",
        cantidad=5,
        stock_resultante=5,
        usuario_id=user.id
    )
    mov = registrar_movimiento(db_session, mov_data_entrada)
    obtenido = get_movimiento_by_id(db_session, mov.id)
    assert obtenido is not None
    assert obtenido.id == mov.id
    assert get_movimiento_by_id(db_session, 99999) is None

def test_get_movimientos(db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="ProdList", precio=30, stock=10))
    user = UsuarioDB(
        username="listuser",
        email="list@test.com",
        hashed_password=get_password_hash("pass"),
        rol="admin",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Registrar varios movimientos
    for i in range(3):
        mov_data = MovimientoBase(
            producto_id=producto.id,
            tipo="entrada" if i % 2 == 0 else "salida",
            cantidad=i+1,
            stock_resultante=10 + (i+1) if i % 2 == 0 else 10 - (i+1),
            usuario_id=user.id
        )
        registrar_movimiento(db_session, mov_data)

    # Obtener todos
    todos = get_movimientos(db_session)
    assert len(todos) == 3

    # Paginación
    primeros = get_movimientos(db_session, skip=0, limit=2)
    assert len(primeros) == 2

    # Filtro por producto_id
    filtrados = get_movimientos(db_session, producto_id=producto.id)
    assert len(filtrados) == 3

    # Filtro por tipo
    solo_entradas = get_movimientos(db_session, tipo="entrada")
    assert len(solo_entradas) == 2

def test_get_movimientos_por_rango_ids(db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="ProdRango", precio=40, stock=15))
    user = UsuarioDB(
        username="rangouser",
        email="rango@test.com",
        hashed_password=get_password_hash("pass"),
        rol="editor",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    ids = []
    for i in range(5):
        mov_data = MovimientoBase(
            producto_id=producto.id,
            tipo="entrada",
            cantidad=1,
            stock_resultante=15 + i + 1,
            usuario_id=user.id
        )
        mov = registrar_movimiento(db_session, mov_data)
        ids.append(mov.id)

    # Obtener rango desde el segundo hasta el cuarto
    rango = get_movimientos_por_rango_ids(db_session, ids[1], ids[3])
    assert len(rango) == 3  # ids[1], ids[2], ids[3]
    assert rango[0].id == ids[1]
    assert rango[-1].id == ids[3]

# ------------------------------------------------------------------------------
# TESTS DE INTEGRACIÓN: ajustar_stock debe registrar movimiento automáticamente
# ------------------------------------------------------------------------------

def test_ajustar_stock_registra_movimiento(db_session):
    # Crear producto y usuario
    producto = create_producto(db_session, ProductoCreate(nombre="StockTest", precio=50, stock=10, stock_maximo=20))
    user = UsuarioDB(
        username="ajustador",
        email="ajusta@test.com",
        hashed_password=get_password_hash("pass"),
        rol="editor",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Ajustar stock (entrada)
    ajustar_stock(db_session, producto.id, 5, es_entrada=True, usuario_id=user.id)

    # Verificar que se haya creado un movimiento
    movimientos = get_movimientos(db_session, producto_id=producto.id)
    assert len(movimientos) == 1
    mov = movimientos[0]
    assert mov.tipo == "entrada"
    assert mov.cantidad == 5
    assert mov.stock_resultante == 15
    assert mov.usuario_id == user.id

    # Ajustar salida
    ajustar_stock(db_session, producto.id, 3, es_entrada=False, usuario_id=user.id)
    movimientos = get_movimientos(db_session, producto_id=producto.id)
    assert len(movimientos) == 2
    mov_salida = movimientos[0]  # el más reciente (orden descendente por fecha)
    assert mov_salida.tipo == "salida"
    assert mov_salida.cantidad == 3
    assert mov_salida.stock_resultante == 12

# ------------------------------------------------------------------------------
# TESTS DE ENDPOINTS DE MOVIMIENTOS (requieren cliente y autenticación)
# ------------------------------------------------------------------------------

def test_endpoint_listar_movimientos(client, auth_headers, db_session):
    # Crear producto y usuario para asociar movimientos
    producto = create_producto(db_session, ProductoCreate(nombre="EndpointProd", precio=60, stock=5))
    # El usuario autenticado es "testuser" (de conftest). Obtenemos su ID
    from app.models.usuario import UsuarioDB
    user = db_session.query(UsuarioDB).filter(UsuarioDB.username == "testuser").first()
    assert user is not None

    # Registrar movimiento
    ajustar_stock(db_session, producto.id, 2, es_entrada=True, usuario_id=user.id)

    # GET /movimientos
    response = client.get("/api/v1/movimientos", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Verificar estructura
    assert "id" in data[0]
    assert "producto_id" in data[0]
    assert "tipo" in data[0]
    assert "cantidad" in data[0]
    assert "stock_resultante" in data[0]

def test_endpoint_obtener_movimiento_por_id(client, auth_headers, db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="GetByIdProd", precio=70, stock=8))
    user = db_session.query(UsuarioDB).filter(UsuarioDB.username == "testuser").first()
    ajustar_stock(db_session, producto.id, 3, es_entrada=True, usuario_id=user.id)
    movimientos = get_movimientos(db_session, producto_id=producto.id)
    mov_id = movimientos[0].id

    response = client.get(f"/api/v1/movimientos/{mov_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mov_id
    assert data["producto_id"] == producto.id

    # ID inexistente
    response = client.get("/api/v1/movimientos/99999", headers=auth_headers)
    assert response.status_code == 404

def test_endpoint_movimientos_rango_ids(client, auth_headers, db_session):
    producto = create_producto(db_session, ProductoCreate(nombre="RangoProd", precio=80, stock=0))
    user = db_session.query(UsuarioDB).filter(UsuarioDB.username == "testuser").first()
    ids = []
    for i in range(3):
        ajustar_stock(db_session, producto.id, 1, es_entrada=True, usuario_id=user.id)
        movimientos = get_movimientos(db_session, producto_id=producto.id)
        ids.append(movimientos[0].id)

    desde, hasta = ids[0], ids[2]
    response = client.get(f"/api/v1/movimientos/range?desde={desde}&hasta={hasta}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["id"] == desde
    assert data[-1]["id"] == hasta

    # Error si desde > hasta
    response = client.get(f"/api/v1/movimientos/range?desde={hasta}&hasta={desde}", headers=auth_headers)
    assert response.status_code == 400