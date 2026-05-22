from sqlalchemy.orm import Session
from app.models.producto import ProductoDB
from app.schemas.producto import ProductoCreate, ProductoUpdate

def get_all_productos(db: Session):
    return db.query(ProductoDB).all()

def get_producto_by_id(db: Session, producto_id: int):
    return db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

def create_producto(db: Session, producto: ProductoCreate):
    existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto.nombre).first()
    if existente:
        raise ValueError("Ya existe un producto con ese nombre")
    db_producto = ProductoDB(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def update_producto(db: Session, producto_id: int, producto_update: ProductoUpdate):
    db_producto = get_producto_by_id(db, producto_id)
    if not db_producto:
        return None
    for key, value in producto_update.dict(exclude_unset=True).items():
        setattr(db_producto, key, value)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def delete_producto(db: Session, producto_id: int):
    db_producto = get_producto_by_id(db, producto_id)
    if db_producto:
        db.delete(db_producto)
        db.commit()
        return True
    return False

def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_entrada: bool = True):
    """Cantidad positiva, es_entrada=True para aumentar stock, False para salida."""
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