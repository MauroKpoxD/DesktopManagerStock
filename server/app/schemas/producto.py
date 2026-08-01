"""
Esquemas de Producto con validaciones.
"""
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock: int
    stock_minimo: Optional[int] = 5
    stock_maximo: Optional[int] = 100
    categoria: Optional[str] = None
    sku: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    proveedor_contacto: Optional[str] = None

    @field_validator('precio')
    def validar_precio(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a cero')
        return v

    @field_validator('stock')
    def validar_stock(cls, v):
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v

    @field_validator('stock_minimo')
    def validar_stock_minimo(cls, v):
        if v is not None and v < 0:
            raise ValueError('El stock mínimo no puede ser negativo')
        return v

    @field_validator('stock_maximo')
    def validar_stock_maximo(cls, v):
        if v is not None and v < 0:
            raise ValueError('El stock máximo no puede ser negativo')
        return v

    @model_validator(mode='after')
    def validar_rangos(self):
        if self.stock_maximo < self.stock_minimo:
            raise ValueError('El stock máximo debe ser mayor o igual al mínimo')
        if self.stock > self.stock_maximo:
            raise ValueError(f'El stock inicial no puede superar el máximo de {self.stock_maximo}')
        return self

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    stock_minimo: Optional[int] = None
    stock_maximo: Optional[int] = None
    categoria: Optional[str] = None
    sku: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    proveedor_contacto: Optional[str] = None
    # Permite reactivar un producto previamente desactivado (ver DELETE /productos/{id}).
    activo: Optional[bool] = None

    @field_validator('precio')
    def validar_precio(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El precio debe ser mayor a cero')
        return v

    @field_validator('stock_minimo')
    def validar_stock_minimo(cls, v):
        if v is not None and v < 0:
            raise ValueError('El stock mínimo no puede ser negativo')
        return v

    @field_validator('stock_maximo')
    def validar_stock_maximo(cls, v):
        if v is not None and v < 0:
            raise ValueError('El stock máximo no puede ser negativo')
        return v

    @model_validator(mode='after')
    def validar_rangos(self):
        if self.stock_minimo is not None and self.stock_maximo is not None:
            if self.stock_maximo < self.stock_minimo:
                raise ValueError('El stock máximo debe ser mayor o igual al mínimo')
        return self

class Producto(ProductoBase):
    id: int
    activo: bool = True
    model_config = ConfigDict(from_attributes=True)

class ImportacionOmitida(BaseModel):
    fila: int
    motivo: str

class ImportacionResultado(BaseModel):
    total_filas: int
    creados: int
    productos_creados: list[str]
    omitidos: list[ImportacionOmitida]