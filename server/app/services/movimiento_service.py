"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Funciones para registrar y consultar movimientos de stock
"""

from sqlalchemy.orm import Session
from app.models.movimiento import MovimientoDB
from app.schemas.movimiento import MovimientoBase
from typing import Optional

# ------------------------------------------------------------

def registrar_movimiento(db: Session, movimiento: MovimientoBase) -> MovimientoDB:
    """Registra un nuevo movimiento en la base de datos."""
    db_mov = MovimientoDB(**movimiento.model_dump())
    db.add(db_mov)
    db.commit()
    db.refresh(db_mov)
    return db_mov

# ------------------------------------------------------------

def get_movimiento_by_id(db: Session, movimiento_id: int) -> Optional[MovimientoDB]:
    return db.query(MovimientoDB).filter(MovimientoDB.id == movimiento_id).first()

# ------------------------------------------------------------

def get_movimientos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    producto_id: Optional[int] = None,
    tipo: Optional[str] = None
):
    """Lista movimientos con paginación y filtros opcionales."""
    query = db.query(MovimientoDB)
    if producto_id is not None:
        query = query.filter(MovimientoDB.producto_id == producto_id)
    if tipo is not None:
        query = query.filter(MovimientoDB.tipo == tipo)
    return query.order_by(MovimientoDB.fecha_hora.desc()).offset(skip).limit(limit).all()

# ------------------------------------------------------------
def get_movimientos_por_rango_ids(db: Session, id_desde: int, id_hasta: int):
    return db.query(MovimientoDB).filter(
        MovimientoDB.id >= id_desde,
        MovimientoDB.id <= id_hasta
    ).order_by(MovimientoDB.id).all()