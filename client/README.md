# DesktopManagerStock — Cliente (.NET MAUI Blazor Hybrid)

Cliente multi-plataforma (Windows, macOS, Android, iOS) escrito en C# con la
UI en Razor Components (HTML + CSS), consumiendo la API del backend
(`../server`). Es "Blazor Hybrid": la interfaz es HTML/CSS renderizado en un
`BlazorWebView` embebido dentro de una app nativa de MAUI, no una app web.

## Diseño visual

- Tipografía: **Poppins** (Google Fonts, con fallback a fuentes del sistema si no hay internet al cargar).
- Íconos: SVG propios dibujados a mano (`Components/Shared/Icon.razor`), sin emojis ni librerías de íconos de terceros.
- El logo de `assets/logo_sin_fondo.png` (del repo) se usa como marca en el sidebar y el login.
- Pantalla de **Inicio/Dashboard** con resumen (productos activos, valor de inventario, alertas de stock bajo, gráfico de actividad semanal, actividad reciente) como landing page después del login.
- **Tema claro/oscuro** conmutable desde Mi perfil (persistido en el dispositivo).
- Notificaciones flotantes (toasts) al confirmar acciones.

## Funcionalidad

- CRUD de productos con categoría, SKU y proveedor (todos opcionales, con autocompletado de categoría) y filtro por categoría (se recuerda entre visitas).
- Búsqueda, orden de columnas y **paginación** en la tabla de productos (en memoria, sobre hasta 500 productos cargados) y de movimientos (paginación real contra el servidor).
- **Selección múltiple y acciones en lote**: cambiar categoría o desactivar varios productos a la vez.
- **Importar / Exportar CSV**: exportar lo filtrado/visible, o importar un catálogo entero de una sola vez (fila por fila; las filas con error se omiten sin abortar el resto).
- **Historial por producto**: botón "Ver historial" abre una ficha con los datos del producto y el timeline completo de sus movimientos.
- **Deshacer** un ajuste de stock: el toast de confirmación incluye un botón "Deshacer" por unos segundos.
- **Reabastecer rápido** desde el Dashboard, en la lista "Para reponer".
- Dashboard con gráfico de actividad semanal y de valor de inventario por categoría.
- Alta de usuarios por un admin (usuario, email, contraseña y rol) desde **Usuarios → Nuevo usuario**.
- **Restablecer contraseña** de un usuario (genera una temporal) para cuando alguien pierde acceso a la suya.
- Alerta de stock bajo visible como badge en el menú lateral; aviso claro cuando la sesión expira (en vez de mandar al login en silencio).
- Atajos: **Esc** cierra cualquier modal, **Enter** confirma los formularios.
- Loading skeletons en las tablas principales en vez de un spinner genérico.

## Requisitos

- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0)
- El **workload de MAUI**:
  ```
  dotnet workload install maui
  ```
- Para compilar **Android**: Android SDK (se instala junto con el workload,
  o vía Visual Studio / Android Studio).
- Para compilar **iOS**: un Mac con Xcode instalado (no se puede compilar
  iOS desde Windows/Linux; si estás en Windows, podés emparejar con un Mac
  remoto usando "Pair to Mac" desde Visual Studio, o directamente omitir
  esta plataforma).
- Para compilar **Windows**: Windows 10/11 con el workload de Windows App SDK
  (lo instala `dotnet workload install maui`).
- Para compilar **Mac Catalyst**: un Mac.

No hace falta tener instalados los 4 workloads a la vez: compilá solo la
plataforma que te interese indicando `-f` (framework objetivo), ver abajo.

## Configurar la URL de la API

Por defecto la app apunta a `http://localhost:8000/api/v1` (el backend
corriendo local). Se puede cambiar sin recompilar desde la pantalla
**Mi perfil → Conexión con la API** una vez logueado, o antes del primer
build editando el valor por defecto en `Services/ApiSettings.cs`.

**Importante en dispositivos/emuladores reales:**
- **Emulador de Android**: `localhost` desde el emulador NO es tu PC, es el
  propio emulador. Usá `http://10.0.2.2:8000/api/v1` para llegar al host.
- **Dispositivo físico (Android/iOS) o simulador de iOS en un Mac distinto**:
  usá la IP de red local de la máquina donde corre el backend, por ejemplo
  `http://192.168.1.50:8000/api/v1`, y asegurate de que el backend escuche
  en `0.0.0.0` (`API_HOST=0.0.0.0` en `server/.env`) y no solo en
  `127.0.0.1`.
- Como la API en desarrollo corre en HTTP simple (sin certificado), Android
  e iOS/MacCatalyst bloquean ese tráfico por defecto. Ya está habilitado
  para desarrollo en `Platforms/Android/AndroidManifest.xml`
  (`usesCleartextTraffic`) y en los `Info.plist` de iOS/MacCatalyst
  (`NSAllowsArbitraryLoads`). **Sacá esas líneas (o pasá a HTTPS real) antes
  de distribuir la app.**

## Compilar y correr

Parado en la carpeta `client/`:

```bash
# Restaurar dependencias
dotnet restore

# Windows
dotnet build -f net10.0-windows10.0.19041.0
dotnet run -f net10.0-windows10.0.19041.0

# Mac Catalyst (desde un Mac)
dotnet build -f net10.0-maccatalyst
dotnet run -f net10.0-maccatalyst

# Android (con un emulador corriendo o dispositivo conectado)
dotnet build -f net10.0-android
dotnet build -f net10.0-android -t:Run

# iOS (desde un Mac, con simulador)
dotnet build -f net10.0-ios -t:Run
```

O simplemente abrí `DesktopManagerStock.csproj` con Visual Studio 2022
(workload ".NET Multi-platform App UI development") o Rider, elegí el
target framework/dispositivo en el selector de arriba y F5.

## Estructura

```
client/
├── DesktopManagerStock.csproj   # Multi-target: android;ios;maccatalyst;windows
├── MauiProgram.cs               # Inyección de dependencias
├── App.xaml(.cs), AppShell.xaml(.cs), MainPage.xaml(.cs)   # Bootstrapping nativo de MAUI
├── Components/
│   ├── Routes.razor             # Restaura sesión y decide Login vs MainLayout
│   ├── Layout/                  # MainLayout (sidebar) + NavMenu
│   ├── Pages/                   # Una página por sección (Productos, Movimientos, ...)
│   └── Shared/                  # Diálogos reutilizables (modal de confirmación, etc.)
├── Services/                    # Un servicio por recurso de la API + infraestructura de auth
├── Models/                      # DTOs que reflejan los schemas de Pydantic del backend
├── Platforms/                   # Boilerplate específico de cada plataforma
├── Resources/                   # Íconos, splash screen, estilos nativos, imágenes
└── wwwroot/                     # HTML/CSS de la UI (esto es lo que se ve en el BlazorWebView)
```

### Por qué no hay `@page`/enrutamiento por URL

La navegación entre secciones (Productos, Movimientos, etc.) se maneja con
un estado simple (`Services/NavigationState.cs`) en vez del `Router` de
Blazor basado en URLs. Para un panel de escritorio como este no hace falta
deep-linking ni botón "atrás del navegador", y evita una capa de
complejidad (rutas, `NavigationManager`, base href dentro del WebView) que
no aporta nada acá. Si en algún momento se necesita compartir enlaces a una
pantalla puntual, es el primer lugar para revisar.

### Autenticación

- `Services/AuthTokenStore.cs`: el `access_token` vive en memoria; el
  `refresh_token` se guarda cifrado con `SecureStorage` (nunca en
  `Preferences`, que no está cifrado).
- `Services/AuthDelegatingHandler.cs`: agrega el header `Authorization` a
  cada request y, ante un 401, intenta renovar el token automáticamente
  antes de reintentar — el resto de la app no tiene que preocuparse por
  tokens vencidos.
- Al abrir la app, `Routes.razor` intenta restaurar la sesión con el
  `refresh_token` guardado, así no hay que loguearse de nuevo cada vez.

## Íconos y splash screen

`Resources/AppIcon/appicon*.svg` y `Resources/Splash/splash.svg` son
placeholders simples (un cuadrado con el color de marca). Reemplazalos por
tu propio arte cuando quieras — `assets/logo_simple.png` en la raíz del
repo puede servir como punto de partida.

## Pendiente / ideas para seguir

- Tests unitarios de la lógica pura (parseo de errores de la API, lógica de
  renovación de token) con xUnit — no se incluyeron todavía, ver conversación.
- Modo offline con caché local (SQLite) para seguir operando sin conexión.
- Notificaciones push cuando el stock cruza el mínimo.
