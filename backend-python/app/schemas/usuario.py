from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    rol: Optional[str] = "lector"

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None

class Usuario(UsuarioBase):
    id: int
    activo: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None