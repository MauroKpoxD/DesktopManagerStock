"""
ÚLTIMA MODIFICACIÓN: 6/6/2025 por S4NDULOS
PROPÓSITO: Configuración centralizada del rate limiter para toda la aplicación.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# aca podria(mos) agregar mas adelante mas cosas
# pensar a futuro