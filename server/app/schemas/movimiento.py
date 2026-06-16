"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Schemas Pydantic para movimientos de stock
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class MovimientoBase(BaseModel):
    producto_id: int
    tipo: str
    cantidad: int
    stock_resultante: int
    usuario_id: Optional[int] = None

class Movimiento(MovimientoBase):
    id: int
    fecha_hora: datetime

    model_config = ConfigDict(from_attributes=True)