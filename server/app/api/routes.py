"""
Rutas principales: productos y movimientos.
"""
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.producto import Producto, ProductoCreate, ProductoUpdate
=======
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.producto import Producto, ProductoCreate, ProductoUpdate, ImportacionResultado
>>>>>>> feature/interfaz-y-reconstruccion
from app.schemas.movimiento import Movimiento
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.core.roles import require_roles, Rol
from app.models.usuario import UsuarioDB
from app.services.producto_service import (
    listar_productos,
<<<<<<< HEAD
=======
    contar_productos,
>>>>>>> feature/interfaz-y-reconstruccion
    obtener_producto_por_id,
    crear_producto,
    actualizar_producto,
    eliminar_producto,
<<<<<<< HEAD
    ajustar_stock,
    obtener_productos_con_stock_bajo
=======
    reactivar_producto,
    ajustar_stock,
    obtener_productos_con_stock_bajo,
    listar_categorias,
    importar_productos_csv
>>>>>>> feature/interfaz-y-reconstruccion
)
from app.services.movimiento_service import (
    obtener_movimiento_por_id,
    listar_movimientos,
<<<<<<< HEAD
    obtener_movimientos_por_rango_ids
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError

router = APIRouter(prefix="/api/v1", tags=["productos"])

=======
    contar_movimientos,
    obtener_movimientos_por_rango_ids
)

router = APIRouter(prefix="/api/v1", tags=["productos"])

# Nota: las excepciones de dominio (NotFoundError, ValidationError,
# ConflictError, ...) ya no se capturan manualmente en cada endpoint; hay
# manejadores globales registrados en main.py que las traducen al
# HTTPException correspondiente con el mismo código de estado que antes.

>>>>>>> feature/interfaz-y-reconstruccion
@router.get("/")
def home():
    return {
        "mensaje": "DesktopManagerStock API",
        "version": settings.api_version,
        "docs": "/docs"
    }

@router.get("/productos", response_model=list[Producto])
def get_productos(
<<<<<<< HEAD
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    return listar_productos(db, skip=skip, limit=limit)
=======
    response: Response,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    incluir_inactivos: bool = Query(False, description="Incluir productos desactivados (soft-deleted)"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría exacta"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    response.headers["X-Total-Count"] = str(contar_productos(db, incluir_inactivos=incluir_inactivos, categoria=categoria))
    return listar_productos(db, skip=skip, limit=limit, incluir_inactivos=incluir_inactivos, categoria=categoria)

@router.get("/productos/categorias", response_model=list[str])
def get_categorias(
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
    """Categorías distintas ya usadas por productos activos, para poblar un filtro en el cliente."""
    return listar_categorias(db)

@router.post("/productos/importar-csv", response_model=ImportacionResultado)
async def importar_productos_csv_endpoint(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
    """
    Importación masiva de productos desde un CSV. Columnas reconocidas
    (solo "nombre" es obligatoria): nombre, categoria, sku, precio, stock,
    stock_minimo, stock_maximo, proveedor_nombre, proveedor_contacto.
    Filas con errores se omiten individualmente (ver respuesta) sin abortar
    el resto de la importación.
    """
    if not archivo.filename or not archivo.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un .csv")
    contenido_bytes = await archivo.read()
    try:
        contenido_texto = contenido_bytes.decode("utf-8-sig")  # utf-8-sig: tolera el BOM que agrega Excel/el cliente
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="El archivo no está en UTF-8. Volvé a guardarlo con esa codificación.")
    resultado = importar_productos_csv(db, contenido_texto)
    return resultado
>>>>>>> feature/interfaz-y-reconstruccion

@router.get("/productos/{producto_id}", response_model=Producto)
def get_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
<<<<<<< HEAD
    try:
        return obtener_producto_por_id(db, producto_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
=======
    return obtener_producto_por_id(db, producto_id)
>>>>>>> feature/interfaz-y-reconstruccion

@router.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
def create_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
<<<<<<< HEAD
    try:
        return crear_producto(db, producto)
    except (ValidationError, ConflictError) as e:
        raise HTTPException(status_code=400, detail=str(e))
=======
    return crear_producto(db, producto)
>>>>>>> feature/interfaz-y-reconstruccion

@router.put("/productos/{producto_id}", response_model=Producto)
def update_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
<<<<<<< HEAD
    try:
        return actualizar_producto(db, producto_id, producto_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ValidationError, ConflictError) as e:
        raise HTTPException(status_code=400, detail=str(e))
=======
    return actualizar_producto(db, producto_id, producto_update, es_admin=(current_user.rol == Rol.ADMIN.value))
>>>>>>> feature/interfaz-y-reconstruccion

@router.delete("/productos/{producto_id}", status_code=204)
def delete_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN]))
):
<<<<<<< HEAD
    try:
        eliminar_producto(db, producto_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
=======
    # Soft delete: desactiva el producto pero conserva su historial de
    # movimientos para auditoría (ver producto_service.eliminar_producto).
    eliminar_producto(db, producto_id)

@router.patch("/productos/{producto_id}/reactivar", response_model=Producto)
def reactivar_producto_endpoint(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN]))
):
    return reactivar_producto(db, producto_id)
>>>>>>> feature/interfaz-y-reconstruccion

@router.patch("/productos/{producto_id}/stock")
def ajustar_stock_endpoint(
    producto_id: int,
    cantidad: int = Query(..., gt=0, description="Cantidad positiva a mover"),
    tipo: str = Query("entrada", pattern="^(entrada|salida)$", description="Tipo: 'entrada' o 'salida'"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN, Rol.EDITOR]))
):
<<<<<<< HEAD
    try:
        producto = ajustar_stock(db, producto_id, cantidad, tipo == "entrada", current_user.id)
        return {"mensaje": f"Stock actualizado. Nuevo stock: {producto.stock}"}
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
=======
    producto = ajustar_stock(db, producto_id, cantidad, tipo == "entrada", current_user.id)
    return {"mensaje": f"Stock actualizado. Nuevo stock: {producto.stock}"}
>>>>>>> feature/interfaz-y-reconstruccion

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
<<<<<<< HEAD
=======
    response: Response,
>>>>>>> feature/interfaz-y-reconstruccion
    skip: int = Query(0, ge=0, description="Número de movimientos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de movimientos a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    tipo: Optional[str] = Query(None, pattern="^(entrada|salida)$", description="Filtrar por tipo"),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user)
):
<<<<<<< HEAD
=======
    response.headers["X-Total-Count"] = str(contar_movimientos(db, producto_id=producto_id, tipo=tipo))
>>>>>>> feature/interfaz-y-reconstruccion
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
<<<<<<< HEAD
    try:
        return obtener_movimiento_por_id(db, movimiento_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
=======
    return obtener_movimiento_por_id(db, movimiento_id)
>>>>>>> feature/interfaz-y-reconstruccion
