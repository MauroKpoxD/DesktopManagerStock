"""
ÚLTIMA MODIFICACIÓN: 4/6/2025 por S4NDULOS
PROPÓSITO: Schemas Pydantic para usuarios y autenticación
           Incluye validación de contraseña segura
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    rol: Optional[str] = "lector"

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def validate_password_strength(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        # Opcional: al menos un carácter especial
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None

class Usuario(UsuarioBase):
    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None