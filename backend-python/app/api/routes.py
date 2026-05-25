# Este archivo define TODAS los endpoints que va a entender la API.

# Importamos las herramientas necesarias
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services import producto_service          
from app.schemas.producto import Producto, ProductoCreate, ProductoUpdate 
from app.core.database import get_db               
from app.core.config import settings             

# establezco route con /api/v1
router = APIRouter(prefix="/api/v1", tags=["productos"]) 

# ------------------------------------------------------------------------------
# ENDPOINT: HOME (raíz)
# ------------------------------------------------------------------------------
@router.get("/")# /api/v1/ 
def home():
    return {
        "mensaje": "DesktopManagerStock API",
        "version": settings.api_version,           # version del .env
        "docs": "/docs"                            # lo mandamos a /docs
    }

# ------------------------------------------------------------------------------
# ENDPOINT: LISTAR todos los productos
# ------------------------------------------------------------------------------
@router.get("/productos", response_model=list[Producto])
# "response_model=list[Producto]" significa: lo que devuelva esta función debe ser una lista de objetos Producto
def get_productos(db: Session = Depends(get_db)):
    """
    Obtiene todos los productos guardados en la base de datos.
    No necesita parámetros.
    Devuelve una lista (puede estar vacía si no hay productos).
    """
    # llamamos a la función del servicio que trae todos los productos.
    # le pasamos la sesión de base de datos (db) para que pueda hacer consultas.
    return producto_service.get_all_productos(db)

# ------------------------------------------------------------------------------
# ENDPOINT: OBTENER un producto por su ID
# ------------------------------------------------------------------------------
@router.get("/productos/{producto_id}", response_model=Producto)
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Busca un producto específico usando su número de ID.
    Ejemplo: GET /api/v1/productos/5  -> devuelve el producto con id=5.
    Si no existe, devuelve un error 404 (No encontrado).
    """
    # le pedimos al servicio que busque el producto por id
    producto = producto_service.get_producto_by_id(db, producto_id)
    
    # si no encontro nada el producto es None, lanzamos un error HTTP 404
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,   # codigo 404 = "No encontrado"
            detail="Producto no encontrado"          # mensaje que vera el usuario
        )
    
    # si lo encontro lo retorna
    return producto

# ------------------------------------------------------------------------------
# ENDPOINT: ACTUALIZAR un producto existente (total o parcial)
# ------------------------------------------------------------------------------
@router.put("/productos/{producto_id}", response_model=Producto)
def update_producto(producto_id: int, producto_update: ProductoUpdate, db: Session = Depends(get_db)):
    """
    actualiza los datos de un producto poder enviar solo los campos que quieras cambiar.
    Ejemplo de petición: PUT /api/v1/productos/3
    Cuerpo:
    {
        "precio": 29.99,
        "stock": 15
    }
    esto cambiaria solo el precio y el stock del producto con id=3
    si el producto no existe, devuelve 404
    devuelve el producto actualizado
    """
    producto = producto_service.update_producto(db, producto_id, producto_update)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# ------------------------------------------------------------------------------
# ENDPOINT: ELIMINAR un producto
# ------------------------------------------------------------------------------
@router.delete("/productos/{producto_id}", status_code=204) # status_code=204 significa "Sin contenido" – la operación fue exitosa pero no devolvemos nada
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    elimina un producto de la base de datos.
    ejemplo: DELETE /api/v1/productos/7
    si se elimina correctamente, devuelve respuesta vacia con codigo 204.
    si el producto no existe, devuelve 404.
    """
    if not producto_service.delete_producto(db, producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # No hay return porque con 204 FastAPI no envía cuerpo

# ------------------------------------------------------------------------------
# ENDPOINT: AJUSTAR STOCK (entrada o salida de mercadería)
# ------------------------------------------------------------------------------
@router.patch("/productos/{producto_id}/stock")
def ajustar_stock(
    producto_id: int,
    cantidad: int,           # cantidad a sumar o restar
    tipo: str = "entrada",   # por defecto es "entrada". Puede ser "entrada" o "salida"
    db: Session = Depends(get_db)
):
    """
    Permite aumentar (entrada) o disminuir (salida) el stock de un producto.
    Ejemplo para entrada: PATCH /api/v1/productos/2/stock?cantidad=5&tipo=entrada
    Ejemplo para salida:  PATCH /api/v1/productos/2/stock?cantidad=3&tipo=salida
    Si tipo=salida y no hay suficiente stock, devuelve un error 400.
    Devuelve un mensaje con el nuevo stock.
    """
    # Convertimos el texto "entrada" o "salida" a booleano
    es_entrada = tipo.lower() == "entrada"
    
    try:
        # Llamamos al servicio que ajusta el stock. Puede lanzar una excepción si no hay stock suficiente.
        producto = producto_service.ajustar_stock(db, producto_id, cantidad, es_entrada)
        return {"mensaje": f"Stock actualizado. Nuevo stock: {producto.stock}"}
    except ValueError as e:
        # Si el servicio lanza un error (por stock negativo), lo capturamos y devolvemos un error 400
        raise HTTPException(status_code=400, detail=str(e))