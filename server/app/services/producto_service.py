"""
Servicio de productos con lógica de negocio.
"""
from sqlalchemy.orm import Session
from app.models.producto import ProductoDB
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.models.movimiento import MovimientoDB
from app.schemas.movimiento import MovimientoBase
from app.core.logging_config import get_logger
from app.core.exceptions import NotFoundError, ValidationError, ConflictError

logger = get_logger(__name__)

def listar_productos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProductoDB).order_by(ProductoDB.id).offset(skip).limit(limit).all()

def obtener_producto_por_id(db: Session, producto_id: int):
    producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
    if not producto:
        raise NotFoundError(f"Producto con ID {producto_id} no encontrado")
    return producto

def crear_producto(db: Session, producto: ProductoCreate):
    existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto.nombre).first()
    if existente:
        raise ConflictError(f"Ya existe un producto con el nombre '{producto.nombre}'")
    db_producto = ProductoDB(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    logger.info(f"Producto creado: {db_producto.nombre} (ID {db_producto.id})")
    return db_producto

def actualizar_producto(db: Session, producto_id: int, producto_update: ProductoUpdate):
    db_producto = obtener_producto_por_id(db, producto_id)
    if producto_update.nombre and producto_update.nombre != db_producto.nombre:
        existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto_update.nombre).first()
        if existente:
            raise ConflictError(f"Ya existe un producto con el nombre '{producto_update.nombre}'")
    update_data = producto_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_producto, key, value)
    # Las validaciones de rangos ya se hicieron en el schema, pero repetimos por seguridad
    if db_producto.stock_minimo > db_producto.stock_maximo:
        raise ValidationError("El stock mínimo no puede ser mayor que el máximo")
    if db_producto.stock > db_producto.stock_maximo:
        raise ValidationError(f"El stock actual ({db_producto.stock}) no puede superar el máximo ({db_producto.stock_maximo})")
    db.commit()
    db.refresh(db_producto)
    logger.info(f"Producto actualizado: {db_producto.nombre} (ID {db_producto.id})")
    return db_producto

def eliminar_producto(db: Session, producto_id: int):
    db_producto = obtener_producto_por_id(db, producto_id)
    db.delete(db_producto)
    db.commit()
    logger.info(f"Producto eliminado: ID {producto_id}")
    return True

def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_entrada: bool, usuario_id: int):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser positiva")
    producto = obtener_producto_por_id(db, producto_id)
    if es_entrada:
        nuevo_stock = producto.stock + cantidad
        if nuevo_stock > producto.stock_maximo:
            raise ValidationError(f"El stock no puede superar el máximo de {producto.stock_maximo}")
        producto.stock = nuevo_stock
        tipo = "entrada"
    else:
        if producto.stock - cantidad < 0:
            raise ValidationError("Stock insuficiente")
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
    logger.info(f"Ajuste de stock: producto_id={producto_id}, usuario_id={usuario_id}, tipo={tipo}, cantidad={cantidad}, nuevo_stock={producto.stock}")
    return producto

def obtener_productos_con_stock_bajo(db: Session, umbral: int = None):
    if umbral is not None:
        return db.query(ProductoDB).filter(ProductoDB.stock <= umbral).all()
    else:
        return db.query(ProductoDB).filter(ProductoDB.stock <= ProductoDB.stock_minimo).all()