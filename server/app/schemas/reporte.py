"""
ÚLTIMA MODIFICACIÓN: 10/6/2025 por S4NDULOS
PROPÓSITO: Esquemas para opciones de generación de reportes
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReporteOpciones(BaseModel):
    formato: str  # "pdf" o "excel"
    umbral: Optional[int] = None  # para stock bajo
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    producto_id: Optional[int] = None