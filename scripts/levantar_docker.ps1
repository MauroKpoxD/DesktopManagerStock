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
