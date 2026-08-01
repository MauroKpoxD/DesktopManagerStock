"""
Tests de las rutas administrativas de usuarios (/api/v1/usuarios).

Antes el esquema UsuarioUpdate estaba definido pero no lo usaba ningún
endpoint: no había forma de listar usuarios, cambiar su rol o
activar/desactivar una cuenta.
"""

def test_listar_usuarios_requiere_admin(client, auth_headers):
    response = client.get("/api/v1/usuarios", headers=auth_headers)
    assert response.status_code == 403

def test_listar_usuarios_como_admin(client, admin_headers, test_user, test_lector):
    response = client.get("/api/v1/usuarios", headers=admin_headers)
    assert response.status_code == 200
    usernames = [u["username"] for u in response.json()]
    assert "testuser" in usernames
    assert "lector" in usernames
    assert "X-Total-Count" in response.headers

def test_admin_cambia_rol_de_usuario(client, admin_headers, test_lector):
    response = client.put(f"/api/v1/usuarios/{test_lector.id}", json={"rol": "editor"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["rol"] == "editor"

def test_admin_no_puede_quitarse_su_propio_rol(client, admin_headers, test_admin):
    response = client.put(f"/api/v1/usuarios/{test_admin.id}", json={"rol": "lector"}, headers=admin_headers)
    assert response.status_code == 400

def test_admin_no_puede_desactivar_su_propia_cuenta(client, admin_headers, test_admin):
    response = client.put(f"/api/v1/usuarios/{test_admin.id}", json={"activo": False}, headers=admin_headers)
    assert response.status_code == 400

def test_admin_desactiva_usuario(client, admin_headers, test_lector):
    response = client.put(f"/api/v1/usuarios/{test_lector.id}", json={"activo": False}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["activo"] is False

def test_usuario_desactivado_no_puede_iniciar_sesion(client, admin_headers, test_lector):
    client.put(f"/api/v1/usuarios/{test_lector.id}", json={"activo": False}, headers=admin_headers)
    response = client.post("/api/v1/auth/login", data={"username": "lector", "password": "lectorpass"})
    assert response.status_code == 401

def test_crear_usuario_requiere_admin(client, auth_headers):
    response = client.post(
        "/api/v1/usuarios",
        json={"username": "nuevo1", "email": "nuevo1@example.com", "password": "Clave123!", "rol": "editor"},
        headers=auth_headers,
    )
    assert response.status_code == 403

def test_admin_crea_usuario_con_rol_elegido(client, admin_headers):
    response = client.post(
        "/api/v1/usuarios",
        json={"username": "nuevoeditor", "email": "nuevoeditor@example.com", "password": "Clave123!", "rol": "editor"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "nuevoeditor"
    assert data["rol"] == "editor"
    assert data["activo"] is True

    # El usuario creado debe poder loguearse con la contraseña dada.
    response = client.post("/api/v1/auth/login", data={"username": "nuevoeditor", "password": "Clave123!"})
    assert response.status_code == 200

def test_admin_no_puede_crear_usuario_duplicado(client, admin_headers, test_lector):
    response = client.post(
        "/api/v1/usuarios",
        json={"username": "lector", "email": "otro@example.com", "password": "Clave123!"},
        headers=admin_headers,
    )
    assert response.status_code == 400

def test_admin_crea_usuario_con_rol_invalido(client, admin_headers):
    response = client.post(
        "/api/v1/usuarios",
        json={"username": "roluser", "email": "roluser@example.com", "password": "Clave123!", "rol": "superadmin"},
        headers=admin_headers,
    )
    assert response.status_code == 400

def test_resetear_password_requiere_admin(client, auth_headers, test_lector):
    response = client.post(f"/api/v1/usuarios/{test_lector.id}/resetear-password", headers=auth_headers)
    assert response.status_code == 403

def test_admin_resetea_password_y_usuario_puede_loguearse(client, admin_headers, test_lector):
    response = client.post(f"/api/v1/usuarios/{test_lector.id}/resetear-password", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["usuario"]["username"] == "lector"
    nueva_password = data["password_temporal"]
    assert len(nueva_password) >= 8

    # La contraseña vieja ya no funciona...
    response = client.post("/api/v1/auth/login", data={"username": "lector", "password": "lectorpass"})
    assert response.status_code == 401

    # ...pero la temporal sí.
    response = client.post("/api/v1/auth/login", data={"username": "lector", "password": nueva_password})
    assert response.status_code == 200
