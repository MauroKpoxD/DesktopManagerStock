"""
ÚLTIMA MODIFICACIÓN: 9/6/2025 por S4NDULOS
PROPÓSITO: Define los endpoints públicos y protegidos de la API
           Agrupa rutas de productos con autenticación JWT y control de roles
           MEJORAS: paginación, validación de cantidad>0, uso de require_roles
           NUEVO: Endpoints para consultar movimientos de stock (historial)
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
    get_all_productos,
    get_producto_by_id,
    create_producto as service_create_producto,
    update_producto as service_update_producto,
    delete_producto as service_delete_producto,
    ajustar_stock as service_ajustar_stock,
    get_productos_stock_bajo
)
from app.services.movimiento_service import (
    get_movimiento_by_id,
    get_movimientos,
    get_movimientos_por_rango_ids
)

router = APIRouter(prefix="/api/v1", tags=["productos"])

# ------------------------------------------------------------------------------
# ENDPOINT: HOME (raíz) - PÚBLICO
# ------------------------------------------------------------------------------
@router.get("/")
def home():
    return {
        "mensaje": "DesktopManagerStock API",
        "version": settings.api_version,
        "docs": "/docs"
    }

# ------------------------------------------------------------------------------
# ENDPOINT: LISTAR todos los productos (requiere autenticación)
# ------------------------------------------------------------------------------
@router.get("/productos", response_model=list[Producto])
def get_productos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    return get_all_productos(db, skip=skip, limit=limit)

# ------------------------------------------------------------------------------
# ENDPOINT: OBTENER un producto por ID (requiere autenticación)
# ------------------------------------------------------------------------------
@router.get("/productos/{producto_id}", response_model=Producto)
def get_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Busca un producto por ID.
    Requiere autenticación.
    """
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return producto

# ------------------------------------------------------------------------------
# ENDPOINT: CREAR un nuevo producto (solo admin o editor)
# ------------------------------------------------------------------------------
@router.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
def create_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    try:
        return service_create_producto(db, producto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------------------
# ENDPOINT: ACTUALIZAR un producto (solo admin o editor)
# ------------------------------------------------------------------------------
@router.put("/productos/{producto_id}", response_model=Producto)
def update_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    """
    Actualiza un producto (parcial o total).
    Requiere rol: admin o editor.
    """
    producto = service_update_producto(db, producto_id, producto_update)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# ------------------------------------------------------------------------------
# ENDPOINT: ELIMINAR un producto (solo admin)
# ------------------------------------------------------------------------------
@router.delete("/productos/{producto_id}", status_code=204)
def delete_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN]))
):
    """
    Elimina un producto.
    Requiere rol: admin.
    """
    if not service_delete_producto(db, producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")

# ------------------------------------------------------------------------------
# ENDPOINT: AJUSTAR STOCK (entrada/salida) - solo admin o editor
# ------------------------------------------------------------------------------
@router.patch("/productos/{producto_id}/stock")
def ajustar_stock(
    producto_id: int,
    cantidad: int = Query(..., gt=0, description="Cantidad positiva a mover"),
    tipo: str = Query("entrada", pattern="^(entrada|salida)$", description="Tipo: 'entrada' o 'salida'"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    """
    Ajusta el stock de un producto (entrada o salida).
    Registra automáticamente un movimiento en el historial.
    Requiere rol admin o editor.
    """
    es_entrada = tipo.lower() == "entrada"
    try:
        producto = service_ajustar_stock(db, producto_id, cantidad, es_entrada, current_user.id)
        return {"mensaje": f"Stock actualizado. Nuevo stock: {producto.stock}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------------------
# ENDPOINT: PRODUCTOS CON STOCK BAJO (requiere autenticación)
# ------------------------------------------------------------------------------
@router.get("/productos/stock/bajo", response_model=list[Producto])
def productos_stock_bajo(  # Nombre diferente para evitar recursión
    umbral: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Retorna productos con stock bajo.
    - Si se envía ?umbral=5 -> stock <= 5.
    - Si no -> stock <= stock_minimo de cada producto.
    Requiere autenticación.
    """
    productos_db = get_productos_stock_bajo(db, umbral)  # Llama al servicio
    return [Producto.model_validate(p) for p in productos_db]

# ------------------------------------------------------------------------------
# ENDPOINT: MOVIMIENTOS POR RANGO DE IDS
# ------------------------------------------------------------------------------
@router.get("/movimientos/range", response_model=list[Movimiento])
def movimientos_por_rango_ids(
    desde: int = Query(..., ge=1, description="ID inicial (inclusive)"),
    hasta: int = Query(..., ge=1, description="ID final (inclusive)"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Obtiene los movimientos cuyos IDs se encuentren en el rango [desde, hasta].
    Útil para consultar bloques consecutivos de movimientos.

    Parámetros:
    - desde: ID inicial (inclusive, debe ser >= 1)
    - hasta: ID final (inclusive, debe ser >= 1)

    Respuesta:
    - Lista de objetos Movimiento ordenados por ID ascendente.

    Códigos de error:
    - 400: si 'desde' > 'hasta' o el rango supera los 1000 registros
    - 401: No autenticado
    - 422: Parámetros inválidos (no enteros, etc.)
    """
    MAX_RANGE = 1000
    if desde > hasta:
        raise HTTPException(
            status_code=400,
            detail="El parámetro 'desde' debe ser menor o igual a 'hasta'"
        )
    if hasta - desde + 1 > MAX_RANGE:
        raise HTTPException(
            status_code=400,
            detail=f"El rango no puede superar los {MAX_RANGE} registros"
        )
    movs = get_movimientos_por_rango_ids(db, desde, hasta)
    return [Movimiento.model_validate(m) for m in movs]

# ------------------------------------------------------------------------------
# ENDPOINT: LISTAR MOVIMIENTOS (PAGINADO Y FILTRADO)
# ------------------------------------------------------------------------------
@router.get("/movimientos", response_model=list[Movimiento])
def listar_movimientos(
    skip: int = Query(0, ge=0, description="Número de movimientos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de movimientos a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    tipo: Optional[str] = Query(None, pattern="^(entrada|salida)$", description="Filtrar por tipo ('entrada' o 'salida')"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Lista los movimientos de stock con paginación y filtros opcionales.
    Los movimientos se devuelven ordenados por fecha descendente (más reciente primero).

    Parámetros query:
    - skip: cantidad de registros a omitir (para paginación)
    - limit: cantidad máxima de registros a devolver (entre 1 y 1000)
    - producto_id: opcional, devuelve solo movimientos de ese producto
    - tipo: opcional, 'entrada' o 'salida'

    Respuesta: lista de objetos Movimiento.
    Requiere autenticación.
    """
    return get_movimientos(db, skip=skip, limit=limit, producto_id=producto_id, tipo=tipo)

# ------------------------------------------------------------------------------
# ENDPOINT: OBTENER UN MOVIMIENTO POR ID
# ------------------------------------------------------------------------------
@router.get("/movimientos/{movimiento_id}", response_model=Movimiento)
def obtener_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Busca un movimiento de stock por su ID único.

    Parámetros path:
    - movimiento_id: ID del movimiento a consultar

    Respuesta: objeto Movimiento.

    Códigos de error:
    - 404: si no existe un movimiento con ese ID
    - 401: No autenticado
    """
    movimiento = get_movimiento_by_id(db, movimiento_id)
    if not movimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento no encontrado"
        )
    return Movimiento.model_validate(movimiento)