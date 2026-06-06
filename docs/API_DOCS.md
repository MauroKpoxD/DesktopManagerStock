# Guía General para Consumir APIs desde Windows Forms (C#)

Esta guía te enseñará los conceptos básicos de las APIs REST, cómo consumirlas desde una aplicación Windows Forms, cómo manejar autenticación con tokens JWT, y cómo estructurar tu código de forma profesional. Al final, aplicarás todo con la API de gestión de stock `DesktopManagerStock`.

---

## 1. ¿Qué es una API REST?

Una **API** (Interfaz de Programación de Aplicaciones) es un puente que permite que dos programas se comuniquen. En la web, las APIs **REST** usan el protocolo **HTTP** y formatos como **JSON** para enviar y recibir datos.

- **Métodos HTTP principales**:
  - `GET` → Obtener datos.
  - `POST` → Crear un nuevo recurso.
  - `PUT` / `PATCH` → Actualizar un recurso.
  - `DELETE` → Eliminar un recurso.

- **JSON**: Es el formato de texto más usado. Ejemplo:
  ```json
  {
    "nombre": "Laptop",
    "precio": 1500.00,
    "stock": 10
  }
  ```

---

## 2. Preparando el Proyecto WinForms

1. Abre Visual Studio y crea un nuevo proyecto **Windows Forms App (.NET Framework o .NET)**.
2. Agrega el paquete **Newtonsoft.Json** desde NuGet (herramientas → Administrador de paquetes NuGet → Buscar `Newtonsoft.Json` e instalar). Es el estándar para trabajar con JSON en .NET.

---

## 3. Concepto Fundamental: `HttpClient`

`HttpClient` es la clase que usamos para enviar peticiones HTTP. **Importante**: No se debe crear una instancia nueva para cada petición (puede causar problemas de rendimiento). Lo ideal es una instancia compartida o un `HttpClientFactory`.

### Ejemplo básico de GET
```csharp
using System.Net.Http;
using Newtonsoft.Json;

public async Task<string> ObtenerDatosAsync()
{
    using HttpClient client = new HttpClient();
    var response = await client.GetAsync("https://api.ejemplo.com/recursos");
    if (response.IsSuccessStatusCode)
    {
        string json = await response.Content.ReadAsStringAsync();
        return json;
    }
    return null;
}
```

---

## 4. Autenticación con JWT (JSON Web Token)

Muchas APIs protegen sus endpoints con tokens. El flujo típico es:

1. Enviar usuario/contraseña a `/login`.
2. Recibir un `access_token`.
3. Enviar ese token en el encabezado `Authorization: Bearer <token>` para todas las demás peticiones.

### Ejemplo de login y almacenamiento del token
```csharp
public async Task<bool> LoginAsync(string username, string password)
{
    var loginData = new { username, password };
    var content = new StringContent(JsonConvert.SerializeObject(loginData), Encoding.UTF8, "application/json");
    
    using HttpClient client = new HttpClient();
    var response = await client.PostAsync("http://127.0.0.1:8000/api/v1/auth/login", content);
    
    if (response.IsSuccessStatusCode)
    {
        string json = await response.Content.ReadAsStringAsync();
        dynamic result = JsonConvert.DeserializeObject(json);
        string token = result.access_token;
        
        // Guardar token (puede ser en una variable estática o en Properties.Settings)
        Properties.Settings.Default.Token = token;
        Properties.Settings.Default.Save();
        
        return true;
    }
    return false;
}
```

### Enviar token en peticiones posteriores
```csharp
client.DefaultRequestHeaders.Authorization = 
    new AuthenticationHeaderValue("Bearer", token);
```

---

## 5. Asincronía y UI (Evitar que la ventana se congele)

Los métodos asincrónicos (`async` / `await`) evitan que la interfaz de usuario se bloquee mientras espera la respuesta de la API.

- Usa `async Task` en lugar de `void` (excepto para eventos de UI).
- En eventos como `button_Click`, puedes usar `async void`, pero dentro de él espera con `await`.

**Ejemplo**:
```csharp
private async void btnLogin_Click(object sender, EventArgs e)
{
    btnLogin.Enabled = false;
    lblEstado.Text = "Conectando...";
    
    bool ok = await LoginAsync(txtUsuario.Text, txtPassword.Text);
    if (ok)
        lblEstado.Text = "Login exitoso";
    else
        lblEstado.Text = "Error de autenticación";
    
    btnLogin.Enabled = true;
}
```

---

## 🧱 6. Estructurando el Código (Buenas Prácticas)

No pongas todo el código de la API dentro del formulario. Separa responsabilidades:

- **Models** → Clases que representan los datos (DTOs).
- **Services** → Clase `ApiService` que contiene los métodos de comunicación.
- **Helpers** → Clase para manejar el token (guardarlo, recuperarlo, etc.).
- **Forms** → Solo lógica de UI y llamadas al servicio.

### Ejemplo de una clase `ApiService` genérica

```csharp
public class ApiService
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    
    public ApiService(string baseUrl = "http://127.0.0.1:8000")
    {
        _baseUrl = baseUrl;
        _httpClient = new HttpClient();
    }
    
    public void SetToken(string token)
    {
        _httpClient.DefaultRequestHeaders.Authorization = 
            new AuthenticationHeaderValue("Bearer", token);
    }
    
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
        
        if (response.IsSuccessStatusCode)
        {
            return JsonConvert.DeserializeObject<T>(responseBody);
        }
        else
        {
            throw new HttpRequestException($"Error {response.StatusCode}: {responseBody}");
        }
    }
    
    public Task<T> GetAsync<T>(string endpoint) => SendAsync<T>(HttpMethod.Get, endpoint);
    public Task<T> PostAsync<T>(string endpoint, object data) => SendAsync<T>(HttpMethod.Post, endpoint, data);
    public Task<T> PutAsync<T>(string endpoint, object data) => SendAsync<T>(HttpMethod.Put, endpoint, data);
    public Task<T> PatchAsync<T>(string endpoint, object data) => SendAsync<T>(HttpMethod.Patch, endpoint, data);
    public Task DeleteAsync(string endpoint) => SendAsync<object>(HttpMethod.Delete, endpoint);
}
```

---

## 7. Ejemplo Práctico con la API de Stock

Aplicamos los conceptos a la API `DesktopManagerStock`. Suponiendo que ya tienes los **modelos** (Producto, Movimiento, etc.) que vimos antes.

### Login y guardado del token
```csharp
public async Task<LoginResponse> LoginAsync(string username, string password)
{
    var content = new FormUrlEncodedContent(new[]
    {
        new KeyValuePair<string, string>("username", username),
        new KeyValuePair<string, string>("password", password)
    });
    
    var response = await _httpClient.PostAsync("/api/v1/auth/login", content);
    var json = await response.Content.ReadAsStringAsync();
    if (response.IsSuccessStatusCode)
        return JsonConvert.DeserializeObject<LoginResponse>(json);
    else
        throw new Exception(json);
}
```

### Obtener lista de productos
```csharp
public async Task<List<Producto>> GetProductosAsync()
{
    return await GetAsync<List<Producto>>("/api/v1/productos");
}
```

### Crear un producto (solo admin/editor)
```csharp
public async Task<Producto> CreateProductoAsync(ProductoCreate producto)
{
    return await PostAsync<Producto>("/api/v1/productos", producto);
}
```

### Ajustar stock (entrada/salida)
```csharp
public async Task<string> AjustarStockAsync(int productoId, int cantidad, string tipo)
{
    var endpoint = $"/api/v1/productos/{productoId}/stock?cantidad={cantidad}&tipo={tipo}";
    return await PatchAsync<string>(endpoint, null);
}
```

### Uso dentro de un formulario
```csharp
private ApiService _api = new ApiService();

private async void btnLogin_Click(object sender, EventArgs e)
{
    try
    {
        var login = await _api.LoginAsync(txtUser.Text, txtPass.Text);
        _api.SetToken(login.access_token);
        
        var productos = await _api.GetProductosAsync();
        dataGridView1.DataSource = productos;
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}");
    }
}
```

---

## 8. Manejo de Errores y Códigos de Estado HTTP

La API puede devolver códigos como:
- `200 OK` → Todo bien.
- `201 Created` → Recurso creado.
- `400 Bad Request` → Datos inválidos (ej. stock negativo).
- `401 Unauthorized` → Falta token o token inválido.
- `403 Forbidden` → No tienes permiso (rol incorrecto).
- `404 Not Found` → Recurso no existe.
- `422 Unprocessable Entity` → Validación falló (ej. contraseña débil).

En tu código, **captura las excepciones** y muestra mensajes amigables:
```csharp
catch (HttpRequestException ex)
{
    if (ex.Message.Contains("401"))
        MessageBox.Show("Sesión expirada. Vuelve a iniciar sesión.");
    else
        MessageBox.Show($"Error de comunicación: {ex.Message}");
}
```

---

## 9. Persistencia del Token (Opcional)

Para que el usuario no tenga que loguearse cada vez que abre la app, guarda el token de forma segura.

```csharp
// Guardar
Properties.Settings.Default.Token = token;
Properties.Settings.Default.Save();

// Cargar al iniciar
string token = Properties.Settings.Default.Token;
if (!string.IsNullOrEmpty(token))
    _api.SetToken(token);
```

---

## 10. Buenas Prácticas Finales

| Práctica | Por qué |
|----------|---------|
| Reutilizar `HttpClient` | Evita agotar puertos y mejora rendimiento. |
| No bloquear la UI con `.Result` o `.Wait()` | Usa `await` siempre. |
| Usar `CancellationToken` | Permite cancelar peticiones largas si el usuario cierra la ventana. |
| Separar en capas (Models, Services, Forms) | Código más limpio, testeable y mantenible. |
| Validar entrada antes de enviar a la API | Reduce errores y carga innecesaria. |
| Mostrar mensajes de error concretos | Mejor experiencia de usuario. |
