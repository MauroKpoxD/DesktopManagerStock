#!/bin/bash
# levantar_servicio.bash
# Levanta el servidor directamente con uvicorn usando el entorno virtual

set -e

# Cambiar al directorio raíz del proyecto
cd "$(dirname "$0")/.."

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
    echo "Instalando dependencias desde requirements.txt..."
    pip install -r server/requirements.txt
fi

# Cargar variables de entorno desde .env (si existe)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Ejecutar la API con uvicorn
echo "Iniciando el servidor en http://$API_HOST:$API_PORT"
cd server
python main.py
# O también: uvicorn main:app --host $API_HOST --port $API_PORT --reload $API_RELOAD