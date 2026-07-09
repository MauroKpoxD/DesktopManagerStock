#!/bin/bash
# levantar_servicio_python.bash
# Levanta el servidor directamente con uvicorn usando el entorno virtual

set -e

# Cambiar al directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# Verificar que existe el directorio server
if [ ! -d "server" ]; then
    echo "ERROR: No se encontró la carpeta 'server'."
    echo "       Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

# Verificar que PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    echo "WARNING: PostgreSQL no está instalado. Asegúrate de tenerlo instalado y corriendo."
    echo "       Puedes instalarlo con: sudo apt install postgresql postgresql-contrib"
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "INFO: No se encontró el entorno virtual 'venv'. Creándolo..."
    python3 -m venv venv
    echo "INFO: Entorno virtual creado."
fi

# Activar el entorno virtual
source venv/bin/activate

# Instalar dependencias si es necesario (comprobación rápida)
if ! pip show fastapi > /dev/null 2>&1; then
    echo "INFO: Instalando dependencias desde server/requirements.txt..."
    pip install -r server/requirements.txt
fi

# Crear directorio logs si no existe
mkdir -p server/logs

# Cargar variables de entorno desde server/.env (si existe)
if [ -f "server/.env" ]; then
    echo "INFO: Cargando variables desde server/.env..."
    set -a
    source server/.env
    set +a
else
    echo "WARNING: No se encontró server/.env. Usando server/.env.example como base."
    cp server/.env.example server/.env
    # Generar SECRET_KEY
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET/" server/.env
    # Generar contraseña para PostgreSQL
    DB_PASS=$(openssl rand -base64 18 | tr -dc 'a-zA-Z0-9')
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=$DB_PASS/" server/.env
    # Asegurar DB_HOST=localhost (por defecto)
    sed -i 's/^DB_HOST=.*/DB_HOST=localhost/' server/.env
    echo "INFO: .env creado con valores generados."
    # Volver a cargar
    set -a
    source server/.env
    set +a
fi

# Definir valores por defecto si no están cargados
API_HOST=${API_HOST:-127.0.0.1}
API_PORT=${API_PORT:-8000}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-desktopmanager}

# Verificar que la base de datos existe
echo "INFO: Verificando que la base de datos '$DB_NAME' existe..."
if psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "INFO: La base de datos '$DB_NAME' ya existe."
else
    echo "WARNING: La base de datos '$DB_NAME' no existe. Creándola..."
    psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -c "CREATE DATABASE $DB_NAME;" || {
        echo "ERROR: No se pudo crear la base de datos. Verifica la conexión a PostgreSQL."
        exit 1
    }
    echo "INFO: Base de datos '$DB_NAME' creada."
fi

# Ejecutar la API con uvicorn
echo "INFO: Iniciando el servidor en http://$API_HOST:$API_PORT"
cd server
python main.py