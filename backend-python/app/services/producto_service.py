# añadir db
_productos = [
    {"id": 1, "nombre": "test", "precio": 10.5, "stock": 5}
]

def get_all_productos():
    """Devuelve todos los productos"""
    return _productos

def add_producto(producto_data: dict):
    """Agrega un nuevo producto (para pruebas)"""
    nuevo_id = len(_productos) + 1
    producto_data["id"] = nuevo_id
    _productos.append(producto_data)
    return producto_data