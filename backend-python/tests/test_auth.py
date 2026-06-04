"""
ÚLTIMA MODIFICACIÓN: 4/6/2025 por S4NDULOS
PROPÓSITO: Prueba el flujo completo de autenticación: registro, login,
           y acceso a endpoint protegido. Incluye tests de seguridad.
"""

import pytest
from app.core.config import settings  # Importar configuración global

def test_register_and_login(client):
    reg_data = {
        "username": "pytestuser",
        "email": "pytest@sixseven.com",
        "password": "Test67!!",  # 8 caracteres (cumple mayúscula, número, especial)
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
    """Verifica el rate limiting en login (si está activado)."""
    if not settings.rate_limit_enabled:
        pytest.skip("Rate limiting desactivado en entorno de pruebas")
    # Realiza 6 intentos con credenciales inválidas
    for _ in range(6):
        response = client.post("/api/v1/auth/login", data={"username": "nonexistent", "password": "wrong"})
        if response.status_code == 429:
            break
    else:
        pytest.fail("No se alcanzó el rate limit después de 6 intentos")