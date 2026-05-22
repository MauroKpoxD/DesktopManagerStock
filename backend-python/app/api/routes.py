from fastapi import APIRouter
from app.services.producto_service import get_all_productos

router = APIRouter()

@router.get("/")
def home():
    return {"mensaje": "Hola mundo!"}

@router.get("/productos")
def get_productos():
    productos = get_all_productos()
    return {"productos": productos}