# 📘 API_DOCS.md (Actualizada)

## Guía Completa para Consumir la API DesktopManagerStock

**Versión de la API:** 0.3.2  
**URL Base:** `http://127.0.0.1:8000/api/v1`  
**Autenticación:** JWT (Bearer Token) + Refresh Tokens rotativos.

Este documento describe todos los endpoints disponibles, los esquemas de datos, el flujo de autenticación (incluyendo rotación de refresh tokens), y ejemplos prácticos para consumir la API desde aplicaciones Windows Forms (.NET) o cualquier cliente HTTP.

---

## 🔐 Autenticación y Gestión de Sesiones

La API utiliza **JWT (JSON Web Tokens)** para proteger los endpoints. Además, implementa un sistema de **refresh tokens rotativos** para mayor seguridad:

- **Access Token:** Válido por 30 minutos (configurable).
- **Refresh Token:** Válido por 7 días, se almacena en la base de datos y se revoca al hacer logout o al rotarlo.
- **Rotación:** Cada vez que se renueva el access token usando el refresh token, el servidor **genera un nuevo refresh token** y revoca el anterior. Esto reduce el riesgo de reutilización maliciosa.
- **Revocación:** Al hacer logout, el refresh token se revoca inmediatamente y no puede volver a usarse.

### 1. Registro de Usuario

**Endpoint:** `POST /auth/register`  
**Body (JSON):**

```json
{
  "username": "ejemplo",
  "email": "ejemplo@dominio.com",
  "password": "SecurePass123!",
  "rol": "lector"   // opcional, siempre se asigna "lector" por seguridad
}
```

**Respuesta exitosa (200):**

```json
{
  "id": 1,
  "username": "ejemplo",
  "email": "ejemplo@dominio.com",
  "rol": "lector",
  "activo": true
}
```

**Validaciones:**  
- Contraseña: mínimo 8 caracteres, al menos una mayúscula, un número y un carácter especial.
- Username y email únicos.

---

### 2. Login (Obtener Tokens)

**Endpoint:** `POST /auth/login`  
**Body (form-urlencoded):**  
`username=ejemplo&password=SecurePass123!`

**Respuesta exitosa (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "refresh_token": "a1b2c3d4e5f6..."
}
```

**Guardar ambos tokens** en el cliente. El `refresh_token` se usará para obtener nuevos access tokens sin pedir credenciales nuevamente.

---

### 3. Renovar Access Token (Refresh)

**Endpoint:** `POST /auth/refresh`  
**Body (JSON):**

```json
{
  "refresh_token": "a1b2c3d4e5f6..."
}
```

**Respuesta exitosa (200):** (el servidor **rota el refresh token**)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs... (nuevo)",
  "token_type": "bearer",
  "refresh_token": "x7y8z9... (nuevo, diferente al anterior)"
}
```

**Importante:** Actualiza el `refresh_token` almacenado en el cliente con el nuevo valor. El token anterior queda revocado y no se puede reutilizar.

---

### 4. Cerrar Sesión (Logout)

**Endpoint:** `POST /auth/logout`  
**Body (JSON):**

```json
{
  "refresh_token": "a1b2c3d4e5f6..."
}
```

**Respuesta exitosa (200):**

```json
{
  "mensaje": "Sesión cerrada exitosamente"
}
```

El refresh token enviado queda **revocado**. Cualquier intento de usarlo en `/refresh` devolverá `401 Unauthorized`.

---

## 📦 Endpoints Principales

Todos los endpoints (excepto `/auth/register` y `/auth/login`) requieren el encabezado:

```
Authorization: Bearer <access_token>
```

### 5. Productos

#### 5.1 Listar productos (paginado)

<<<<<<< HEAD
**GET** `/productos?skip=0&limit=100`
=======
**GET** `/productos?skip=0&limit=100&incluir_inactivos=false&categoria=Almacén`

- `incluir_inactivos` (opcional, default `false`): si es `true`, incluye también los productos desactivados (ver 5.5).
- `categoria` (opcional): filtra por categoría exacta.
- La respuesta incluye el header `X-Total-Count` con el total de productos que cumplen el filtro (útil para paginar en el cliente sin traer todo).
>>>>>>> feature/interfaz-y-reconstruccion

**Respuesta:** Lista de objetos `Producto`:

```json
[
  {
    "id": 1,
    "nombre": "Laptop",
<<<<<<< HEAD
    "precio": 1500.50,
    "stock": 10,
    "stock_minimo": 5,
    "stock_maximo": 50
=======
    "categoria": "Electrónica",
    "sku": "LAP-001",
    "proveedor_nombre": "Distribuidora XYZ",
    "proveedor_contacto": "011-4444-5555",
    "precio": 1500.50,
    "stock": 10,
    "stock_minimo": 5,
    "stock_maximo": 50,
    "activo": true
>>>>>>> feature/interfaz-y-reconstruccion
  }
]
```

<<<<<<< HEAD
=======
`categoria`, `sku`, `proveedor_nombre` y `proveedor_contacto` son todos campos de texto libre y opcionales (pueden ser `null`).

**GET** `/productos/categorias` devuelve la lista de categorías distintas ya usadas por productos activos (`["Almacén", "Electrónica", ...]`), útil para poblar un filtro en el cliente.

>>>>>>> feature/interfaz-y-reconstruccion
#### 5.2 Obtener producto por ID

**GET** `/productos/{id}`

#### 5.3 Crear producto (requiere rol admin o editor)

**POST** `/productos`  
**Body:**

```json
{
  "nombre": "Mouse",
  "precio": 25.99,
  "stock": 20,
  "stock_minimo": 5,
  "stock_maximo": 100
}
```

**Respuesta:** Producto creado (201).

#### 5.4 Actualizar producto (requiere admin o editor)

**PUT** `/productos/{id}`  
**Body (todos opcionales):**

```json
{
  "nombre": "Mouse Gamer",
  "precio": 35.99,
  "stock_minimo": 3,
  "stock_maximo": 80
}
```

<<<<<<< HEAD
**Nota:** El campo `stock` no se puede modificar directamente; se debe usar el endpoint de ajuste de stock.
=======
**Nota:** El campo `stock` no se puede modificar directamente; se debe usar el endpoint de ajuste de stock. El campo `activo` solo puede modificarlo un usuario con rol `admin` (un `editor` recibe 400 si lo incluye).
>>>>>>> feature/interfaz-y-reconstruccion

#### 5.5 Eliminar producto (solo admin)

**DELETE** `/productos/{id}` (sin contenido, 204)

<<<<<<< HEAD
=======
Es un **soft delete**: el producto se marca como `activo=false` y deja de aparecer en los listados por defecto, pero **su historial de movimientos se conserva** para auditoría y reportes. Un producto desactivado no admite nuevos ajustes de stock (400 si se intenta). El nombre del producto queda reservado (no se puede crear otro con el mismo nombre) hasta que se reactive o se le cambie el nombre.

#### 5.5b Reactivar producto (solo admin)

**PATCH** `/productos/{id}/reactivar`

Vuelve a marcar como `activo=true` un producto previamente eliminado (soft delete).

#### 5.5c Importar productos desde CSV (admin o editor)

**POST** `/productos/importar-csv` (multipart/form-data, campo `archivo`)

Columnas reconocidas (solo `nombre` es obligatoria): `nombre, categoria, sku, precio, stock, stock_minimo, stock_maximo, proveedor_nombre, proveedor_contacto`. Filas con errores (nombre duplicado, datos inválidos, sin nombre) se omiten individualmente sin abortar el resto de la importación.

```json
{
  "total_filas": 3,
  "creados": 2,
  "productos_creados": ["Teclado", "Mouse"],
  "omitidos": [{ "fila": 3, "motivo": "Ya existe un producto con el nombre 'Teclado'" }]
}
```

>>>>>>> feature/interfaz-y-reconstruccion
#### 5.6 Ajustar stock (requiere admin o editor)

**PATCH** `/productos/{id}/stock?cantidad=5&tipo=entrada`  
- `cantidad`: número positivo.
- `tipo`: `entrada` o `salida`.

**Respuesta:**

```json
{
  "mensaje": "Stock actualizado. Nuevo stock: 15"
}
```

#### 5.7 Listar productos con stock bajo

**GET** `/productos/stock/bajo?umbral=5`  
- `umbral` (opcional): si no se envía, usa el `stock_minimo` de cada producto.

---

### 6. Movimientos de Stock

#### 6.1 Listar movimientos (filtros)

**GET** `/movimientos?skip=0&limit=100&producto_id=1&tipo=entrada`

- Filtros opcionales: `producto_id`, `tipo`.

**Respuesta:** Lista de `Movimiento`:

```json
[
  {
    "id": 1,
    "producto_id": 1,
    "tipo": "entrada",
    "cantidad": 5,
    "stock_resultante": 15,
    "usuario_id": 2,
    "fecha_hora": "2026-07-09T03:05:28"
  }
]
```

#### 6.2 Obtener movimiento por ID

**GET** `/movimientos/{id}`

#### 6.3 Rango de movimientos por IDs (útil para sincronización)

**GET** `/movimientos/range?desde=10&hasta=20`  
- Límite máximo de 1000 registros.

---

### 7. Reportes (requiere admin o editor)

Los reportes se generan en **PDF** o **Excel** y se descargan como archivo.

#### 7.1 Reporte de productos

**GET** `/reportes/productos?formato=pdf`  
- `formato`: `pdf` o `excel`.

#### 7.2 Reporte de stock bajo

**GET** `/reportes/stock-bajo?formato=pdf&umbral=10`  
- `umbral` (opcional): umbral de stock para el filtro.

#### 7.3 Reporte de movimientos (con filtros de fecha optimizados)

**GET** `/reportes/movimientos?formato=pdf&fecha_desde=2026-01-01&fecha_hasta=2026-12-31&producto_id=1`

- `fecha_desde`, `fecha_hasta`: en formato ISO (YYYY-MM-DD).
- `producto_id` (opcional): filtrar por producto.

**Nota:** Los filtros de fecha se aplican directamente en la consulta SQL, lo que mejora el rendimiento con grandes volúmenes de datos.

---

## 🧑‍💻 Ejemplo Práctico para Cliente .NET (WinForms)

A continuación se muestra un **servicio completo** que maneja autenticación, rotación de refresh tokens y reconexión automática.

### Clase `ApiService` (con soporte para refresh automático)

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class ApiService
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    private string _accessToken;
    private string _refreshToken;
    private bool _isRefreshing;

    public event Action OnUnauthorized; // para notificar a la UI que debe reloguearse

    public ApiService(string baseUrl = "http://127.0.0.1:8000/api/v1")
    {
        _baseUrl = baseUrl;
        _httpClient = new HttpClient();
    }

    public void SetTokens(string accessToken, string refreshToken)
    {
        _accessToken = accessToken;
        _refreshToken = refreshToken;
        _httpClient.DefaultRequestHeaders.Authorization = 
            new AuthenticationHeaderValue("Bearer", _accessToken);
    }

    public (string AccessToken, string RefreshToken) GetTokens() => (_accessToken, _refreshToken);

    private async Task<T> SendAsync<T>(HttpMethod method, string endpoint, object data = null)
    {
        var request = new HttpRequestMessage(method, $"{_baseUrl}{endpoint}");
        if (data != null)
        {
            var json = JsonConvert.SerializeObject(data);
            request.Content = new StringContent(json, Encoding.UTF8, "application/json");
        }

        var response = await _httpClient.SendAsync(request);
        var responseBody = await response.Content.ReadAsStringAsync();

        if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized && !_isRefreshing)
        {
            // Intentar renovar token automáticamente
            if (await RefreshTokenAsync())
            {
                // Reintentar la petición original
                request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _accessToken);
                response = await _httpClient.SendAsync(request);
                responseBody = await response.Content.ReadAsStringAsync();
            }
            else
            {
                OnUnauthorized?.Invoke(); // Notificar que las credenciales ya no sirven
                throw new UnauthorizedAccessException("Sesión expirada. Vuelve a iniciar sesión.");
            }
        }

        if (!response.IsSuccessStatusCode)
            throw new HttpRequestException($"Error {response.StatusCode}: {responseBody}");

        if (typeof(T) == typeof(string))
            return (T)(object)responseBody;
        else
            return JsonConvert.DeserializeObject<T>(responseBody);
    }

    private async Task<bool> RefreshTokenAsync()
    {
        _isRefreshing = true;
        try
        {
            var payload = new { refresh_token = _refreshToken };
            var json = JsonConvert.SerializeObject(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync($"{_baseUrl}/auth/refresh", content);
            if (response.IsSuccessStatusCode)
            {
                var result = JsonConvert.DeserializeObject<LoginResponse>(await response.Content.ReadAsStringAsync());
                _accessToken = result.access_token;
                _refreshToken = result.refresh_token; // NUEVO refresh token
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _accessToken);
                return true;
            }
            return false;
        }
        finally
        {
            _isRefreshing = false;
        }
    }

    // Métodos específicos de la API
    public Task<T> GetAsync<T>(string endpoint) => SendAsync<T>(HttpMethod.Get, endpoint);
    public Task<T> PostAsync<T>(string endpoint, object data) => SendAsync<T>(HttpMethod.Post, endpoint, data);
    public Task<T> PutAsync<T>(string endpoint, object data) => SendAsync<T>(HttpMethod.Put, endpoint, data);
    public Task<T> PatchAsync<T>(string endpoint, object data) => SendAsync<T>(HttpMethod.Patch, endpoint, data);
    public Task DeleteAsync(string endpoint) => SendAsync<object>(HttpMethod.Delete, endpoint);

    // Login (obtener tokens)
    public async Task<LoginResponse> LoginAsync(string username, string password)
    {
        var content = new FormUrlEncodedContent(new[]
        {
            new KeyValuePair<string, string>("username", username),
            new KeyValuePair<string, string>("password", password)
        });
        var response = await _httpClient.PostAsync($"{_baseUrl}/auth/login", content);
        var json = await response.Content.ReadAsStringAsync();
        if (response.IsSuccessStatusCode)
        {
            var result = JsonConvert.DeserializeObject<LoginResponse>(json);
            SetTokens(result.access_token, result.refresh_token);
            return result;
        }
        throw new Exception(json);
    }

    // Logout (revocar token)
    public async Task LogoutAsync()
    {
        var payload = new { refresh_token = _refreshToken };
        await PostAsync<object>("/auth/logout", payload);
        _accessToken = null;
        _refreshToken = null;
        _httpClient.DefaultRequestHeaders.Authorization = null;
    }
}

public class LoginResponse
{
    public string access_token { get; set; }
    public string token_type { get; set; }
    public string refresh_token { get; set; }
}
```

### Uso en un formulario

```csharp
private ApiService _api = new ApiService();

private async void btnLogin_Click(object sender, EventArgs e)
{
    try
    {
        await _api.LoginAsync(txtUser.Text, txtPass.Text);
        var productos = await _api.GetAsync<List<Producto>>("/productos");
        dataGridView1.DataSource = productos;
        lblStatus.Text = "Conectado";
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}");
    }
}

// Cerrar sesión
private async void btnLogout_Click(object sender, EventArgs e)
{
    await _api.LogoutAsync();
    // Limpiar UI y tokens
}

// Manejar evento de token expirado
private void OnUnauthorized()
{
    this.Invoke((MethodInvoker)delegate {
        MessageBox.Show("Tu sesión ha expirado. Vuelve a iniciar sesión.");
        // Redirigir a pantalla de login
    });
}
```

---

## 🛡️ Roles y Autorización

La API define tres roles:

| Rol | Permisos |
|-----|----------|
| **admin** | CRUD completo de productos, ajuste de stock, reportes, eliminación de productos. |
| **editor** | Crear, actualizar productos, ajustar stock, ver reportes (excepto eliminar). |
| **lector** | Solo lectura de productos y movimientos. Sin acceso a reportes. |

**Endpoints con restricciones:**
- `POST /productos` → admin/editor
- `PUT /productos` → admin/editor
- `DELETE /productos` → solo admin
- `PATCH /productos/{id}/stock` → admin/editor
- Todos los reportes → admin/editor
- Los endpoints GET (productos, movimientos) → cualquier usuario autenticado.

---

## 📊 Ejemplo de Reporte con Filtros de Fecha

```csharp
// Descargar reporte de movimientos en PDF
var query = "?formato=pdf&fecha_desde=2026-01-01&fecha_hasta=2026-12-31";
byte[] pdfBytes = await _api.GetAsync<byte[]>($"/reportes/movimientos{query}");
File.WriteAllBytes("movimientos.pdf", pdfBytes);
```

---

## 🧹 Mantenimiento de la Base de Datos

La API realiza automáticamente las siguientes tareas al iniciar:
- Crea las tablas (si no existen).
- Crea un usuario `admin` con contraseña aleatoria (guardada en `logs/.admin_password.txt` en producción).
- **Elimina todos los refresh tokens expirados o revocados**, manteniendo la base de datos limpia y eficiente.

---

## 🐳 Despliegue con Docker

El proyecto incluye un `docker-compose.yml` con **healthcheck** que verifica el estado de la API usando Python (sin depender de `curl`). Para levantar el entorno:

```bash
docker compose up -d
```

Para verificar el estado:

```bash
docker compose ps
```

El contenedor `api` debe aparecer como `healthy`.

---

## 📌 Buenas Prácticas para el Cliente

1. **Almacenamiento seguro de tokens:** Usa `Properties.Settings` o un almacenamiento cifrado (ej. Windows Credential Manager).
2. **Manejo de errores:** Siempre captura excepciones y muestra mensajes claros.
3. **No uses `.Result` o `.Wait()`** para no bloquear la UI; usa `await`.
4. **Configura la URL base** desde un archivo de configuración (appsettings.json o similar) para cambiar entre entornos.
5. **Renovación automática:** Implementa el patrón de refresh automático como en el ejemplo.
6. **Reutiliza `HttpClient`** (una instancia por aplicación) para evitar agotar puertos.

---

<<<<<<< HEAD
=======
## 👤 Perfil propio

#### 8.1 Ver mi perfil

**GET** `/auth/me`

#### 8.2 Actualizar mi email

**PUT** `/auth/me`
```json
{ "email": "nuevo@example.com" }
```
No permite cambiar el propio rol (eso solo lo puede hacer un admin, ver más abajo).

#### 8.3 Cambiar mi contraseña

**POST** `/auth/me/password`
```json
{ "password_actual": "actual123!", "password_nueva": "NuevaClave123!" }
```
Al cambiar la contraseña se revocan todos los refresh tokens existentes (se cierra sesión en otros dispositivos).

---

## 🧑‍⚖️ Administración de usuarios (solo admin)

#### 9.1 Listar usuarios

**GET** `/usuarios?skip=0&limit=100` — incluye header `X-Total-Count`.

#### 9.2 Crear un usuario directamente

**POST** `/usuarios`
```json
{ "username": "jperez", "email": "jperez@example.com", "password": "Clave123!", "rol": "editor" }
```
A diferencia de `POST /auth/register` (público, siempre crea `rol: "lector"`), este endpoint es solo para admins y permite elegir el rol del usuario nuevo (admin/editor/lector) directamente.

#### 9.3 Ver un usuario

**GET** `/usuarios/{id}`

#### 9.4 Actualizar rol / estado / email de un usuario

**PUT** `/usuarios/{id}`
```json
{ "rol": "editor", "activo": true, "email": "otro@example.com" }
```
Todos los campos son opcionales. Un admin no puede quitarse a sí mismo el rol de admin ni desactivar su propia cuenta (evita quedarse sin acceso). Al desactivar un usuario se revocan sus refresh tokens y ya no puede iniciar sesión.

#### 9.5 Restablecer contraseña de un usuario

**POST** `/usuarios/{id}/resetear-password`

Genera una contraseña temporal para un usuario que perdió acceso a la suya (no hay recuperación por email todavía). La respuesta incluye la contraseña en texto plano **una sola vez**:
```json
{ "usuario": { "id": 3, "username": "jperez", ... }, "password_temporal": "Xy7pQr2mK!A1" }
```
Se recomienda que la persona la cambie apenas entre, con `POST /auth/me/password`.

---

## ❤️ Healthcheck

**GET** `/health` (sin autenticación)

Verifica que la API responde **y** que puede conectarse a la base de datos:

```json
{ "status": "ok", "database": "ok", "version": "1.0.0" }
```

Responde `503` con `"status": "degraded"` si la base de datos no responde. Es el endpoint que usa el `healthcheck` de Docker (antes apuntaba a `/` y no detectaba caídas de la base de datos).

---

>>>>>>> feature/interfaz-y-reconstruccion
## 📄 Licencia

Este proyecto está bajo licencia **Apache 2.0**. Consulta el archivo LICENSE para más detalles.

---

<<<<<<< HEAD
**Última actualización:** 2026-07-09
=======
**Última actualización:** 2026-07-13
>>>>>>> feature/interfaz-y-reconstruccion
