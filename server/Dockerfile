FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crea un usuario sin privilegios (coincide por defecto con "user: 1000:1000" en docker-compose.yml)
# y prepara los directorios de datos con los permisos correctos para que el
# contenedor no necesite ejecutarse como root.
RUN groupadd -g 1000 appuser \
    && useradd -u 1000 -g appuser -m appuser \
    && mkdir -p /app/logs /app/reports /app/usuarios \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python healthcheck.py

# Forma shell (no exec) para poder expandir ${API_PORT}; si no está definida
# (por ejemplo, corriendo el contenedor suelto sin docker-compose), usa 8000.
CMD uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-8000}
