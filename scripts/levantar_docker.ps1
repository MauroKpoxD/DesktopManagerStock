# levantar_docker.ps1
# Levanta el servidor con Docker usando docker-compose
# Uso: .\scripts\levantar_docker.ps1

# Cambiar al directorio raiz del proyecto
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path "$ScriptDir\.."

# Verificar que existe el directorio server
if (-not (Test-Path -Path "server")) {
    Write-Host "ERROR: No se encontro la carpeta 'server'. Ejecuta este script desde la raiz del proyecto." -ForegroundColor Red
    exit 1
}

# Verificar que Docker está instalado
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no está instalado o no está en el PATH." -ForegroundColor Red
    exit 1
}

# Verificar que docker-compose funciona
try {
    docker compose version | Out-Null
} catch {
    Write-Host "ERROR: docker-compose no está disponible. Asegúrate de tener Docker Desktop instalado." -ForegroundColor Red
    exit 1
}

# Verificar si existe el archivo .env
$envFile = "server\.env"
if (-not (Test-Path -Path $envFile)) {
    Write-Host "INFO: No se encontro $envFile. Creando desde .env.example..." -ForegroundColor Yellow
    Copy-Item "server\.env.example" -Destination $envFile

    # Generar SECRET_KEY con Python
    $secret = python -c "import secrets; print(secrets.token_urlsafe(32))" 2>$null
    if ($secret) {
        (Get-Content $envFile) -replace '^SECRET_KEY=.*', "SECRET_KEY=$secret" | Set-Content $envFile
    }

    # Generar contraseña para PostgreSQL
    $dbpass = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 18 | ForEach-Object { [char]$_ })
    (Get-Content $envFile) -replace '^DB_PASSWORD=.*', "DB_PASSWORD=$dbpass" | Set-Content $envFile

    # Cambiar DB_HOST a 'db' (nombre del servicio en docker-compose)
    (Get-Content $envFile) -replace '^DB_HOST=.*', 'DB_HOST=db' | Set-Content $envFile

    Write-Host "INFO: .env creado con valores generados." -ForegroundColor Green
} else {
    Write-Host "INFO: .env ya existe. Usando configuración existente." -ForegroundColor Green
}

# Levantar los contenedores
Write-Host "INFO: Construyendo y levantando contenedores con docker-compose..." -ForegroundColor Cyan
Set-Location -Path "server"
docker compose up -d --build

# Mostrar estado
Write-Host "`nINFO: Estado de los contenedores:" -ForegroundColor Green
docker compose ps

Write-Host "`nINFO: Logs en tiempo real (Ctrl+C para salir sin detener):" -ForegroundColor Yellow
docker compose logs -f