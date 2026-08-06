"""
Modelo de Producto.
"""
<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, Float, Index
=======
from sqlalchemy import Column, Integer, String, Float, Boolean, Index
>>>>>>> feature/interfaz-y-reconstruccion
from app.core.database import Base

class ProductoDB(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)
    stock_maximo = Column(Integer, default=100)
<<<<<<< HEAD
=======
    # Antes "eliminar" un producto lo borraba físicamente y, por el
    # ondelete="CASCADE" en MovimientoDB.producto_id, se llevaba puesto todo
    # su historial de movimientos: justo la auditoría que el sistema dice
    # ofrecer. Ahora "eliminar" desactiva el producto (soft delete) y
    # conserva sus movimientos para reportes e historial.
    activo = Column(Boolean, default=True, nullable=False, index=True)
    # Campo libre y opcional: agrupar/filtrar productos (ej. "Bebidas",
    # "Limpieza") sin tener que crear una tabla de categorías aparte, ya
    # que el volumen de productos de este proyecto no lo justifica.
    categoria = Column(String, nullable=True, index=True)
    # SKU/código de barras: opcional, libre. Pensado para si en algún
    # momento se agrega escaneo por cámara en el cliente móvil.
    sku = Column(String, nullable=True, index=True)
    # Proveedor simple (nombre + contacto) sin tabla aparte: alcanza para
    # saber a quién reponerle sin la complejidad de un módulo de proveedores.
    proveedor_nombre = Column(String, nullable=True)
    proveedor_contacto = Column(String, nullable=True)
>>>>>>> feature/interfaz-y-reconstruccion

    __table_args__ = (Index('idx_producto_stock', 'stock'),)