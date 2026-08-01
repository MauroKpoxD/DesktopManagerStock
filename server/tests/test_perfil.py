"""
Tests de los endpoints de perfil propio.

Antes no existían: no había forma de que un usuario viera su propio perfil,
actualizara su email o cambiara su contraseña sin acceso directo a la base
de datos.
"""

def test_obtener_mi_perfil(client, auth_headers, test_user):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user.username


def test_obtener_mi_perfil_sin_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_actualizar_mi_email(client, auth_headers):
    response = client.put("/api/v1/auth/me", json={"email": "nuevo@example.com"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "nuevo@example.com"


def test_actualizar_mi_email_duplicado(client, auth_headers, lector_headers):
    # test_lector ya tiene email lector@example.com
    response = client.put("/api/v1/auth/me", json={"email": "lector@example.com"}, headers=auth_headers)
    assert response.status_code == 400


def test_cambiar_password_incorrecta(client, auth_headers):
    response = client.post(
        "/api/v1/auth/me/password",
        json={"password_actual": "incorrecta", "password_nueva": "NuevaClave123!"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_cambiar_password_exitoso_y_relogin(client, auth_headers):
    response = client.post(
        "/api/v1/auth/me/password",
        json={"password_actual": "testpass", "password_nueva": "NuevaClave123!"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # La nueva contraseña debe permitir login...
    response = client.post("/api/v1/auth/login", data={"username": "testuser", "password": "NuevaClave123!"})
    assert response.status_code == 200
    # ...y la vieja ya no debe funcionar.
    response = client.post("/api/v1/auth/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 401


def test_cambiar_password_debil_es_rechazada(client, auth_headers):
    response = client.post(
        "/api/v1/auth/me/password",
        json={"password_actual": "testpass", "password_nueva": "debil"},
        headers=auth_headers,
    )
    assert response.status_code == 422
