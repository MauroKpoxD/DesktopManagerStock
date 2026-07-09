"""
Excepciones personalizadas de la aplicación.
"""
class AppException(Exception):
    """Excepción base."""
    pass

class NotFoundError(AppException):
    """Recurso no encontrado."""
    pass

class ValidationError(AppException):
    """Error de validación de negocio."""
    pass

class ConflictError(AppException):
    """Conflicto con datos existentes (duplicados)."""
    pass

class BusinessError(AppException):
    """Error de lógica de negocio."""
    pass

class AuthenticationError(AppException):
    """Error de autenticación."""
    pass

class AuthorizationError(AppException):
    """Error de autorización."""
    pass