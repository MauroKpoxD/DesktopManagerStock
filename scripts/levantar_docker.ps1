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