<h1 align="center">
  <img src="assets/cartel_logotipo.png" width="1000">
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue">
  <img src="https://img.shields.io/badge/.NET-10-purple">
  <img src="https://img.shields.io/badge/FastAPI-0.136-green">
  <img src="https://img.shields.io/badge/license-APACHE2.0-lightgrey">
  <img src="https://img.shields.io/badge/version-0.3.1-blue">
  <img src="https://img.shields.io/badge/Docker-Ready-blue">
</p>

<!-- Sistema de Stock -->
<p align="center">
  <img src="assets/cartel_sistemadestockinventario_chico.png" width="850">
</p>

<p align="center">
  <b>Sistema de gestión de inventario y stock para escritorio</b><br>
  desarrollado con <b>Python</b> (backend API) + <b>.NET 10</b> (frontend Windows Forms).
</p>

<hr>

<!-- Lenguajes -->
<h2 align="center">Lenguajes utilizados</h2>
<p align="center">
  <img src="assets/cartel_lenguajes_usados.png" width="750">
</p>

<hr>

<!-- Características implementadas -->
<h2>✅ Características (implementadas)</h2>

<ul>
  <li>✅ Gestión de productos (alta, baja, modificación)</li>
  <li>✅ Control de stock mínimo y máximo</li>
  <li>✅ Alertas de stock bajo</li>
  <li>✅ Autenticación segura con JWT y roles (admin, editor, lector)</li>
  <li>✅ Validaciones de seguridad: registro forzado a rol "lector", cantidad positiva, respeto de stock máximo</li>
  <li>✅ Paginación en listado de productos y movimientos</li>
  <li>✅ Índices en base de datos para consultas rápidas</li>
  <li>✅ <strong>Historial de movimientos de stock</strong> (auditoría de entradas/salidas)</li>
  <li>✅ <strong>Reportes en PDF y Excel</strong> (productos, stock bajo, movimientos)</li>
  <li>✅ Rate limiting en login y registro (protección contra fuerza bruta)</li>
  <li>✅ Logging estructurado de eventos de seguridad y operaciones críticas</li>
  <li>✅ Validación de contraseña fuerte (mayúscula, número, carácter especial)</li>
  <li>✅ Tests unitarios y de integración (41 tests, 100% de funcionalidades cubiertas)</li>
  <li>✅ <strong>Despliegue con Docker</strong> (docker-compose)</li>
  <li>✅ <strong>Scripts de automatización</strong> para Windows (PowerShell) y Linux (Bash)</li>
  <li>✅ <strong>Healthcheck</strong> para monitoreo del contenedor</li>
  <li>✅ <strong>Usuario no root</strong> en contenedor para mayor seguridad</li>
</ul>

<!-- Próximas características (en desarrollo) -->
<h2>⏳ Próximas características (en desarrollo)</h2>

<ul>
  <li>⏳ Refresh tokens para sesiones más largas sin re-login</li>
  <li>⏳ Reportes avanzados (gráficos, resúmenes mensuales)</li>
  <li>⏳ Integración con frontend .NET (ya en desarrollo)</li>
  <li>⏳ Despliegue con HTTPS mediante nginx-proxy-manager</li>
</ul>

<hr>

<!-- Cartel de API REST -->
<p align="center">
  <img src="assets/cartel_modelo_apirest.png" width="800">
</p>

<!-- Tecnologías en tabla -->
<h2>🛠️ Tecnologías utilizadas</h2>

<table>
  <tr>
    <td valign="top" width="33%">
      <h3>🐍 Backend (Python)</h3>
      <ul>
        <li>Python 3.11+</li>
        <li>FastAPI 0.136</li>
        <li>SQLAlchemy 2.0</li>
        <li>SQLite</li>
        <li>ReportLab (PDF)</li>
        <li>OpenPyXL (Excel)</li>
        <li>python-jose (JWT)</li>
        <li>passlib (bcrypt)</li>
        <li>slowapi (rate limiting)</li>
      </ul>
    </td>
    <td valign="top" width="33%">
      <h3>🖥️ Frontend (.NET 10)</h3>
      <ul>
        <li>.NET 10</li>
        <li>Windows Forms</li>
        <li>HttpClient (consumo de API)</li>
      </ul>
    </td>
    <td valign="top" width="33%">
      <h3>🔧 Herramientas</h3>
      <ul>
        <li>Git & GitHub</li>
        <li>Visual Studio 2022</li>
        <li>FastAPI /docs</li>
        <li>Docker & Docker Compose</li>
        <li>pytest / coverage</li>
        <li>PowerShell / Bash</li>
      </ul>
    </td>
   </tr>
</table>

<hr>

<!-- Requisitos e instalación -->
<h2>📋 Requisitos previos</h2>

<ul>
  <li>Python 3.11+</li>
  <li>.NET 10 SDK (para compilar el frontend)</li>
  <li>SQLite3</li>
  <li>Git (opcional)</li>
  <li>Docker y Docker Compose (opcional, para despliegue)</li>
</ul>

<h2>📥 Instalación y configuración</h2>

<pre>
<code>git clone https://github.com/MauroKpoxD/DesktopManagerStock.git
cd DesktopManagerStock</code>
</pre>

<h2>💻 Ejecución local</h2>

<h3>Backend (API)</h3>
<pre>
<code>cd server
pip install -r requirements.txt
# Configurar .env (copiar de .env.example)
cp .env.example .env
# Editar .env con tus variables
python main.py
# La API corre en http://localhost:8000
# Documentación interactiva: http://localhost:8000/docs</code>
</pre>

<h3>Frontend (Cliente .NET Windows Forms) <span style="background-color: #ffcc00; color: #333; padding: 2px 8px; border-radius: 4px; font-size: 0.7em;">Próximamente</span></h3>
<pre>
<code>cd client
dotnet build
dotnet run --project DesktopStock.csproj</code>
</pre>
<p><del>O abre la solución en Visual Studio 2022 y ejecuta.</del> <strong>Esta sección está en desarrollo activo.</strong></p>

<h2>🐳 Despliegue con Docker</h2>

<h3>Opción 1: Script automático (recomendado)</h3>
<pre>
<code>cd scripts
chmod +x deploy_api.sh
./deploy_api.sh</code>
</pre>
<p>Este script instala dependencias, clona el repo, configura .env y levanta el contenedor automáticamente.</p>

<h3>Opción 2: Manual</h3>
<pre>
<code>cd server
docker compose up -d --build
docker compose logs -f</code>
</pre>

<h3>Comandos útiles de Docker</h3>
<pre>
<code># Detener el contenedor
docker compose down

# Ver logs
docker compose logs -f

# Reconstruir después de cambios
docker compose up -d --build

# Ver estado
docker compose ps</code>
</pre>

<h2>📜 Scripts de automatización</h2>

<p>El proyecto incluye scripts para facilitar el despliegue en diferentes sistemas:</p>

<table>
  <tr>
    <th>Script</th>
    <th>Sistema</th>
    <th>Descripción</th>
  </tr>
  <tr>
    <td><code>scripts/deploy_api.sh</code></td>
    <td>Linux / macOS</td>
    <td>Despliegue completo con Docker (instala dependencias, clona, configura y levanta)</td>
  </tr>
  <tr>
    <td><code>scripts/levantar_servicio_python.bash</code></td>
    <td>Linux / macOS</td>
    <td>Levanta el servidor directamente sin Docker (modo desarrollo)</td>
  </tr>
  <tr>
    <td><code>scripts/levantar_docker.ps1</code></td>
    <td>Windows PowerShell</td>
    <td>Levanta el contenedor con docker-compose</td>
  </tr>
  <tr>
    <td><code>scripts/levantar_servicio.ps1</code></td>
    <td>Windows PowerShell</td>
    <td>Levanta el servidor directamente sin Docker (modo desarrollo)</td>
  </tr>
</table>

<h2>⚙️ Configuración</h2>

<p>Crea un archivo <code>.env</code> en la carpeta <code>server/</code> (puedes copiar de <code>.env.example</code>):</p>

<pre>
<code># Generar una SECRET_KEY con: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Base de datos
DATABASE_URL=sqlite:///./stock.db
DB_ECHO=False
RUN_SEEDER=false

# API
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true
API_VERSION=0.3.1

# Stock
STOCK_ALERT_THRESHOLD=5

# CORS (para frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Rate limiting
RATE_LIMIT_ENABLED=true
LOGIN_RATE_LIMIT=5/minute
REGISTER_RATE_LIMIT=2/minute

# Entorno (development / production)
ENVIRONMENT=production</code>
</pre>

<h2>🧪 Tests</h2>

<p>Para ejecutar la suite de pruebas:</p>
<pre>
<code>cd server
pytest tests/ -v</code>
</pre>
<p>Resultado actual: <strong>41 passed, 1 skipped, 2 warnings</strong> (cobertura completa de funcionalidades críticas).</p>

<h2>📡 Documentación de la API</h2>

<p>La documentación completa de la API REST (endpoints, autenticación, esquemas, ejemplos) se encuentra en el archivo:</p>

<p align="center">
  <a href="docs/API_DOCS.md"><strong>📘 docs/API_DOCS.md</strong></a>
</p>

<p>Además, una vez que el backend esté corriendo, puedes explorar la documentación interactiva generada automáticamente por FastAPI:</p>

<ul>
  <li><strong>Swagger UI</strong>: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a></li>
  <li><strong>ReDoc</strong>: <a href="http://localhost:8000/redoc">http://localhost:8000/redoc</a></li>
</ul>

<p><strong>Nota</strong>: En producción, se recomienda desactivar /docs para mayor seguridad.</p>

<hr>

<h2>🤝 Contribuir</h2>

<ol>
  <li>Fork el proyecto</li>
  <li>Crea tu rama (<code>git checkout -b feature/nueva-funcionalidad</code>)</li>
  <li>Commit tus cambios</li>
  <li>Push a la rama</li>
  <li>Abre un Pull Request</li>
</ol>

<h2>📄 Licencia</h2>

<p><b>APACHE 2.0</b> - ver archivo <a href="LICENSE">LICENSE</a></p>
