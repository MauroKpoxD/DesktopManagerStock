<h1 align="center">
  <img src="assets/cartel_logotipo.png" width="1000">
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue">
  <img src="https://img.shields.io/badge/Java-17-red">
  <img src="https://img.shields.io/badge/FastAPI-0.100-green">
  <img src="https://img.shields.io/badge/license-APACHE2.0-lightgrey">
  <img src="https://img.shields.io/badge/version-0.1.1-blue">
</p>

<!-- Sistema de Stock -->
<p align="center">
  <img src="assets/cartel_sistemadestockinventario_chico.png" width="850">
</p>

<p align="center">
  <b>Sistema de gestión de inventario y stock para escritorio</b><br>
  desarrollado con <b>Python/Java</b> + <b>API REST</b>.
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
  <li>✅ Autenticación segura de usuario</li>
</ul>

<!-- Próximas características -->
<h2>⏳ Próximas características (en desarrollo)</h2>

<ul>
  <li>⏳ Entradas y salidas de inventario</li>
  <li>⏳ Reportes en PDF/Excel</li>
  <li>⏳ Cálculo de ganancias/pérdidas</li>
  <li>⏳ Impresión de etiquetas y comprobantes</li>
  <li>⏳ Mejora de interfaz visual</li>
</ul>

<!-- Futuras características -->
<h2>🔮 Futuras características</h2>

<ul>
  <li>📦 Módulo de proveedores</li>
  <li>📦 Códigos de barras</li>
  <li>📦 Backup automático</li>
  <li>📦 Modo claro/oscuro</li>
  <li>📦 Facturación electrónica</li>
  <li>📦 Múltiples sucursales</li>
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
        <li>FastAPI</li>
        <li>SQLAlchemy</li>
        <li>SQLite</li>
      </ul>
    </td>
    <td valign="top" width="33%">
      <h3>☕ Frontend (Java)</h3>
      <ul>
        <li>Java 17+</li>
        <li>Swing</li>
        <li>HttpClient</li>
        <li>API Consumible</li>
      </ul>
    </td>
    <td valign="top" width="33%">
      <h3>🔧 Herramientas</h3>
      <ul>
        <li>Git & GitHub</li>
        <li>Maven</li>
        <li>FastAPI /docs</li>
        <li>Docker (opcional)</li>
      </ul>
    </td>
   </tr>
</table>

<hr>

<!-- Requisitos e instalación -->
<h2>📋 Requisitos previos</h2>

<ul>
  <li>Python 3.11+</li>
  <li>Java JDK 17+</li>
  <li>Maven 3.8+</li>
  <li>SQLite3</li>
  <li>Git (opcional para el git clone o sino descargar el .zip desde el repositorio)</li>
</ul>

<h2>📥 Instalación y configuración</h2>

<pre>
<code>git clone https://github.com/MauroKpoxD/DesktopManagerStock.git
cd DesktopManagerStock</code>
</pre>

<h2>💻 Ejecución local</h2>

<h3>Backend (API)</h3>
<pre>
<code>cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# La API corre en http://localhost:8000
# Documentación: http://localhost:8000/docs</code>
# Proximamente se dejará un dockerfile / exe
</pre>

<h3>Frontend (Cliente)</h3>
<pre>
<code>cd frontend
mvn clean install
java -jar target/desktop-stock.jar</code>
# En releases se adjuntará un .exe generico para no compilar a mano proximamente
</pre>

<h2>⚙️ Configuración</h2>

<p>Crea un archivo <code>.env</code> en la raíz del backend:</p>

<pre>
<code>DATABASE_URL=sqlite:///./stock.db
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true
API_VERSION=1.0.0
SECRET_KEY=token123
STOCK_ALERT_THRESHOLD=3</code>
</pre>

<h2>📡 Endpoints principales</h2>

<table border="1" cellpadding="8" cellspacing="0">
  <thead>
    <tr>
      <th>Método</th>
      <th>Endpoint</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>GET</b></td>
      <td>/productos</td>
      <td>Listar todos</td>
    </tr>
    <tr>
      <td><b>POST</b></td>
      <td>/productos</td>
      <td>Crear nuevo</td>
    </tr>
    <tr>
      <td><b>PUT</b></td>
      <td>/productos/{id}</td>
      <td>Actualizar stock</td>
    </tr>
    <tr>
      <td><b>DELETE</b></td>
      <td>/productos/{id}</td>
      <td>Eliminar</td>
    </tr>
  </tbody>
</table>

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
