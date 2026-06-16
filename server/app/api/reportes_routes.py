"""
ÚLTIMA MODIFICACIÓN: 12/6/2025 por S4NDULOS
PROPÓSITO: Endpoints para generación de reportes (PDF y Excel)
           Permisos: admin o editor
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.roles import require_roles, Rol
from app.models.usuario import UsuarioDB
from app.services.reporte_service import (
    generar_reporte_productos,
    generar_reporte_stock_bajo,
    generar_reporte_movimientos
)

router = APIRouter(prefix="/api/v1/reportes", tags=["reportes"])


@router.get("/productos")
def reporte_productos(
    formato: str = Query("pdf", pattern="^(pdf|excel)$"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    """Genera reporte de todos los productos en PDF o Excel."""
    return generar_reporte_productos(db, formato)


@router.get("/stock-bajo")
def reporte_stock_bajo(
    formato: str = Query("pdf", pattern="^(pdf|excel)$"),
    umbral: Optional[int] = Query(None, description="Umbral personalizado"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    """Genera reporte de productos con stock bajo."""
    return generar_reporte_stock_bajo(db, formato, umbral)


@router.get("/movimientos")
def reporte_movimientos(
    formato: str = Query("pdf", pattern="^(pdf|excel)$"),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    producto_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    """Genera reporte de movimientos de stock con filtros opcionales."""
    return generar_reporte_movimientos(db, formato, fecha_desde, fecha_hasta, producto_id)