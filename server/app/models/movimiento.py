"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Modelo SQLAlchemy para la tabla 'movimientos'
           Registra cada entrada/salida de stock para auditoría
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.database import Base

class MovimientoDB(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String, nullable=False) # entrada o salida
    cantidad = Column(Integer, nullable=False)
    stock_resultante = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_movimiento_fecha', 'fecha_hora'),
        Index('idx_movimiento_producto_fecha', 'producto_id', 'fecha_hora'),
    )