"""
ÚLTIMA MODIFICACIÓN: 12/6/2025 por S4NDULOS
PROPÓSITO: Pruebas para endpoints de reportes (PDF y Excel)
"""

import pytest
from fastapi import status

def test_reportes_requieren_autenticacion(client):
    endpoints = [
        "/api/v1/reportes/productos",
        "/api/v1/reportes/stock-bajo",
        "/api/v1/reportes/movimientos"
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_reportes_requieren_rol_admin_o_editor(client, lector_headers):
    endpoints = [
        "/api/v1/reportes/productos",
        "/api/v1/reportes/stock-bajo",
        "/api/v1/reportes/movimientos"
    ]
    for endpoint in endpoints:
        response = client.get(endpoint, headers=lector_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

def test_reportes_permitidos_editor(client, auth_headers):
    endpoints = [
        ("/api/v1/reportes/productos?formato=pdf", "application/pdf"),
        ("/api/v1/reportes/stock-bajo?formato=pdf", "application/pdf"),
        ("/api/v1/reportes/movimientos?formato=pdf", "application/pdf"),
    ]
    for endpoint, content_type in endpoints:
        response = client.get(endpoint, headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == content_type

def test_reporte_productos_excel(client, auth_headers):
    response = client.get("/api/v1/reportes/productos?formato=excel", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content[:2] == b'PK'

def test_reporte_stock_bajo_con_umbral(client, auth_headers, productos_demo):
    response = client.get("/api/v1/reportes/stock-bajo?formato=pdf&umbral=15", headers=auth_headers)
    assert response.status_code == 200

def test_reporte_movimientos_filtros(client, auth_headers, movimientos_demo):
    response = client.get("/api/v1/reportes/movimientos?formato=pdf&producto_id=1", headers=auth_headers)
    assert response.status_code == 200

def test_reporte_formato_invalido(client, auth_headers):
    response = client.get("/api/v1/reportes/productos?formato=csv", headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY