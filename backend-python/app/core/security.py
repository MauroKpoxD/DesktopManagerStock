"""
SEGURIDAD: Hashing de contraseñas y autenticación con JWT
Este archivo contiene las herramientas para:
- Encriptar y verificar contraseñas (bcrypt)
- Crear y validar tokens JWT
- Obtener el usuario actual a partir del token
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.usuario import UsuarioDB
from app.schemas.usuario import TokenData

# -------------------------------------------------------------------
# HASHING DE CONTRASEÑAS
# -------------------------------------------------------------------

# Configuración del algoritmo de encriptación (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica si una contraseña en texto plano coincide con su hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera un hash seguro a partir de una contraseña en texto plano"""
    return pwd_context.hash(password)

# -------------------------------------------------------------------
# AUTENTICACIÓN Y TOKENS JWT
# -------------------------------------------------------------------

# Configuración del esquema OAuth2: indica a FastAPI que el token se obtiene en /api/v1/auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def authenticate_user(db: Session, username: str, password: str):
    """
    Busca un usuario por nombre de usuario y verifica su contraseña
    Retorna el usuario si es correcto, o False si falla
    """
    usuario = db.query(UsuarioDB).filter(UsuarioDB.username == username).first()
    if not usuario or not verify_password(password, usuario.hashed_password):
        return False
    return usuario

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Crea un token JWT con fecha de expiración.
    - data: diccionario con la información a incluir (ej: {"sub": "username"})
    - expires_delta: tiempo de vida opcional (si no se da, usa el valor de settings)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(db: Session = Depends(), token: str = Depends(oauth2_scheme)):
    """
    Obtiene el usuario actual a partir del token JWT enviado en el header
    - Verifica que el token sea válido y no haya expirado
    - Busca el usuario en la base de datos
    - Si algo falla, lanza error 401 (No autorizado)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificar el token usando la clave secreta
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")  # "sub" es el nombre de usuario
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    usuario = db.query(UsuarioDB).filter(UsuarioDB.username == token_data.username).first()
    if usuario is None:
        raise credentials_exception
    return usuario

def get_current_active_user(current_user: UsuarioDB = Depends(get_current_user)):
    """
    Dependencia que se usa en los endpoints protegidos
    - Toma el usuario actual (de get_current_user) y verifica que esté activo
    - Si está inactivo, lanza error 400
    """
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user