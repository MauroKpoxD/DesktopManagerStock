"""
Endpoints para generación de reportes.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
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
    return generar_reporte_productos(db, formato)

@router.get("/stock-bajo")
def reporte_stock_bajo(
    formato: str = Query("pdf", pattern="^(pdf|excel)$"),
    umbral: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
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
    return generar_reporte_movimientos(db, formato, fecha_desde, fecha_hasta, producto_id)