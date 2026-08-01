"""
Esquemas para opciones de reportes.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReporteOpciones(BaseModel):
    formato: str  # "pdf" o "excel"
    umbral: Optional[int] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    producto_id: Optional[int] = None