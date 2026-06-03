"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Define los endpoints públicos y protegidos de la API
           Agrupa rutas de productos con autenticación JWT y control de roles.
           MEJORAS: paginación, validación de cantidad>0, uso de require_roles.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.producto import Producto, ProductoCreate, ProductoUpdate
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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session       
from app.schemas.producto import Producto, ProductoCreate, ProductoUpdate 
from app.core.database import get_db               
from app.core.config import settings       
from app.core.security import get_current_active_user 
from app.models.usuario import UsuarioDB                
from typing import Optional     

from app.services.producto_service import (
    get_all_productos,
    get_producto_by_id,
    create_producto as service_create_producto,
    update_producto as service_update_producto,
    delete_producto as service_delete_producto,
    ajustar_stock as service_ajustar_stock,
    get_productos_stock_bajo
)

# establezco route con /api/v1
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
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Actualiza un producto (parcial o total).
    Requiere rol: admin o editor.
    """
    if current_user.rol not in ["admin", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar productos"
        )
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
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Elimina un producto.
    Requiere rol: admin.
    """
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar productos"
        )
    if not service_delete_producto(db, producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # No hay return (código 204)

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
    es_entrada = tipo.lower() == "entrada"
    try:
        producto = service_ajustar_stock(db, producto_id, cantidad, es_entrada)
        return {"mensaje": f"Stock actualizado. Nuevo stock: {producto.stock}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------------------
# ENDPOINT: PRODUCTOS CON STOCK BAJO (requiere autenticación)
# ------------------------------------------------------------------------------
@router.get("/productos/stock-bajo", response_model=list[Producto])
def get_productos_stock_bajo(
    umbral: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """
    Retorna productos con stock bajo.
    - Si se envía ?umbral=5 → stock <= 5.
    - Si no → stock <= stock_minimo de cada producto.
    Requiere autenticación.
    """
    return get_productos_stock_bajo(db, umbral)