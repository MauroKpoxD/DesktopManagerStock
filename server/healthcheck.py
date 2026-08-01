"""
Script de healthcheck usado por el HEALTHCHECK de Docker.

Se extrajo a un archivo separado en vez de un one-liner inline en el
Dockerfile para evitar problemas de escapado de comillas anidadas (Docker
HEALTHCHECK en forma shell -> /bin/sh -> python -c "...") y para que sea
legible y fácil de probar por separado.
"""
import os
import sys
import urllib.request

port = os.environ.get("API_PORT", "8000")
url = f"http://localhost:{port}/api/v1/health"

try:
    with urllib.request.urlopen(url, timeout=4) as response:
        sys.exit(0 if response.getcode() == 200 else 1)
except Exception:
    sys.exit(1)
