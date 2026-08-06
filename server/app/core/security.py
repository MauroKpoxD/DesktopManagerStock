"""
Funciones de hash, JWT y dependencias de autenticación.
"""
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.usuario import UsuarioDB
from app.schemas.usuario import TokenData

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def authenticate_user(db: Session, username: str, password: str):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.username == username).first()
    if not usuario or not verify_password(password, usuario.hashed_password):
        return False
<<<<<<< HEAD
=======
    if not usuario.activo:
        # Antes esto no se validaba aquí: una cuenta desactivada por un admin
        # podía igual hacer login y recibir un access_token + refresh_token
        # válidos, y solo fallaba en la primera llamada a un endpoint
        # protegido (get_current_active_user). Es mejor rechazarlo ya en el
        # login: evita emitir tokens innecesarios y da un mensaje más claro.
        return False
>>>>>>> feature/interfaz-y-reconstruccion
    return usuario

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
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
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user