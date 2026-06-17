# levantar_servicio.ps1
# Levanta el servidor directamente con uvicorn usando el entorno virtual

# Cambiar al directorio raíz del proyectos
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path "$ScriptDir\.."

# Verificar que existe el entorno virtual
if (-not (Test-Path -Path "venv")) {
    Write-Host "No se encontró el entorno virtual 'venv'. Creándolo..." -ForegroundColor Red
    python -m venv venv
    Write-Host "Entorno virtual creado." -ForegroundColor Green
}

# Activar el entorno virtual
& .\venv\Scripts\Activate.ps1

# Instalar dependencias si es necesario (comprobación rápida)
$fastapi = pip show fastapi 2>$null
if (-not $fastapi) {
    Write-Host "Instalando dependencias desde server\requirements.txt..." -ForegroundColor Cyan
    pip install -r server\requirements.txt
}

# Cargar variables de entorno desde server\.env (si existe) o server\.env.example
$envFile = "server\.env"
if (-not (Test-Path -Path $envFile)) {
    Write-Host "No se encontró $envFile. Usando server\.env.example como base." -ForegroundColor Yellow
    $envFile = "server\.env.example"
}
if (Test-Path -Path $envFile) {
    Get-Content -Path $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            Set-Item -Path "Env:$($matches[1])" -Value $matches[2]
        }
    }
    Write-Host "Variables de entorno cargadas desde $envFile" -ForegroundColor Green
}

# Definir valores por defecto si no están cargados
if (-not $env:API_HOST) { $env:API_HOST = "127.0.0.1" }
if (-not $env:API_PORT) { $env:API_PORT = "8000" }
if (-not $env:API_RELOAD) { $env:API_RELOAD = "true" }

# Ir a la carpeta server y ejecutar
Write-Host "Iniciando el servidor en http://$env:API_HOST`:$env:API_PORT" -ForegroundColor Green
Set-Location -Path "server"
python main.py