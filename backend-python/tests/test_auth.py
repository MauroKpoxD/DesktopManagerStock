"""
ÚLTIMA MODIFICACIÓN: 30/05/2025 por S4NDULOS
PROPÓSITO: Prueba el flujo completo de autenticación:
           registro de usuario, login, obtención de token y acceso a endpoint protegido
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_and_login(client):
    reg_data = {
        "username": "pytestuser",
        "email": "pytest@sixseven.com",
        "password": "test67",
        "rol": "lector"
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 200
    assert response.json()["username"] == "pytestuser"

    login_data = {
        "username": "pytestuser",
        "password": "test67"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/productos", headers=headers)
    assert response.status_code == 200