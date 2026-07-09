"""
Servicio de Refresh Tokens.
"""
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshTokenDB
from app.models.usuario import UsuarioDB
from app.core.exceptions import AuthenticationError
from app.core.config import settings

REFRESH_TOKEN_EXPIRE_DAYS = 7

def generar_refresh_token() -> str:
    return secrets.token_urlsafe(64)

def crear_refresh_token(db: Session, user_id: int) -> RefreshTokenDB:
    token_str = generar_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshTokenDB(
        token=token_str,
        user_id=user_id,
        expires_at=expires_at,
        revoked=False
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def verificar_refresh_token(db: Session, token_str: str) -> UsuarioDB:
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == token_str).first()
    if not db_token:
        raise AuthenticationError("Refresh token inválido")
    if db_token.revoked:
        raise AuthenticationError("Refresh token revocado")
    if db_token.expires_at < datetime.now(timezone.utc):
        raise AuthenticationError("Refresh token expirado")
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == db_token.user_id).first()
    if not usuario or not usuario.activo:
        raise AuthenticationError("Usuario no válido o inactivo")
    return usuario

def revocar_refresh_token(db: Session, token_str: str):
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == token_str).first()
    if db_token:
        db_token.revoked = True
        db.commit()

def revocar_todos_refresh_tokens(db: Session, user_id: int):
    db.query(RefreshTokenDB).filter(RefreshTokenDB.user_id == user_id).update({"revoked": True})
    db.commit()

def rotar_refresh_token(db: Session, old_token_str: str):
    """
    Rota un refresh token: verifica, revoca el anterior y crea uno nuevo.
    Devuelve el usuario y el nuevo token.
    """
    usuario = verificar_refresh_token(db, old_token_str)
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == old_token_str).first()
    if db_token:
        db_token.revoked = True
        db.commit()
    nuevo_token = crear_refresh_token(db, usuario.id)
    return usuario, nuevo_token

def limpiar_tokens_expirados(db: Session):
    """Elimina tokens expirados o revocados."""
    now = datetime.now(timezone.utc)
    db.query(RefreshTokenDB).filter(
        (RefreshTokenDB.expires_at < now) | (RefreshTokenDB.revoked == True)
    ).delete(synchronize_session=False)
    db.commit()