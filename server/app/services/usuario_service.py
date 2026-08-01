"""
Servicio de usuarios: perfil propio y administración de cuentas.

Antes el esquema UsuarioUpdate existía en app/schemas/usuario.py pero ningún
endpoint lo usaba: no había forma de cambiar la contraseña, desactivar un
usuario o listar los usuarios existentes sin ir directo a la base de datos.
"""
from sqlalchemy.orm import Session
import secrets
from app.models.usuario import UsuarioDB
from app.schemas.usuario import UsuarioUpdate, UsuarioCreate, PerfilUpdate, CambioPassword
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.core.logging_config import get_logger
from app.services.refresh_token_service import revocar_todos_refresh_tokens

logger = get_logger(__name__)


def listar_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UsuarioDB).order_by(UsuarioDB.id).offset(skip).limit(limit).all()


def obtener_usuario_por_id(db: Session, usuario_id: int) -> UsuarioDB:
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise NotFoundError(f"Usuario con ID {usuario_id} no encontrado")
    return usuario


def crear_usuario_admin(db: Session, datos: UsuarioCreate, admin_actual: UsuarioDB) -> UsuarioDB:
    """
    Permite a un admin crear un usuario directamente, con el rol que elija
    (a diferencia de POST /auth/register, que es público y siempre fuerza
    rol='lector' por seguridad). Antes esta era la única forma de sumar
    gente al sistema: pedirle a cada persona que se autorregistrara, sin
    poder decidir su rol de entrada.
    """
    if db.query(UsuarioDB).filter(UsuarioDB.username == datos.username).first():
        raise ConflictError(f"Ya existe un usuario con el nombre de usuario '{datos.username}'")
    if db.query(UsuarioDB).filter(UsuarioDB.email == datos.email).first():
        raise ConflictError(f"El email '{datos.email}' ya está en uso")

    from app.core.roles import Rol
    rol = datos.rol or Rol.LECTOR.value
    if rol not in [r.value for r in Rol]:
        raise ValidationError(f"Rol inválido: '{rol}'")

    usuario = UsuarioDB(
        username=datos.username,
        email=datos.email,
        hashed_password=get_password_hash(datos.password),
        rol=rol,
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    logger.info(f"Usuario {usuario.username} (ID {usuario.id}) creado por admin {admin_actual.username} con rol {rol}")
    return usuario


def actualizar_usuario_admin(db: Session, usuario_id: int, datos: UsuarioUpdate, admin_actual: UsuarioDB) -> UsuarioDB:
    """Permite a un admin cambiar email, rol o estado activo de cualquier usuario."""
    usuario = obtener_usuario_por_id(db, usuario_id)

    if datos.email and datos.email != usuario.email:
        existente = db.query(UsuarioDB).filter(UsuarioDB.email == datos.email).first()
        if existente:
            raise ConflictError(f"El email '{datos.email}' ya está en uso")
        usuario.email = datos.email

    if datos.rol is not None:
        from app.core.roles import Rol
        if datos.rol not in [r.value for r in Rol]:
            raise ValidationError(f"Rol inválido: '{datos.rol}'")
        if usuario.id == admin_actual.id and datos.rol != "admin":
            # Evita que un admin se quite a sí mismo el rol y quede el
            # sistema sin administradores accesibles.
            raise ValidationError("No puedes quitarte a ti mismo el rol de administrador")
        usuario.rol = datos.rol

    if datos.activo is not None:
        if usuario.id == admin_actual.id and datos.activo is False:
            raise ValidationError("No puedes desactivar tu propia cuenta")
        usuario.activo = datos.activo
        if datos.activo is False:
            # Si se desactiva la cuenta, sus refresh tokens dejan de servir
            # para renovar sesión, cerrando cualquier sesión activa.
            revocar_todos_refresh_tokens(db, usuario.id)

    db.commit()
    db.refresh(usuario)
    logger.info(f"Usuario {usuario.username} (ID {usuario.id}) actualizado por admin {admin_actual.username}")
    return usuario


def actualizar_perfil_propio(db: Session, usuario_actual: UsuarioDB, datos: PerfilUpdate) -> UsuarioDB:
    if datos.email != usuario_actual.email:
        existente = db.query(UsuarioDB).filter(UsuarioDB.email == datos.email).first()
        if existente:
            raise ConflictError(f"El email '{datos.email}' ya está en uso")
        usuario_actual.email = datos.email
        db.commit()
        db.refresh(usuario_actual)
    return usuario_actual


def resetear_password_admin(db: Session, usuario_id: int, admin_actual: UsuarioDB) -> tuple[UsuarioDB, str]:
    """
    Genera una contraseña temporal nueva para un usuario que no puede
    entrar (se olvidó la suya) y no tiene forma de resetearla él mismo, ya
    que POST /auth/me/password exige conocer la contraseña actual. Devuelve
    la contraseña en texto plano UNA sola vez (en la respuesta de este
    endpoint); no queda guardada en ningún lado, así que el admin tiene que
    copiarla y pasársela a la persona en el momento.
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    password_temporal = secrets.token_urlsafe(9) + "!A1"  # asegura que cumpla la regla de fortaleza
    usuario.hashed_password = get_password_hash(password_temporal)
    db.commit()
    db.refresh(usuario)
    # Igual que un cambio de contraseña normal: se cierra cualquier sesión
    # activa, ya que se asume que el usuario perdió el acceso.
    revocar_todos_refresh_tokens(db, usuario.id)
    logger.info(f"Contraseña de {usuario.username} (ID {usuario.id}) reseteada por admin {admin_actual.username}")
    return usuario, password_temporal


def cambiar_password_propio(db: Session, usuario_actual: UsuarioDB, datos: CambioPassword) -> UsuarioDB:
    if not verify_password(datos.password_actual, usuario_actual.hashed_password):
        raise ValidationError("La contraseña actual es incorrecta")
    if datos.password_actual == datos.password_nueva:
        raise ValidationError("La nueva contraseña debe ser distinta de la actual")
    usuario_actual.hashed_password = get_password_hash(datos.password_nueva)
    db.commit()
    db.refresh(usuario_actual)
    # Al cambiar la contraseña, se revocan todas las sesiones (refresh tokens)
    # existentes, tal como hacen otras plataformas: si alguien más tenía una
    # sesión abierta (o el cambio se debe a que la cuenta fue comprometida),
    # queda desconectado.
    revocar_todos_refresh_tokens(db, usuario_actual.id)
    logger.info(f"Contraseña actualizada para el usuario {usuario_actual.username} (ID {usuario_actual.id})")
    return usuario_actual
