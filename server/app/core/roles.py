"""
Definición de roles y dependencia de autorización.
"""
from enum import Enum
from fastapi import Depends, HTTPException, status
from app.models.usuario import UsuarioDB
from app.core.security import get_current_active_user

class Rol(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    LECTOR = "lector"

def require_roles(allowed_roles: list[Rol]):
    def dependency(current_user: UsuarioDB = Depends(get_current_active_user)):
        if current_user.rol not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return dependency