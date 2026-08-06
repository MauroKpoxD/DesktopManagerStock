# Mejoras y correcciones aplicadas

Resumen de todo lo revisado y cambiado en esta pasada. Organizado por severidad.

## 🔴 Bugs críticos (rompían el proyecto o los datos)

1. **`docker-compose.yml` no tenía servicio `db`.** El servicio `api` declaraba
   `depends_on: db: condition: service_healthy`, pero no existía ningún
   servicio `db` en el archivo. `docker compose up` fallaba siempre.
   → Se agregó el servicio `db` (PostgreSQL 16), con volumen persistente y
   healthcheck (`pg_isready`).

2. **`server/requirements.txt` estaba en UTF-16 LE** (probablemente guardado
   con PowerShell `Out-File` sin especificar encoding). `pip install -r
   requirements.txt` falla o se comporta mal con ese archivo en muchos
   entornos. → Convertido a UTF-8.

3. **Eliminar un producto borraba su historial de movimientos.** El modelo
   `MovimientoDB.producto_id` tiene `ondelete="CASCADE"`, y `eliminar_producto`
   hacía un `DELETE` físico. Resultado: justo la auditoría que el proyecto
   anuncia como característica se perdía al borrar un producto. → Ahora
   `DELETE /productos/{id}` es un **soft delete** (`activo=false`); el
   historial se conserva. Se agregó `PATCH /productos/{id}/reactivar`.

4. **`scripts/levantar_docker.ps1` no usaba Docker.** Era una copia idéntica
   de `levantar_servicio.ps1` (ambos hacían `python main.py` directo). El
   README ya documentaba que este script debía levantar el contenedor con
   docker-compose, pero no lo hacía. → Reescrito para validar Docker, crear
   `.env`/carpetas necesarias y ejecutar `docker compose up -d --build`.

## 🟠 Bugs de seguridad / lógica

5. **Login no revisaba si el usuario estaba activo.** `authenticate_user`
   solo comparaba usuario/contraseña; un usuario desactivado por un admin
   podía igual iniciar sesión y obtener tokens válidos (fallaba recién en el
   siguiente request). → Ahora el login rechaza usuarios inactivos.

6. **Condición de carrera en ajuste de stock.** Dos solicitudes concurrentes
   de salida de stock podían leer el mismo valor, pasar ambas la validación y
   dejar el stock negativo. → Se agregó `SELECT ... FOR UPDATE` (solo contra
   PostgreSQL, el motor de producción; SQLite —usado en tests— lo ignora
   deliberadamente en el código para no romper nada).

7. **`CORS_ORIGINS="*"` + `allow_credentials=True`** es una combinación que
   los navegadores rechazan igual, pero la app no lo detectaba y arrancaba
   igual, dejando un CORS roto en producción sin avisar. → Se agregó
   validación en el arranque.

8. **Contraseña de administrador en texto plano sin restringir permisos del
   archivo.** `logs/.admin_password.txt` se creaba con los permisos por
   defecto del proceso. → Ahora se restringe a `600` (solo el dueño puede
   leerlo) donde el sistema operativo lo permite.

## 🟡 Funcionalidad incompleta / huérfana

9. **`UsuarioUpdate` existía pero ningún endpoint lo usaba.** No había forma
   de listar usuarios, cambiar el rol de alguien, desactivar una cuenta, ver
   el propio perfil o cambiar la propia contraseña. → Se agregaron:
   - `GET /auth/me`, `PUT /auth/me`, `POST /auth/me/password`
   - `GET /usuarios`, `GET /usuarios/{id}`, `PUT /usuarios/{id}` (solo admin)

10. **`REFRESH_TOKEN_EXPIRE_DAYS` estaba en `.env.example` pero el código
    usaba una constante fija de 7 días**, ignorando la variable de entorno.
    → Ahora es un setting real (`settings.refresh_token_expire_days`).

11. **El healthcheck de Docker apuntaba a `/` (bienvenida),** que responde
    200 aunque la base de datos esté caída. → Nuevo endpoint real
    `GET /health` que verifica conectividad a la base de datos.

12. **Sin paginación real:** los listados de productos y movimientos no
    exponían el total de registros, obligando al cliente a adivinar cuántas
    páginas hay. → Se agregó el header `X-Total-Count` en ambos listados.

## 🔵 Calidad de código / mantenibilidad

13. **Manejo de errores repetido en cada endpoint** (`try/except` para
    traducir `NotFoundError`/`ValidationError`/`ConflictError` a
    `HTTPException`). Frágil: un endpoint nuevo que olvide el `try/except`
    termina devolviendo un 500 genérico. → Se centralizó con
    `@app.exception_handler(...)` en `main.py`, manteniendo los mismos
    códigos de estado que ya usaba la app (no cambia el contrato con el
    cliente).

14. **`Dockerfile` con restos de una versión anterior con SQLite**
    (`RUN touch stock.db && chmod 666 stock.db`), sin sentido en una app que
    usa PostgreSQL. Además corría como root sin coincidir con el
    `user: "1000:1000"` de `docker-compose.yml`. → Limpiado, se agregó un
    usuario sin privilegios y un `HEALTHCHECK`.

15. **`logout` capturaba `except Exception` genérico** sobre una función que
    nunca lanza excepciones, camuflando cualquier error real (por ejemplo, de
    base de datos) como un 400 "manejado". → Eliminado ese bloque.

16. **Sin herramienta de migraciones (Alembic).** El proyecto solo usa
    `Base.metadata.create_all()`, que crea tablas nuevas pero nunca agrega
    columnas a tablas existentes. Al agregar la columna `activo` esto
    hubiera roto cualquier base de datos ya desplegada. → Se agregó una
    migración ligera idempotente (`ensure_schema_compat()` en
    `app/core/database.py`) que agrega la columna si falta. **Recomendación
    a futuro:** si el esquema sigue creciendo, migrar a Alembic en vez de
    seguir con este parche manual.

## Notas para quien despliegue esto

- Antes de `docker compose up`, crea `server/.env` a partir de
  `.env.example` y ajusta `SECRET_KEY`, `DB_PASSWORD`, etc.
  (`scripts/levantar_docker.ps1` ya lo hace automáticamente en Windows).
- Los volúmenes `./logs`, `./reports`, `./usuarios` se montan sobre el
  usuario `1000:1000` del contenedor; si tu usuario de host tiene otro
  UID/GID, ajusta esa línea en `docker-compose.yml` o crea esas carpetas
  con `chown` acorde.
- Cambia la contraseña del usuario `admin` apenas puedas con
  `POST /api/v1/auth/me/password`, y borra
  `server/logs/.admin_password.txt` después.
