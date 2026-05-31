"""
ÚLTIMA MODIFICACIÓN: 30/5/2025 por S4NDULOS
PROPÓSITO: Contiene las operaciones CRUD y lógica de negocio para productos.
           Aísla el acceso a la base de datos de los controladores.
"""

from sqlalchemy.orm import Session
from app.models.producto import ProductoDB
from app.schemas.producto import ProductoCreate, ProductoUpdate


# ------------------------------------------------------------
def get_all_productos(db: Session):
    """Devuelve todos los productos (lista vacía si no hay)."""
    return db.query(ProductoDB).all()


# ------------------------------------------------------------
def get_producto_by_id(db: Session, producto_id: int):
    """Busca un producto por su ID. Retorna el producto o None."""
    return db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()


# ------------------------------------------------------------
def create_producto(db: Session, producto: ProductoCreate):
    """
    Crea un nuevo producto
    - Lanza error si ya existe otro con el mismo nombre
    - Guarda en BD y retorna el producto creado (con su ID asignado)
    """
    # Verificar duplicado por nombre
    existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto.nombre).first()
    if existente:
        raise ValueError("Ya existe un producto con ese nombre")

    # Crear instancia del modelo y guardar
    db_producto = ProductoDB(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)   # actualiza con el ID generado
    return db_producto


# ------------------------------------------------------------
def update_producto(db: Session, producto_id: int, producto_update: ProductoUpdate):
    """
    Actualiza un producto existente (solo los campos enviados)
    Retorna el producto actualizado o None si no existe
    """
    db_producto = get_producto_by_id(db, producto_id)
    if not db_producto:
        return None

    # Aplicar solo los campos que vienen en producto_update (exclude_unset=True)
    for key, value in producto_update.dict(exclude_unset=True).items():
        setattr(db_producto, key, value)

    db.commit()
    db.refresh(db_producto)
    return db_producto


# ------------------------------------------------------------
def delete_producto(db: Session, producto_id: int):
    """
    Elimina un producto por ID.
    Retorna True si se elimino, False si no existia
    """
    db_producto = get_producto_by_id(db, producto_id)
    if db_producto:
        db.delete(db_producto)
        db.commit()
        return True
    return False


# ------------------------------------------------------------
def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_entrada: bool = True):
    """
    Ajusta el stock de un producto
    - es_entrada=True  -> aumenta stock (ej: compra, devolución)
    - es_entrada=False -> disminuye stock (ej: venta)
    Si el stock se vuelve negativo, lanza un error
    Retorna el producto actualizado o None si no existe
    """
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        return None

    if es_entrada:
        producto.stock += cantidad
    else:
        if producto.stock - cantidad < 0:
            raise ValueError("Stock insuficiente")
        producto.stock -= cantidad

    db.commit()
    db.refresh(producto)
    return producto


# ------------------------------------------------------------
def get_productos_stock_bajo(db: Session, umbral: int = None):
    """
    Retorna productos con stock bajo.
    - Si se pasa 'umbral' (ej: umbral=5), devuelve productos con stock <= umbral
    - Si no se pasa umbral, compara con el 'stock_minimo' de cada producto
    """
    if umbral is not None:
        return db.query(ProductoDB).filter(ProductoDB.stock <= umbral).all()
    else:
        return db.query(ProductoDB).filter(ProductoDB.stock <= ProductoDB.stock_minimo).all()