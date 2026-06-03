# Documentación de la API - DesktopManagerStock

## Base URL

Cuando el backend está corriendo localmente en:

```
http://localhost:8000/api/v1
```

La documentación interactiva generada automáticamente por FastAPI está disponible en:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Endpoints públicos (sin autenticación)

### Home / Información de la API

**GET** `/`

- **Autenticación:** no requerida
- **Respuesta:** información básica de la API

**Ejemplo:**

```bash
curl -X GET "http://localhost:8000/api/v1/"
```

**Respuesta (200 OK):**

```json
{
  "mensaje": "DesktopManagerStock API",
  "version": "0.1.1",
  "docs": "/docs"
}
```

---

## Autenticación

La mayoría de los endpoints requieren autenticación mediante **JWT** (Bearer token).

### Obtener token (login)

**Endpoint:** `POST /api/v1/auth/login`  
**Content-Type:** `application/x-www-form-urlencoded`

**Parámetros (form-data):**

| Campo      | Tipo   | Descripción                |
|------------|--------|----------------------------|
| `username` | string | Nombre de usuario          |
| `password` | string | Contraseña                 |

**Ejemplo de solicitud (curl):**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Respuesta exitosa (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Registro de nuevo usuario

**Endpoint:** `POST /api/v1/auth/register`  
**Content-Type:** `application/json`

**Cuerpo (JSON):**

| Campo      | Tipo   | Obligatorio | Descripción                                |
|------------|--------|-------------|--------------------------------------------|
| `username` | string | sí          | Nombre de usuario único                    |
| `email`    | string | sí          | Correo electrónico único                   |
| `password` | string | sí          | Contraseña en texto plano                  |
| `rol`      | string | no          | `admin`, `editor` o `lector` (por defecto `lector`) |

**Ejemplo:**

```json
{
  "username": "s4ndulos",
  "email": "s4ndulos@DesktopManagerStock.com",
  "password": "password_very_looong",
  "rol": "editor"
}
```

**Respuesta exitosa (200 OK):**

```json
{
  "id": 2,
  "username": "s4ndulos",
  "email": "s4ndulos@DesktopManagerStock.com",
  "rol": "editor",
  "activo": true
}
```

### Uso del token

Incluir el token en el encabezado `Authorization` de todas las peticiones a endpoints protegidos:

```
Authorization: Bearer <token>
```

---

## Endpoints de productos (requieren autenticación)

A continuación se detallan los endpoints para la gestión de productos.  
**Nota:** Todos devuelven o reciben objetos en formato JSON.

### Esquema del objeto `Producto`

| Campo          | Tipo    | Descripción                          |
|----------------|---------|--------------------------------------|
| `id`           | int     | Identificador único (autogenerado)   |
| `nombre`       | string  | Nombre del producto (único)          |
| `precio`       | float   | Precio unitario                      |
| `stock`        | int     | Cantidad disponible                  |
| `stock_minimo` | int     | Umbral para alerta (por defecto 5)   |
| `stock_maximo` | int     | Límite superior (por defecto 100)    |

**Ejemplo:**

```json
{
  "id": 1,
  "nombre": "Laptop",
  "precio": 750.67,
  "stock": 15,
  "stock_minimo": 5,
  "stock_maximo": 100
}
```

---

### 1. Listar todos los productos

**GET** `/productos`

- **Autenticación:** requerida (cualquier rol)
- **Respuesta:** lista de productos (vacía si no hay)

**Ejemplo:**

```bash
curl -X GET "http://localhost:8000/api/v1/productos" \
  -H "Authorization: Bearer <token>"
```

**Respuesta (200 OK):**

```json
[
  {
    "id": 1,
    "nombre": "Laptop",
    "precio": 750.67,
    "stock": 15,
    "stock_minimo": 5,
    "stock_maximo": 100
  }
]
```

---

### 2. Obtener un producto por ID

**GET** `/productos/{producto_id}`

- **Autenticación:** requerida (cualquier rol)
- **Respuesta:** producto solicitado

**Ejemplo:**

```bash
curl -X GET "http://localhost:8000/api/v1/productos/1" \
  -H "Authorization: Bearer <token>"
```

**Respuesta exitosa (200 OK):** objeto `Producto`.

**Errores:**  
- `404 Not Found` – producto no existe.

---

### 3. Crear un nuevo producto

**POST** `/productos`

- **Autenticación:** requerida (roles `admin` o `editor`)
- **Cuerpo:** objeto `ProductoCreate` (no incluye `id`)

**Ejemplo:**

```bash
curl -X POST "http://localhost:8000/api/v1/productos" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "nombre": "Mouse",
        "precio": 25000,50,
        "stock": 50,
        "stock_minimo": 10,
        "stock_maximo": 200
      }'
```

**Respuesta exitosa (201 Created):** el producto creado (con `id` asignado).

**Errores:**  
- `400 Bad Request` – ya existe un producto con el mismo nombre.  
- `403 Forbidden` – rol no autorizado.

---

### 4. Actualizar un producto (parcial o total)

**PUT** `/productos/{producto_id}`

- **Autenticación:** requerida (roles `admin` o `editor`)
- **Cuerpo:** objeto `ProductoUpdate` (todos los campos opcionales)

**Ejemplo (actualizar solo precio y stock):**

```bash
curl -X PUT "http://localhost:8000/api/v1/productos/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "precio": 999.99,
        "stock": 15
      }'
```

**Respuesta exitosa (200 OK):** producto actualizado.

**Errores:**  
- `404 Not Found` – producto no existe.  
- `403 Forbidden` – rol no autorizado.

---

### 5. Eliminar un producto

**DELETE** `/productos/{producto_id}`

- **Autenticación:** requerida (solo rol `admin`)
- **Respuesta:** sin contenido (código 204)

**Ejemplo:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/productos/1" \
  -H "Authorization: Bearer <token>"
```

**Respuesta exitosa:** `204 No Content`

**Errores:**  
- `404 Not Found` – producto no existe.  
- `403 Forbidden` – rol no es admin.

---

### 6. Ajustar stock (entrada/salida)

**PATCH** `/productos/{producto_id}/stock`

- **Autenticación:** requerida (roles `admin` o `editor`)
- **Parámetros de consulta (query):**

| Parámetro  | Tipo   | Obligatorio | Descripción                                   |
|------------|--------|-------------|-----------------------------------------------|
| `cantidad` | int    | sí          | Cantidad a aumentar o disminuir               |
| `tipo`     | string | no          | `entrada` (aumenta, por defecto) o `salida` (disminuye) |

**Ejemplo (aumentar stock en 5):**

```bash
curl -X PATCH "http://localhost:8000/api/v1/productos/1/stock?cantidad=5&tipo=entrada" \
  -H "Authorization: Bearer <token>"
```

**Respuesta exitosa (200 OK):**

```json
{
  "mensaje": "Stock actualizado. Nuevo stock: 15"
}
```

**Errores:**  
- `400 Bad Request` – stock insuficiente (si tipo=salida y cantidad > stock actual).  
- `404 Not Found` – producto no existe.  
- `403 Forbidden` – rol no autorizado.

---

### 7. Productos con stock bajo

**GET** `/productos/stock-bajo`

- **Autenticación:** requerida (cualquier rol)
- **Parámetros de consulta (opcional):**

| Parámetro | Tipo | Descripción                                                                 |
|-----------|------|-----------------------------------------------------------------------------|
| `umbral`  | int  | Si se envía, devuelve productos con stock <= umbral. Si no, usa `stock_minimo` de cada producto. |

**Ejemplo (umbral 3):**

```bash
curl -X GET "http://localhost:8000/api/v1/productos/stock-bajo?umbral=3" \
  -H "Authorization: Bearer <token>"
```

**Respuesta (200 OK):** lista de productos que cumplen la condición.

---

## Códigos de estado comunes

| Código | Significado                           |
|--------|---------------------------------------|
| 200    | OK – éxito                            |
| 201    | Created – recurso creado              |
| 204    | No Content – eliminación exitosa      |
| 400    | Bad Request – error de validación o lógica de negocio (stock insuficiente, duplicado, etc.) |
| 401    | Unauthorized – falta token o token inválido |
| 403    | Forbidden – rol insuficiente para la operación |
| 404    | Not Found – recurso no encontrado     |

---

## Notas adicionales

- El backend utiliza SQLite como base de datos por defecto. El archivo se crea automáticamente en `stock.db`.
- La clave secreta para JWT (`SECRET_KEY`) debe cambiarse en entornos de producción.
- Los roles disponibles son: `admin` (acceso total), `editor` (puede crear, modificar y ajustar stock, pero no eliminar), `lector` (solo consultas).
- El usuario administrador por defecto se crea automáticamente al iniciar la aplicación por primera vez:
  - **username:** `admin`
  - **password:** `admin123`
  - **rol:** `admin`
- La variable de entorno `STOCK_ALERT_THRESHOLD` (definida en `.env.example`) está disponible para configurar el umbral global de alerta de stock bajo, pero no es utilizada directamente en los endpoints actuales; la lógica de stock bajo se basa en `stock_minimo` de cada producto o en el parámetro `umbral`.