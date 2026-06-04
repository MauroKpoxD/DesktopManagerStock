"""
ÚLTIMA MODIFICACIÓN: 3/6/2025 por S4NDULOS
PROPÓSITO: Endpoints de autenticación: registro de usuarios y login con JWT
           Maneja creación de usuarios y generación de tokens de acceso
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_password_hash
from app.schemas.usuario import UsuarioCreate, Usuario, Token
from app.models.usuario import UsuarioDB
from app.core.config import settings
from app.core.roles import Rol

router = APIRouter(prefix="/api/v1/auth", tags=["autenticación"])

# ------------------------------------------------------------------------------
# ENDPOINT: REGISTRO DE NUEVO USUARIO
# ------------------------------------------------------------------------------
@router.post("/register", response_model=Usuario, status_code=status.HTTP_200_OK)
def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    Por defecto, se asigna el rol 'lector' (sin privilegios de escritura).

    Parámetros body (JSON):
    - username: str (obligatorio, único)
    - email: EmailStr (obligatorio, único)
    - password: str (obligatorio, mínimo 4 caracteres, se hashea automáticamente)
    - rol: str (opcional, se ignora, siempre se asigna 'lector' por seguridad)

    Respuesta: objeto Usuario (sin incluir la contraseña).

    Códigos de error:
    - 400: Nombre de usuario o email ya registrados.
    - 422: Datos inválidos (email mal formado, password demasiado corto, etc.)
    """
    # Verificar si ya existe username o email
    if db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first():
        raise HTTPException(status_code=400, detail="Nombre de usuario ya registrado")
    if db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed = get_password_hash(usuario.password)
    db_usuario = UsuarioDB(
        username=usuario.username,
        email=usuario.email,
        hashed_password=hashed,
        rol=Rol.LECTOR.value,
        activo=True
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# ------------------------------------------------------------------------------
# ENDPOINT: LOGIN (OBTENCIÓN DE TOKEN JWT)
# ------------------------------------------------------------------------------
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica a un usuario y devuelve un token JWT de acceso.
    El token debe incluirse en el header `Authorization: Bearer <token>` para acceder a endpoints protegidos.

    Parámetros (form-data):
    - username: str (nombre de usuario registrado)
    - password: str (contraseña en texto plano)

    Respuesta:
    - access_token: str (token JWT válido por `ACCESS_TOKEN_EXPIRE_MINUTES` minutos)
    - token_type: str (siempre 'bearer')

    Códigos de error:
    - 401: Credenciales inválidas (usuario no existe o contraseña incorrecta)
    """
    usuario = authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}