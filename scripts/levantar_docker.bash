#!/bin/bash
# levantar_docker.bash
# Levanta el contenedor de la API usando docker-compose

set -e  # Detener si hay error

# Cambiar al directorio raíz del proyecto (donde está docker-compose.yml)
cd "$(dirname "$0")/.."

# Verificar que existe .env, si no, copiar desde .env.example
if [ ! -f .env ]; then
    echo "No se encontró .env. Copiando desde .env.example..."
    cp .env.example .env
    echo ".env creado. Revisa y ajusta las variables (especialmente SECRET_KEY)."
fi

# Construir y levantar el contenedor en segundo plano
echo "Levantando el contenedor con docker-compose..."
docker-compose up -d --build

# Mostrar estado
echo "Contenedor levantado. Estado:"
docker-compose ps

# Mostrar logs en tiempo real (opcional: comenta si no quieres logs automáticos)
echo "Mostrando logs (presiona Ctrl+C para salir sin detener el contenedor)"
docker-compose logs -f