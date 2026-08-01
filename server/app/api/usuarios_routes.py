"""
Rutas administrativas de usuarios.

No existían antes: el esquema UsuarioUpdate estaba definido pero huérfano,
sin ningún endpoint que lo usara. Con esto un admin puede listar usuarios,
ver el detalle de uno y cambiar su rol/estado activo.
"""
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.roles import require_roles, Rol
from app.models.usuario import UsuarioDB
from app.schemas.usuario import Usuario, UsuarioUpdate, UsuarioCreate, PasswordTemporal
from app.services.usuario_service import (
    listar_usuarios,
    obtener_usuario_por_id,
    actualizar_usuario_admin,
    crear_usuario_admin,
    resetear_password_admin,
)

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])


@router.get("", response_model=List[Usuario])
def get_usuarios(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN])),
):
    total = db.query(UsuarioDB).count()
    response.headers["X-Total-Count"] = str(total)
    return listar_usuarios(db, skip=skip, limit=limit)


@router.post("", response_model=Usuario, status_code=status.HTTP_201_CREATED)
def create_usuario(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN])),
):
    """
    A diferencia de POST /auth/register (público, siempre crea rol='lector'),
    este endpoint es solo para admins y permite elegir el rol del usuario
    nuevo directamente (admin/editor/lector).
    """
    return crear_usuario_admin(db, datos, current_user)


@router.get("/{usuario_id}", response_model=Usuario)
def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN])),
):
    return obtener_usuario_por_id(db, usuario_id)


@router.put("/{usuario_id}", response_model=Usuario)
def update_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN])),
):
    return actualizar_usuario_admin(db, usuario_id, datos, current_user)


@router.post("/{usuario_id}/resetear-password", response_model=PasswordTemporal)
def resetear_password(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioDB = Depends(require_roles([Rol.ADMIN])),
):
    """
    Genera una contraseña temporal para un usuario que perdió acceso a la
    suya. La contraseña viaja en texto plano SOLO en esta respuesta (no se
    guarda en ningún lado); el admin debe copiarla y pasársela por un canal
    seguro a la persona, que debería cambiarla apenas entre
    (POST /auth/me/password).
    """
    usuario, password_temporal = resetear_password_admin(db, usuario_id, current_user)
    return PasswordTemporal(usuario=usuario, password_temporal=password_temporal)
