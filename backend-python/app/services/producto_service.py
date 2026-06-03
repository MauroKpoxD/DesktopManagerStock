"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Contiene las operaciones CRUD y lógica de negocio para productos.
           MEJORAS: respeta stock_maximo, evita duplicados en update,
           validaciones de rangos y valores positivos.
"""

from sqlalchemy.orm import Session
from app.models.producto import ProductoDB
from app.schemas.producto import ProductoCreate, ProductoUpdate


# ------------------------------------------------------------
def get_all_productos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProductoDB).offset(skip).limit(limit).all()

# ------------------------------------------------------------
def get_producto_by_id(db: Session, producto_id: int):
    return db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()


# ------------------------------------------------------------
def create_producto(db: Session, producto: ProductoCreate):
    # Validaciones de negocio
    if producto.precio <= 0:
        raise ValueError("El precio debe ser mayor a cero")
    if producto.stock < 0:
        raise ValueError("El stock no puede ser negativo")
    if producto.stock_minimo < 0:
        raise ValueError("El stock mínimo no puede ser negativo")
    if producto.stock_maximo < producto.stock_minimo:
        raise ValueError("El stock máximo debe ser mayor o igual al mínimo")
    # Unicidad
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
    
    # Si cambia el nombre, verificar unicidad
    if producto_update.nombre and producto_update.nombre != db_producto.nombre:
        existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto_update.nombre).first()
        if existente:
            raise ValueError("Ya existe un producto con ese nombre")
    
    # Validar rangos si se actualizan ambos límites
    if producto_update.stock_maximo is not None and producto_update.stock_minimo is not None:
        if producto_update.stock_maximo < producto_update.stock_minimo:
            raise ValueError("El stock máximo no puede ser menor al mínimo")
    
    for key, value in producto_update.model_dump(exclude_unset=True).items():
        setattr(db_producto, key, value)
    
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
def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_entrada: bool = True):
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
    else:
        if producto.stock - cantidad < 0:
            raise ValueError("Stock insuficiente")
        producto.stock -= cantidad
    
    db.commit()
    db.refresh(producto)
    return producto


# ------------------------------------------------------------
def get_productos_stock_bajo(db: Session, umbral: int = None):
    if umbral is not None:
        return db.query(ProductoDB).filter(ProductoDB.stock <= umbral).all()
    else:
        return db.query(ProductoDB).filter(ProductoDB.stock <= ProductoDB.stock_minimo).all()
    