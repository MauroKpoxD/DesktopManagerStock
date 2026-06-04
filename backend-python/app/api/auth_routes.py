"""
ÚLTIMA MODIFICACIÓN: 4/6/2025 por S4NDULOS
PROPÓSITO: Endpoints de autenticación: registro de usuarios y login con JWT
           Maneja creación de usuarios y generación de tokens de acceso
           Añadido rate limiting y logging de eventos de seguridad.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_password_hash
from app.schemas.usuario import UsuarioCreate, Usuario, Token
from app.models.usuario import UsuarioDB
from app.core.config import settings
from app.core.roles import Rol
from app.core.logging_config import setup_logging
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1/auth", tags=["autenticación"])
logger = setup_logging()
limiter = Limiter(key_func=get_remote_address)

# ------------------------------------------------------------------------------
# ENDPOINT: REGISTRO DE NUEVO USUARIO
# ------------------------------------------------------------------------------
@router.post("/register", response_model=Usuario, status_code=status.HTTP_200_OK)
@limiter.limit(settings.register_rate_limit)  # Ej: 2 por minuto
def register(request: Request, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    Por defecto, se asigna el rol 'lector' (sin privilegios de escritura).
    La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial.
    """
    # Verificar si ya existe username o email
    if db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first():
        logger.warning(f"Intento de registro con username ya existente: {usuario.username}")
        raise HTTPException(status_code=400, detail="Nombre de usuario ya registrado")
    if db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first():
        logger.warning(f"Intento de registro con email ya existente: {usuario.email}")
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed = get_password_hash(usuario.password)
    # Forzar rol 'lector' por seguridad (ignorar lo que venga en el request)
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
    logger.info(f"Nuevo usuario registrado: {usuario.username} (email: {usuario.email})")
    return db_usuario

# ------------------------------------------------------------------------------
# ENDPOINT: LOGIN (OBTENCIÓN DE TOKEN JWT)
# ------------------------------------------------------------------------------
@router.post("/login", response_model=Token)
@limiter.limit(settings.login_rate_limit)  # Ej: 5 por minuto
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica a un usuario y devuelve un token JWT de acceso.
    """
    usuario = authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        logger.warning(f"Intento de login fallido para usuario: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )
    logger.info(f"Login exitoso: {usuario.username} (rol: {usuario.rol})")
    return {"access_token": access_token, "token_type": "bearer"}