# Cliente .NET MAUI Blazor Hybrid

Este directorio contiene el frontend de **DesktopManagerStock**, desarrollado con **.NET MAUI** y **Blazor Hybrid**. La interfaz de usuario se renderiza con HTML/CSS dentro de un `BlazorWebView` nativo, lo que permite compartir la misma lógica y componentes entre Windows, macOS, Android e iOS.

---

## 📋 Requisitos previos

- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0)
- Workload de MAUI:
  ```bash
  dotnet workload install maui
  ```
- Para cada plataforma:
  - **Windows**: Windows 10/11 con el workload de Windows App SDK (incluido en `maui`).
  - **macOS (Mac Catalyst)**: Mac con Xcode.
  - **Android**: Android SDK (se instala con el workload o con Android Studio).
  - **iOS**: Mac con Xcode (no se puede compilar desde Windows/Linux; se puede usar "Pair to Mac" desde Visual Studio).

No es necesario instalar todos los workloads si solo compilás para una plataforma específica.

---

## ⚙️ Configuración de la API

Por defecto, el cliente apunta a `http://localhost:8000/api/v1`. Podés cambiarlo:

1. **Desde la UI**: Una vez logueado, andá a **Mi perfil → Conexión con la API**.
2. **Editando el código**: Modificá la constante `DefaultUrl` en `Services/ApiSettings.cs`.

### ⚠️ Importante en emuladores y dispositivos reales

| Plataforma | URL para llegar al host |
|------------|--------------------------|
| Emulador Android | `http://10.0.2.2:8000/api/v1` |
| Dispositivo físico (Android/iOS) o simulador iOS en otra máquina | Usá la IP local de tu PC (ej. `http://192.168.1.50:8000/api/v1`), y asegurate que el backend escuche en `0.0.0.0` (en `server/.env`). |

> **Nota:** En desarrollo la API usa HTTP plano. Android, iOS y MacCatalyst bloquean ese tráfico por defecto. Ya está habilitado en los archivos de plataforma (`usesCleartextTraffic` en Android, `NSAllowsArbitraryLoads` en iOS/MacCatalyst). **Deshabilitá estas opciones antes de distribuir la app en producción.**

---

## 🛠️ Compilar y ejecutar

Parado en la carpeta `client/`, ejecutá:

```bash
# Restaurar dependencias
dotnet restore

# Windows
dotnet build -f net10.0-windows10.0.19041.0
dotnet run -f net10.0-windows10.0.19041.0

# Mac Catalyst (desde un Mac)
dotnet build -f net10.0-maccatalyst
dotnet run -f net10.0-maccatalyst

# Android (con un emulador o dispositivo conectado)
dotnet build -f net10.0-android
dotnet build -f net10.0-android -t:Run

# iOS (desde un Mac, con simulador)
dotnet build -f net10.0-ios -t:Run
```

También podés abrir el proyecto con **Visual Studio 2022** o **Rider**, seleccionar el dispositivo/emulador y presionar `F5`.

---

## 📁 Estructura del proyecto

```
client/
├── DesktopManagerStock.csproj   # Proyecto multi-target (android;ios;maccatalyst;windows)
├── MauiProgram.cs               # Configuración de DI y servicios
├── App.xaml(.cs)                # Arranque de la app MAUI
├── AppShell.xaml(.cs)           # Shell principal (contiene el BlazorWebView)
├── MainPage.xaml(.cs)           # Página que aloja el BlazorWebView
├── Components/
│   ├── Routes.razor             # Decide Login vs MainLayout y restaura sesión
│   ├── Layout/                  # NavMenu y MainLayout (sidebar + contenido)
│   ├── Pages/                   # Cada sección: Dashboard, Productos, Movimientos, etc.
│   └── Shared/                  # Diálogos reutilizables (modales, toasts, skeletons)
├── Services/                    # Servicios de API, autenticación, navegación, etc.
├── Models/                      # DTOs (mapean a los schemas de Pydantic del backend)
├── Platforms/                   # Código específico para cada plataforma (Android, iOS, etc.)
├── Resources/                   # Íconos, splash screen, estilos nativos
└── wwwroot/                     # Archivos estáticos: CSS, imágenes, index.html
```

---

## 🔐 Autenticación y manejo de sesión

- **Access token**: se guarda en memoria (`AuthTokenStore.AccessToken`).
- **Refresh token**: se almacena de forma cifrada con `SecureStorage` (nunca en `Preferences`).
- **Renovación automática**: `AuthDelegatingHandler` intercepta cada request; ante un 401, intenta renovar el token usando el refresh token y reintenta la petición.
- **Restauración de sesión**: al abrir la app, `Routes.razor` intenta restaurar la sesión con el refresh token guardado, evitando que el usuario tenga que loguearse cada vez.

---

## 🎨 Personalización

### Íconos y splash screen

Los archivos en `Resources/AppIcon/` y `Resources/Splash/` son placeholders. Reemplazalos con tus propios SVG (podés usar `assets/logo_simple.png` de la raíz como base).

### Tema claro/oscuro

El tema se controla desde **Mi perfil → Apariencia** y se persiste en `Preferences` (`tema_claro`). El login y la pantalla de arranque mantienen el tema oscuro de marca.

### Fuentes

Por defecto se usa **Poppins** (cargada desde Google Fonts). Si no hay conexión, cae a la pila de fuentes del sistema. Si querés usar otra fuente, modificá `wwwroot/index.html` y el CSS.

---

## 🧪 Pruebas y depuración

- **Logs de la API**: se muestran en la consola del backend.
- **Errores del cliente**: se muestran en toasts (notificaciones flotantes) y en la consola de desarrollo (F12 en el WebView si está habilitado).
- **Depuración remota en Android**: podés usar `chrome://inspect` si la app está en modo desarrollo.

---

## 🔧 Problemas comunes

| Problema | Solución |
|----------|----------|
| La app no arranca en Android / iOS | Verificá que el emulador o dispositivo tenga permisos de red y que la URL de la API sea accesible desde él. |
| La API responde 401 aunque el usuario está logueado | El refresh token puede haber expirado. Limpiá la sesión (desde la UI o borrando SecureStorage). |
| El WebView no muestra la UI | Revisá que `wwwroot/index.html` y el CSS estén correctamente referenciados. |
| Los íconos no se ven | Asegurate de que `Resources/Images/logo.png` exista y que las rutas en el código sean correctas. |

---

## 📚 Más información

- [README principal del proyecto](../README.md)
- [Documentación de la API](../docs/API_DOCS.md)
- [Mejoras y correcciones aplicadas](../docs/MEJORAS.md)
```

---

## 🔄 Actualizar el README raíz

Ahora, en el `README.md` de la raíz, buscá las referencias a `client/README.md` y reemplazalas por `docs/cliente.md`. También podés agregar un enlace en la sección de documentación:

```markdown
## 📚 Documentación adicional

- [Guía del cliente .NET MAUI](docs/cliente.md)
- [Mejoras y correcciones](docs/MEJORAS.md)
```

---

## 📂 Crear el archivo y hacer commit

```powershell
# Crear el archivo docs/cliente.md con el contenido de arriba
# (usá tu editor favorito para pegar el contenido)

# Agregar los cambios
git add docs/cliente.md README.md

# Commitear
git commit -m "Docs: agregar guía técnica del cliente en docs/cliente.md"

# Pushear
git push origin main
```