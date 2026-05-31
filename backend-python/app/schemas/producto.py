"""
ÚLTIMA MODIFICACIÓN: 24/05/2025 por S4NDULOS
PROPÓSITO: Schemas Pydantic para validación de datos de productos.
           Incluye ProductoBase, ProductoCreate, ProductoUpdate, Producto (respuesta).
"""

from pydantic import BaseModel
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock: int
    stock_minimo: Optional[int] = 5
    stock_maximo: Optional[int] = 100

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    stock_maximo: Optional[int] = None

class Producto(ProductoBase):
    id: int

    class Config:
        from_attributes = True