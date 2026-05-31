"""
ÚLTIMA MODIFICACIÓN: 30/5/2025 por S4NDULOS
PROPÓSITO: Define el modelo SQLAlchemy para la tabla 'usuarios'.
           Incluye autenticación (username, email, hashed_password) y roles.
"""

from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, default="lector")  # admin, editor, lector
    activo = Column(Boolean, default=True)