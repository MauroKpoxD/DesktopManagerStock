"""
Esquemas de Usuario y autenticación.
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional


def _validar_fortaleza_password(v: str) -> str:
    """
    Regla de fortaleza de contraseña compartida entre el registro y el cambio
    de contraseña. Antes solo existía en UsuarioCreate, así que un usuario
    podía cambiar su contraseña por una débil usando /auth/... (no había
    endpoint, pero cualquiera que se agregara habría heredado el problema).
    """
    if not any(char.isupper() for char in v):
        raise ValueError('La contraseña debe contener al menos una letra mayúscula')
    if not any(char.isdigit() for char in v):
        raise ValueError('La contraseña debe contener al menos un número')
    if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in v):
        raise ValueError('La contraseña debe contener al menos un carácter especial')
    return v


class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    rol: Optional[str] = "lector"

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def validate_password_strength(cls, v):
        return _validar_fortaleza_password(v)

class UsuarioUpdate(BaseModel):
    """Uso administrativo: permite cambiar el rol y activar/desactivar usuarios."""
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None

class PerfilUpdate(BaseModel):
    """Uso propio: un usuario solo puede editar su email, nunca su rol."""
    email: EmailStr

class CambioPassword(BaseModel):
    password_actual: str
    password_nueva: str = Field(..., min_length=8)

    @field_validator('password_nueva')
    def validate_password_strength(cls, v):
        return _validar_fortaleza_password(v)

class Usuario(UsuarioBase):
    id: int
    activo: bool
    model_config = ConfigDict(from_attributes=True)

class PasswordTemporal(BaseModel):
    """Respuesta de POST /usuarios/{id}/resetear-password: la contraseña
    solo se muestra en esta respuesta, no queda guardada en ningún lado."""
    usuario: Usuario
    password_temporal: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    username: str | None = None