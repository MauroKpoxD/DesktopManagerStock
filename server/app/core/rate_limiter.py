"""
ÚLTIMA MODIFICACIÓN: 11/6/2025 por S4NDULOS
PROPÓSITO: Configuración centralizada del rate limiter para toda la aplicación
           Soporta desactivación condicional (rate_limit_enabled=false) devolviendo un decorador nulo
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

class ConditionalLimiter:
    def __init__(self, limiter: Limiter):
        self._limiter = limiter
        self._enabled = settings.rate_limit_enabled

    def limit(self, *args, **kwargs):
        if self._enabled:
            return self._limiter.limit(*args, **kwargs)
        else:
            # Decorador nulo: retorna la función original sin modificar
            def decorator(func):
                return func
            return decorator

_limiter = Limiter(key_func=get_remote_address)
limiter = ConditionalLimiter(_limiter)