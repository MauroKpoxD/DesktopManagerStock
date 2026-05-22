from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class ProductoDB(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)      # para alertas
    stock_maximo = Column(Integer, default=100)
    # se puede agregar mas cosas como el codigo de barras para mas adelante