<<<<<<< HEAD
# levantar_servicio.ps1
# Levanta el servidor directamente con uvicorn usando el entorno virtual
# Uso: .\scripts\levantar_servicio.ps1

# Cambiar al directorio raiz del proyecto
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path "$ScriptDir\.."

# Verificar que existe el directorio server
if (-not (Test-Path -Path "server")) {
    Write-Host "ERROR: No se encontro la carpeta 'server'. Ejecuta este script desde la raiz del proyecto." -ForegroundColor Red
    exit 1
}

# Verificar que existe el entorno virtual
if (-not (Test-Path -Path "venv")) {
    Write-Host "INFO: No se encontro el entorno virtual 'venv'. Creandolo..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "INFO: Entorno virtual creado." -ForegroundColor Green
}

# Activar el entorno virtual
& .\venv\Scripts\Activate.ps1

# Instalar dependencias si es necesario (comprobacion rapida)
$fastapi = pip show fastapi 2>$null
if (-not $fastapi) {
    Write-Host "INFO: Instalando dependencias desde server\requirements.txt..." -ForegroundColor Cyan
    pip install -r server\requirements.txt
}

# Crear directorio logs si no existe
if (-not (Test-Path -Path "server\logs")) {
    Write-Host "INFO: Creando directorio server\logs..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path "server\logs" -Force | Out-Null
}

# Cargar variables de entorno desde server\.env (si existe) o server\.env.example
$envFile = "server\.env"
if (-not (Test-Path -Path $envFile)) {
    Write-Host "WARNING: No se encontro $envFile. Usando server\.env.example como base." -ForegroundColor Yellow
    $envFile = "server\.env.example"
}

if (Test-Path -Path $envFile) {
    Get-Content -Path $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $nombre = $matches[1].Trim()
            $valor = $matches[2].Trim()
            # Remover comillas si existen
            if ($valor -match '^"(.*)"$' -or $valor -match "^'(.*)'$") {
                $valor = $matches[1]
            }
            Set-Item -Path "Env:$nombre" -Value $valor
        }
    }
    Write-Host "INFO: Variables de entorno cargadas desde $envFile" -ForegroundColor Green
}

# Definir valores por defecto si no estan cargados
if (-not $env:API_HOST) { $env:API_HOST = "127.0.0.1" }
if (-not $env:API_PORT) { $env:API_PORT = "8000" }

# Ir a la carpeta server y ejecutar
Write-Host "INFO: Iniciando el servidor en http://$env:API_HOST`:$env:API_PORT" -ForegroundColor Green
Set-Location -Path "server"
python main.py
=======
# levantar_docker.ps1
# Levanta el servicio con Docker Compose (build + up en segundo plano).
# Uso: .\scripts\levantar_docker.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path "$ScriptDir\..\server"

if (-not (Test-Path -Path "docker-compose.yml")) {
    Write-Host "ERROR: No se encontro 'server\docker-compose.yml'. Ejecuta este script desde su ubicacion original dentro del repo." -ForegroundColor Red
    exit 1
}

# Verificar que Docker esta disponible
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no esta instalado o no esta en el PATH. Instala Docker Desktop primero." -ForegroundColor Red
    exit 1
}

docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker esta instalado pero el daemon no responde. Abre Docker Desktop y vuelve a intentar." -ForegroundColor Red
    exit 1
}

# Verificar/crear .env
if (-not (Test-Path -Path ".env")) {
    Write-Host "WARNING: No se encontro .env. Creandolo desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "INFO: Recuerda completar SECRET_KEY y las credenciales de PostgreSQL en server\.env" -ForegroundColor Yellow
}

# Crear carpetas de datos que se montan como volumenes, para evitar problemas de permisos
foreach ($dir in @("logs", "reports", "usuarios")) {
    if (-not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Host "INFO: Construyendo y levantando contenedores (api + db) con Docker Compose..." -ForegroundColor Green
docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Fallo 'docker compose up'. Revisa los mensajes anteriores." -ForegroundColor Red
    exit 1
}

Write-Host "INFO: Estado de los contenedores:" -ForegroundColor Green
docker compose ps

Write-Host "INFO: La API estara disponible en http://localhost:$env:API_PORT una vez que el healthcheck de la base de datos pase." -ForegroundColor Green
Write-Host "INFO: Para ver los logs en tiempo real: docker compose logs -f" -ForegroundColor Cyan
>>>>>>> feature/interfaz-y-reconstruccion
