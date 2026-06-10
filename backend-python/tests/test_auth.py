"""
ÚLTIMA MODIFICACIÓN: 9/6/2025 por S4NDULOS
PROPÓSITO: Prueba el flujo completo de autenticación: registro, login,
           y acceso a endpoint protegido. Incluye tests de seguridad.
"""

import pytest
from app.core.config import settings

def test_register_and_login(client):
    reg_data = {
        "username": "pytestuser",
        "email": "pytest@sixseven.com",
        "password": "Test67!!",
        "rol": "lector"
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    if response.status_code != 200:
        print("Error en registro:", response.json())
    assert response.status_code == 200
    assert response.json()["username"] == "pytestuser"
    assert response.json()["rol"] == "lector"

    login_data = {
        "username": "pytestuser",
        "password": "Test67!!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/productos", headers=headers)
    assert response.status_code == 200

def test_register_ignores_admin_role(client):
    reg_data = {
        "username": "hacker",
        "email": "hacker@test.com",
        "password": "SecurePass123!",
        "rol": "admin"
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 200
    assert response.json()["rol"] == "lector"

def test_register_weak_password(client):
    reg_data = {
        "username": "weakuser",
        "email": "weak@test.com",
        "password": "1234",
        "rol": "lector"
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 422
    detail = response.json()["detail"]
    error_str = str(detail).lower()
    assert any(keyword in error_str for keyword in ["contraseña", "password", "mayúscula", "número", "carácter especial", "length"]), \
        f"Error inesperado: {detail}"

def test_login_rate_limit(client):
    if not settings.rate_limit_enabled:
        pytest.skip("Rate limiting desactivado en entorno de pruebas")
    for _ in range(6):
        response = client.post("/api/v1/auth/login", data={"username": "nonexistent", "password": "wrong"})
        if response.status_code == 429:
            break
    else:
        pytest.fail("No se alcanzó el rate limit después de 6 intentos")

# -------------------- NUEVOS TESTS --------------------

def test_protected_endpoint_with_invalid_token(client):
    headers = {"Authorization": "Bearer tokeninvalido"}
    response = client.get("/api/v1/productos", headers=headers)
    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    response = client.get("/api/v1/productos")
    assert response.status_code == 401

def test_register_duplicate_username(client):
    reg_data = {
        "username": "duplicate",
        "email": "dup1@test.com",
        "password": "SecurePass123!"
    }
    client.post("/api/v1/auth/register", json=reg_data)
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 400
    assert "Nombre de usuario ya registrado" in response.json()["detail"]

def test_register_duplicate_email(client):
    reg_data1 = {"username": "user1", "email": "same@test.com", "password": "SecurePass123!"}
    reg_data2 = {"username": "user2", "email": "same@test.com", "password": "SecurePass123!"}
    client.post("/api/v1/auth/register", json=reg_data1)
    response = client.post("/api/v1/auth/register", json=reg_data2)
    assert response.status_code == 400
    assert "Email ya registrado" in response.json()["detail"]