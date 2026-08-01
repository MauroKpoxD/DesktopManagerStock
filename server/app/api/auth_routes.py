"""
Endpoints de autenticación con refresh tokens.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_password_hash, get_current_active_user
from app.schemas.usuario import UsuarioCreate, Usuario, Token, PerfilUpdate, CambioPassword
from app.models.usuario import UsuarioDB
from app.core.config import settings
from app.core.roles import Rol
from app.core.logging_config import get_logger
from app.core.rate_limiter import limiter
from app.services.refresh_token_service import crear_refresh_token, revocar_refresh_token, rotar_refresh_token
from app.services.usuario_service import actualizar_perfil_propio, cambiar_password_propio
from app.core.exceptions import ConflictError
from app.schemas.auth import RefreshTokenRequest

router = APIRouter(prefix="/api/v1/auth", tags=["autenticación"])
logger = get_logger(__name__)

# Nota: las excepciones de dominio (ConflictError, AuthenticationError, etc.)
# ya no se capturan manualmente aquí; hay manejadores globales registrados en
# main.py que las traducen al HTTPException correspondiente.

@router.post("/register", response_model=Usuario, status_code=status.HTTP_200_OK)
@limiter.limit(settings.register_rate_limit)
def register(request: Request, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first():
        raise ConflictError("Nombre de usuario ya registrado")
    if db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first():
        raise ConflictError("Email ya registrado")

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
    logger.info(f"Nuevo usuario registrado: {usuario.username}")
    return db_usuario

@router.post("/login", response_model=Token)
@limiter.limit(settings.login_rate_limit)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        logger.warning(f"Intento de login fallido para usuario: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": usuario.username}, expires_delta=access_token_expires)
    refresh_token_obj = crear_refresh_token(db, usuario.id)
    logger.info(f"Login exitoso: {usuario.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token_obj.token
    }

@router.post("/refresh", response_model=Token)
def refresh_token_endpoint(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    usuario, nuevo_token_obj = rotar_refresh_token(db, request_data.refresh_token)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": usuario.username}, expires_delta=access_token_expires)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": nuevo_token_obj.token
    }

@router.post("/logout")
def logout(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    # Antes había un `except Exception` genérico aquí, pero revocar_refresh_token
    # nunca lanza (si el token no existe, simplemente no hace nada), así que ese
    # bloque solo lograba camuflar un error real de la base de datos como un 400.
    revocar_refresh_token(db, request_data.refresh_token)
    return {"mensaje": "Sesión cerrada exitosamente"}

@router.get("/me", response_model=Usuario)
def obtener_mi_perfil(current_user: UsuarioDB = Depends(get_current_active_user)):
    """Devuelve el perfil del usuario autenticado. Antes no había forma de que
    un cliente supiera quién es el usuario actual salvo decodificando el JWT
    por su cuenta."""
    return current_user

@router.put("/me", response_model=Usuario)
def actualizar_mi_perfil(
    datos: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user),
):
    """Permite al usuario actualizar su propio email. No puede cambiar su rol
    por esta vía (eso solo lo puede hacer un admin, ver /usuarios/{id})."""
    return actualizar_perfil_propio(db, current_user, datos)

@router.post("/me/password")
def cambiar_mi_password(
    datos: CambioPassword,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(get_current_active_user),
):
    """Cambia la contraseña del usuario autenticado y revoca sus sesiones
    activas (refresh tokens), obligando a volver a iniciar sesión en otros
    dispositivos."""
    cambiar_password_propio(db, current_user, datos)
    return {"mensaje": "Contraseña actualizada correctamente. Vuelve a iniciar sesión en tus otros dispositivos."}