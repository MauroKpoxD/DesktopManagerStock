"""
Servicio de movimientos.
"""
from sqlalchemy.orm import Session
from app.models.movimiento import MovimientoDB
from app.schemas.movimiento import MovimientoBase
from app.core.exceptions import NotFoundError, ValidationError
from typing import Optional
from datetime import datetime, timedelta, timezone, date

def registrar_movimiento(db: Session, movimiento: MovimientoBase) -> MovimientoDB:
    if movimiento.cantidad <= 0:
        raise ValidationError("La cantidad debe ser positiva")
    db_mov = MovimientoDB(**movimiento.model_dump())
    db.add(db_mov)
    db.commit()
    db.refresh(db_mov)
    return db_mov

def obtener_movimiento_por_id(db: Session, movimiento_id: int) -> Optional[MovimientoDB]:
    mov = db.query(MovimientoDB).filter(MovimientoDB.id == movimiento_id).first()
    if not mov:
        raise NotFoundError(f"Movimiento con ID {movimiento_id} no encontrado")
    return mov

def listar_movimientos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    producto_id: Optional[int] = None,
    tipo: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None
):
    query = db.query(MovimientoDB)
    if producto_id is not None:
        query = query.filter(MovimientoDB.producto_id == producto_id)
    if tipo is not None:
        query = query.filter(MovimientoDB.tipo == tipo)
    if fecha_desde:
        query = query.filter(MovimientoDB.fecha_hora >= fecha_desde)
    if fecha_hasta:
        # Para incluir todo el día, se suma un día y se usa <
        query = query.filter(MovimientoDB.fecha_hora < fecha_hasta + timedelta(days=1))
    return query.order_by(MovimientoDB.fecha_hora.desc()).offset(skip).limit(limit).all()

def obtener_movimientos_por_rango_ids(db: Session, id_desde: int, id_hasta: int):
    if id_desde > id_hasta:
        raise ValidationError("El ID desde debe ser menor o igual al ID hasta")
    return db.query(MovimientoDB).filter(
        MovimientoDB.id >= id_desde,
        MovimientoDB.id <= id_hasta
    ).order_by(MovimientoDB.id).all()