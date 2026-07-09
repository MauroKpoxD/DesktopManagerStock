"""
Rutas principales: productos y movimientos.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.producto import Producto, ProductoCreate, ProductoUpdate
from app.schemas.movimiento import Movimiento
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.core.roles import require_roles, Rol
from app.models.usuario import UsuarioDB
from app.services.producto_service import (
    listar_productos,
    obtener_producto_por_id,
    crear_producto,
    actualizar_producto,
    eliminar_producto,
    ajustar_stock,
    obtener_productos_con_stock_bajo
)
from app.services.movimiento_service import (
    obtener_movimiento_por_id,
    listar_movimientos,
    obtener_movimientos_por_rango_ids
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError

router = APIRouter(prefix="/api/v1", tags=["productos"])

@router.get("/")
def home():
    return {
        "mensaje": "DesktopManagerStock API",
        "version": settings.api_version,
        "docs": "/docs"
    }

@router.get("/productos", response_model=list[Producto])
def get_productos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    return listar_productos(db, skip=skip, limit=limit)

@router.get("/productos/{producto_id}", response_model=Producto)
def get_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    try:
        return obtener_producto_por_id(db, producto_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
def create_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    try:
        return crear_producto(db, producto)
    except (ValidationError, ConflictError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/productos/{producto_id}", response_model=Producto)
def update_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    try:
        return actualizar_producto(db, producto_id, producto_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ValidationError, ConflictError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/productos/{producto_id}", status_code=204)
def delete_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN]))
):
    try:
        eliminar_producto(db, producto_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/productos/{producto_id}/stock")
def ajustar_stock_endpoint(
    producto_id: int,
    cantidad: int = Query(..., gt=0, description="Cantidad positiva a mover"),
    tipo: str = Query("entrada", pattern="^(entrada|salida)$", description="Tipo: 'entrada' o 'salida'"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    try:
        producto = ajustar_stock(db, producto_id, cantidad, tipo == "entrada", current_user.id)
        return {"mensaje": f"Stock actualizado. Nuevo stock: {producto.stock}"}
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/productos/stock/bajo", response_model=list[Producto])
def productos_stock_bajo(
    umbral: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    productos_db = obtener_productos_con_stock_bajo(db, umbral)
    return [Producto.model_validate(p) for p in productos_db]

# ========== RUTAS DE MOVIMIENTOS (orden corregido) ==========

@router.get("/movimientos", response_model=list[Movimiento])
def listar_movimientos_endpoint(
    skip: int = Query(0, ge=0, description="Número de movimientos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de movimientos a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    tipo: Optional[str] = Query(None, pattern="^(entrada|salida)$", description="Filtrar por tipo"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    return listar_movimientos(db, skip=skip, limit=limit, producto_id=producto_id, tipo=tipo)

# IMPORTANTE: ruta fija /range ANTES de la ruta con parámetro {movimiento_id}
@router.get("/movimientos/range", response_model=list[Movimiento])
def movimientos_por_rango_ids_endpoint(
    desde: int = Query(..., ge=1, description="ID inicial (inclusive)"),
    hasta: int = Query(..., ge=1, description="ID final (inclusive)"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    MAX_RANGE = 1000
    if desde > hasta:
        raise HTTPException(status_code=400, detail="El parámetro 'desde' debe ser menor o igual a 'hasta'")
    if hasta - desde + 1 > MAX_RANGE:
        raise HTTPException(status_code=400, detail=f"El rango no puede superar los {MAX_RANGE} registros")
    movs = obtener_movimientos_por_rango_ids(db, desde, hasta)
    return [Movimiento.model_validate(m) for m in movs]

@router.get("/movimientos/{movimiento_id}", response_model=Movimiento)
def obtener_movimiento_endpoint(
    movimiento_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    try:
        return obtener_movimiento_por_id(db, movimiento_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))