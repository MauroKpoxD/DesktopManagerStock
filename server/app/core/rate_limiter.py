"""
Configuración de rate limiter condicional.
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
            def decorator(func):
                return func
            return decorator

_limiter = Limiter(key_func=get_remote_address)
limiter = ConditionalLimiter(_limiter)