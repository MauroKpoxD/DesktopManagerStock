"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Modelo SQLAlchemy para la tabla 'productos'
           Define campos: id, nombre, precio, stock, stock_minimo, stock_maximo
           Agregado índice en stock para mejorar consultas de stock bajo.
"""

from sqlalchemy import Column, Integer, String, Float, Index
from app.core.database import Base

class ProductoDB(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)
    stock_maximo = Column(Integer, default=100)

    __table_args__ = (Index('idx_producto_stock', 'stock'),)