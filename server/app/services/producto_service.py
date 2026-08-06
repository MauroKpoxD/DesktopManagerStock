"""
Servicio de productos con lógica de negocio.
"""
<<<<<<< HEAD
=======
import csv
import io
from pydantic import ValidationError as PydanticValidationError
>>>>>>> feature/interfaz-y-reconstruccion
from sqlalchemy.orm import Session
from app.models.producto import ProductoDB
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.models.movimiento import MovimientoDB
from app.schemas.movimiento import MovimientoBase
from app.core.logging_config import get_logger
from app.core.exceptions import NotFoundError, ValidationError, ConflictError

logger = get_logger(__name__)

<<<<<<< HEAD
def listar_productos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProductoDB).order_by(ProductoDB.id).offset(skip).limit(limit).all()

def obtener_producto_por_id(db: Session, producto_id: int):
=======
def listar_productos(db: Session, skip: int = 0, limit: int = 100, incluir_inactivos: bool = False, categoria: str = None):
    query = db.query(ProductoDB)
    if not incluir_inactivos:
        query = query.filter(ProductoDB.activo.is_(True))
    if categoria:
        query = query.filter(ProductoDB.categoria == categoria)
    return query.order_by(ProductoDB.id).offset(skip).limit(limit).all()

def contar_productos(db: Session, incluir_inactivos: bool = False, categoria: str = None) -> int:
    query = db.query(ProductoDB)
    if not incluir_inactivos:
        query = query.filter(ProductoDB.activo.is_(True))
    if categoria:
        query = query.filter(ProductoDB.categoria == categoria)
    return query.count()

def listar_categorias(db: Session):
    """Categorías distintas ya usadas (para poblar un filtro en el cliente)."""
    filas = (
        db.query(ProductoDB.categoria)
        .filter(ProductoDB.categoria.isnot(None), ProductoDB.activo.is_(True))
        .distinct()
        .order_by(ProductoDB.categoria)
        .all()
    )
    return [f[0] for f in filas]

def obtener_producto_por_id(db: Session, producto_id: int):
    # Se busca sin filtrar por "activo": un producto desactivado debe poder
    # seguir consultándose por ID (por ejemplo, para ver su historial de
    # movimientos o reactivarlo), solo se oculta de los listados generales.
>>>>>>> feature/interfaz-y-reconstruccion
    producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()
    if not producto:
        raise NotFoundError(f"Producto con ID {producto_id} no encontrado")
    return producto

def crear_producto(db: Session, producto: ProductoCreate):
    existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto.nombre).first()
    if existente:
<<<<<<< HEAD
        raise ConflictError(f"Ya existe un producto con el nombre '{producto.nombre}'")
=======
        if existente.activo:
            raise ConflictError(f"Ya existe un producto con el nombre '{producto.nombre}'")
        raise ConflictError(
            f"Ya existe un producto desactivado con el nombre '{producto.nombre}'. "
            f"Reactívalo con PUT /productos/{existente.id} (activo=true) en vez de crear uno nuevo."
        )
>>>>>>> feature/interfaz-y-reconstruccion
    db_producto = ProductoDB(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    logger.info(f"Producto creado: {db_producto.nombre} (ID {db_producto.id})")
    return db_producto

<<<<<<< HEAD
def actualizar_producto(db: Session, producto_id: int, producto_update: ProductoUpdate):
    db_producto = obtener_producto_por_id(db, producto_id)
=======
def actualizar_producto(db: Session, producto_id: int, producto_update: ProductoUpdate, es_admin: bool = False):
    db_producto = obtener_producto_por_id(db, producto_id)
    if producto_update.activo is not None and not es_admin:
        # Mismo criterio que DELETE /productos/{id} y PATCH /reactivar:
        # activar/desactivar un producto es una operación de administrador,
        # no algo que un editor deba poder hacer de paso al actualizar el precio.
        raise ValidationError("Solo un administrador puede activar o desactivar un producto")
>>>>>>> feature/interfaz-y-reconstruccion
    if producto_update.nombre and producto_update.nombre != db_producto.nombre:
        existente = db.query(ProductoDB).filter(ProductoDB.nombre == producto_update.nombre).first()
        if existente:
            raise ConflictError(f"Ya existe un producto con el nombre '{producto_update.nombre}'")
    update_data = producto_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_producto, key, value)
    # Las validaciones de rangos ya se hicieron en el schema, pero repetimos por seguridad
    if db_producto.stock_minimo > db_producto.stock_maximo:
        raise ValidationError("El stock mínimo no puede ser mayor que el máximo")
    if db_producto.stock > db_producto.stock_maximo:
        raise ValidationError(f"El stock actual ({db_producto.stock}) no puede superar el máximo ({db_producto.stock_maximo})")
    db.commit()
    db.refresh(db_producto)
    logger.info(f"Producto actualizado: {db_producto.nombre} (ID {db_producto.id})")
    return db_producto

def eliminar_producto(db: Session, producto_id: int):
<<<<<<< HEAD
    db_producto = obtener_producto_por_id(db, producto_id)
    db.delete(db_producto)
    db.commit()
    logger.info(f"Producto eliminado: ID {producto_id}")
    return True

def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_entrada: bool, usuario_id: int):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser positiva")
    producto = obtener_producto_por_id(db, producto_id)
=======
    """
    Antes esto hacía un DELETE físico. Como MovimientoDB.producto_id tiene
    ondelete="CASCADE", borrar un producto borraba en cascada TODO su
    historial de movimientos, perdiendo la auditoría (una de las
    características que el proyecto anuncia). Ahora se hace un soft delete:
    el producto deja de aparecer en los listados y no admite nuevos
    movimientos de stock, pero su historial se conserva intacto.
    """
    db_producto = obtener_producto_por_id(db, producto_id)
    if not db_producto.activo:
        raise ValidationError(f"El producto '{db_producto.nombre}' ya está desactivado")
    db_producto.activo = False
    db.commit()
    logger.info(f"Producto desactivado (soft delete): {db_producto.nombre} (ID {producto_id})")
    return True

def reactivar_producto(db: Session, producto_id: int):
    db_producto = obtener_producto_por_id(db, producto_id)
    if db_producto.activo:
        raise ValidationError(f"El producto '{db_producto.nombre}' ya está activo")
    db_producto.activo = True
    db.commit()
    db.refresh(db_producto)
    logger.info(f"Producto reactivado: {db_producto.nombre} (ID {producto_id})")
    return db_producto

def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_entrada: bool, usuario_id: int):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser positiva")

    # SELECT ... FOR UPDATE: bloquea la fila del producto hasta que termine
    # la transacción. Sin esto, dos solicitudes concurrentes de salida de
    # stock (por ejemplo, dos cajeros vendiendo el último producto al mismo
    # tiempo) podían leer el mismo stock, pasar ambas la validación
    # "stock - cantidad >= 0" y dejar el stock en negativo.
    # Se aplica solo contra PostgreSQL (el motor de producción, según
    # settings.database_url): SQLite -usado en los tests- no soporta
    # bloqueo de filas y su nivel de aislamiento por archivo hace este
    # problema irrelevante ahí, así que evitamos cualquier incompatibilidad.
    query = db.query(ProductoDB).filter(ProductoDB.id == producto_id)
    if db.get_bind().dialect.name == "postgresql":
        query = query.with_for_update()
    producto = query.first()
    if not producto:
        raise NotFoundError(f"Producto con ID {producto_id} no encontrado")
    if not producto.activo:
        raise ValidationError(f"El producto '{producto.nombre}' está desactivado y no admite movimientos de stock")

>>>>>>> feature/interfaz-y-reconstruccion
    if es_entrada:
        nuevo_stock = producto.stock + cantidad
        if nuevo_stock > producto.stock_maximo:
            raise ValidationError(f"El stock no puede superar el máximo de {producto.stock_maximo}")
        producto.stock = nuevo_stock
        tipo = "entrada"
    else:
        if producto.stock - cantidad < 0:
            raise ValidationError("Stock insuficiente")
        producto.stock -= cantidad
        tipo = "salida"
    movimiento_data = MovimientoBase(
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        stock_resultante=producto.stock,
        usuario_id=usuario_id
    )
    db_movimiento = MovimientoDB(**movimiento_data.model_dump())
    db.add(db_movimiento)
    db.commit()
    db.refresh(producto)
    logger.info(f"Ajuste de stock: producto_id={producto_id}, usuario_id={usuario_id}, tipo={tipo}, cantidad={cantidad}, nuevo_stock={producto.stock}")
    return producto

def obtener_productos_con_stock_bajo(db: Session, umbral: int = None):
<<<<<<< HEAD
    if umbral is not None:
        return db.query(ProductoDB).filter(ProductoDB.stock <= umbral).all()
    else:
        return db.query(ProductoDB).filter(ProductoDB.stock <= ProductoDB.stock_minimo).all()
=======
    query = db.query(ProductoDB).filter(ProductoDB.activo.is_(True))
    if umbral is not None:
        return query.filter(ProductoDB.stock <= umbral).all()
    else:
        return query.filter(ProductoDB.stock <= ProductoDB.stock_minimo).all()

# Columnas reconocidas en el CSV de importación. "nombre" es la única
# obligatoria; el resto usa los valores por defecto de ProductoCreate si
# falta o viene vacía.
_COLUMNAS_CSV = ["nombre", "categoria", "sku", "precio", "stock", "stock_minimo", "stock_maximo", "proveedor_nombre", "proveedor_contacto"]

def importar_productos_csv(db: Session, contenido: str):
    """
    Importación masiva de productos desde un CSV (ver POST /productos/importar-csv).
    Antes, cargar un catálogo entero significaba crear cada producto a mano,
    uno por uno, desde el cliente.

    Se procesa fila por fila: si una fila falla (nombre duplicado, precio
    inválido, etc.) se omite con el motivo, pero NO aborta el resto de la
    importación. Devuelve un resumen con lo creado y lo omitido.
    """
    lector = csv.DictReader(io.StringIO(contenido))
    if lector.fieldnames is None:
        raise ValidationError("El archivo está vacío o no tiene encabezados.")

    encabezados_normalizados = {h.strip().lower() for h in lector.fieldnames}
    if "nombre" not in encabezados_normalizados:
        raise ValidationError(
            "El CSV debe tener al menos una columna 'nombre'. "
            f"Columnas esperadas (las demás son opcionales): {', '.join(_COLUMNAS_CSV)}"
        )

    creados = []
    omitidos = []
    total_filas = 0

    for numero_fila, fila_cruda in enumerate(lector, start=2):  # fila 1 = encabezados
        total_filas += 1
        fila = {(k or "").strip().lower(): (v.strip() if v else None) for k, v in fila_cruda.items()}
        nombre = fila.get("nombre")
        if not nombre:
            omitidos.append({"fila": numero_fila, "motivo": "Falta el nombre"})
            continue

        try:
            datos = ProductoCreate(
                nombre=nombre,
                categoria=fila.get("categoria") or None,
                sku=fila.get("sku") or None,
                proveedor_nombre=fila.get("proveedor_nombre") or None,
                proveedor_contacto=fila.get("proveedor_contacto") or None,
                precio=float(fila["precio"]) if fila.get("precio") else 0.01,
                stock=int(fila["stock"]) if fila.get("stock") else 0,
                stock_minimo=int(fila["stock_minimo"]) if fila.get("stock_minimo") else 5,
                stock_maximo=int(fila["stock_maximo"]) if fila.get("stock_maximo") else 100,
            )
            producto = crear_producto(db, datos)
            creados.append(producto.nombre)
        except (PydanticValidationError, ValueError) as e:
            omitidos.append({"fila": numero_fila, "motivo": f"Datos inválidos: {e}"})
        except ConflictError as e:
            omitidos.append({"fila": numero_fila, "motivo": str(e)})
        except ValidationError as e:
            omitidos.append({"fila": numero_fila, "motivo": str(e)})

    logger.info(f"Importación CSV: {len(creados)} creados, {len(omitidos)} omitidos de {total_filas} filas")
    return {"total_filas": total_filas, "creados": len(creados), "productos_creados": creados, "omitidos": omitidos}
>>>>>>> feature/interfaz-y-reconstruccion
