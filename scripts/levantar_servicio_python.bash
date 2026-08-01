#!/bin/bash
# levantar_servicio_python.bash
# Levanta el servidor directamente con uvicorn usando el entorno virtual

set -e

# Cambiar al directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# Verificar que existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "No se encontró el entorno virtual 'venv'. Creándolo..."
    python -m venv venv
    echo "Entorno virtual creado."
fi

# Activar el entorno virtual
source venv/bin/activate

# Instalar dependencias si es necesario (comprobación rápida)
if ! pip show fastapi > /dev/null 2>&1; then
    echo "Instalando dependencias desde server/requirements.txt..."
    pip install -r server/requirements.txt
fi

# Cargar variables de entorno desde server/.env (si existe)
if [ -f "server/.env" ]; then
    echo "Cargando variables desde server/.env..."
    set -a
    source server/.env
    set +a
else
    echo "No se encontró server/.env. Usando valores por defecto."
    export API_HOST="127.0.0.1"
    export API_PORT="8000"
fi

# Asegurar que las variables tengan valores
API_HOST=${API_HOST:-127.0.0.1}
API_PORT=${API_PORT:-8000}

# Crear directorio logs si no existe y dar permisos
mkdir -p server/logs
chmod 755 server/logs

# Ejecutar la API con uvicorn
echo "Iniciando el servidor en http://$API_HOST:$API_PORT"
cd server
python main.py