"""
ÚLTIMA MODIFICACIÓN: 12/6/2025 por S4NDULOS
PROPÓSITO: Contiene las operaciones CRUD y lógica de negocio para productos
           MEJORAS: respeta stock_maximo, evita duplicados en update,
           validaciones de rangos y valores positivos
           NUEVO: Registro automático de movimientos al ajustar stock
           FIX: Validación de stock máximo en update con restauración segura
"""

from sqlalchemy.orm import Session
from app.models.producto import ProductoDB
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.models.movimiento import MovimientoDB
from app.schemas.movimiento import MovimientoBase
from app.core.logging_config import setup_logging
logger = setup_logging()

# ------------------------------------------------------------
def get_all_productos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProductoDB).order_by(ProductoDB.id).offset(skip).limit(limit).all()


# ------------------------------------------------------------
def get_producto_by_id(db: Session, producto_id: int):
    return db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()


# ------------------------------------------------------------
def create_producto(db: Session, producto: ProductoCreate):
    if producto.precio <= 0:
        raise ValueError("El precio debe ser mayor a cero")
    if producto.stock < 0:
        raise ValueError("El stock no puede ser negativo")
    if producto.stock_minimo < 0:
        raise ValueError("El stock mínimo no puede ser negativo")
    if producto.stock_maximo < producto.stock_minimo:
        raise ValueError("El stock máximo debe ser mayor o igual al mínimo")
    if producto.stock > producto.stock_maximo:
        raise ValueError(f"El stock inicial no puede superar el máximo de {producto.stock_maximo}")
    
    existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto.nombre).first()
    if existente:
        raise ValueError("Ya existe un producto con ese nombre")
    
    db_producto = ProductoDB(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


# ------------------------------------------------------------
def update_producto(db: Session, producto_id: int, producto_update: ProductoUpdate):
    db_producto = get_producto_by_id(db, producto_id)
    if not db_producto:
        return None
    
    # Validar nombre duplicado
    if producto_update.nombre and producto_update.nombre != db_producto.nombre:
        existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto_update.nombre).first()
        if existente:
            raise ValueError("Ya existe un producto con ese nombre")
    
    # Guardar valores originales para posible restauración
    original_stock = db_producto.stock
    original_min = db_producto.stock_minimo
    original_max = db_producto.stock_maximo
    
    # Aplicar cambios en memoria
    update_data = producto_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_producto, key, value)
    
    # Validaciones después de cambios
    if db_producto.stock_minimo > db_producto.stock_maximo:
        # Revertir mín/máx
        db_producto.stock_minimo = original_min
        db_producto.stock_maximo = original_max
        raise ValueError("El stock mínimo no puede ser mayor que el máximo")
    
    if db_producto.stock > db_producto.stock_maximo:
        # Revertir stock
        db_producto.stock = original_stock
        raise ValueError(f"El stock actual ({db_producto.stock}) no puede superar el máximo ({db_producto.stock_maximo})")
    
    db.commit()
    db.refresh(db_producto)
    return db_producto


# ------------------------------------------------------------
def delete_producto(db: Session, producto_id: int):
    db_producto = get_producto_by_id(db, producto_id)
    if db_producto:
        db.delete(db_producto)
        db.commit()
        return True
    return False


# ------------------------------------------------------------
def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_entrada: bool, usuario_id: int):
    """
    Ajusta el stock de un producto (entrada o salida) y registra el movimiento.
    
    Args:
        db: Sesión de base de datos.
        producto_id: ID del producto.
        cantidad: Cantidad a sumar o restar (positiva).
        es_entrada: True para entrada (aumenta stock), False para salida (disminuye).
        usuario_id: ID del usuario que realiza la operación (para auditoría).
    
    Returns:
        ProductoDB: El producto actualizado.
    
    Raises:
        ValueError: Si cantidad <= 0, producto no existe, stock insuficiente,
                    o se supera el stock máximo.
    """
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva")
    
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        raise ValueError("Producto no encontrado")
    
    if es_entrada:
        nuevo_stock = producto.stock + cantidad
        if nuevo_stock > producto.stock_maximo:
            raise ValueError(f"El stock no puede superar el máximo de {producto.stock_maximo}")
        producto.stock = nuevo_stock
        tipo = "entrada"
    else:
        if producto.stock - cantidad < 0:
            raise ValueError("Stock insuficiente")
        producto.stock -= cantidad
        tipo = "salida"

    movimiento_data = MovimientoBase(
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        stock_resultante=producto.stock,
        usuario_id=usuario_id
    )
    db_movimiento = MovimientoDB(**movimiento_data.model_dump())
    db.add(db_movimiento)
    
    db.commit()
    db.refresh(producto)
    
    logger.info(f"Ajuste de stock: producto_id={producto_id}, usuario_id={usuario_id}, tipo={tipo}, cantidad={cantidad}, stock_resultante={producto.stock}")
    return producto


# ------------------------------------------------------------
def get_productos_stock_bajo(db: Session, umbral: int = None):
    if umbral is not None:
        return db.query(ProductoDB).filter(ProductoDB.stock <= umbral).all()
    else:
        return db.query(ProductoDB).filter(ProductoDB.stock <= ProductoDB.stock_minimo).all()