# Contexto del proyecto — Volantines Strong

Este archivo existe para que un agente nuevo (o una persona) pueda retomar el trabajo **sin leer toda la conversación**. Contiene decisiones, estado real y pendientes.

Repo: `https://github.com/Christian01215/Volantines-strong.git`
Rama: `main`
Working directory original: `/home/christiant/Escritorio/Volantines_DE_CERO/BASE`

---

## 1. Objetivo original

1. Replicar `refvisual/index.html` **1:1** en Django (tienda). ✅
2. Replicar `refvisual/admin.html` **1:1** en Django (panel admin). ✅
3. Agregar checkout con comprobante de pago obligatorio y correo de verificación al dueño usando **Resend**. ✅

Regla visual: `refvisual/` es la **única fuente de verdad**. No simplificar ni omitir clases, estilos ni scripts. Reemplazar rutas relativas por `{% static '...' %}`.

`refvisual/` sólo contiene `index.html`, `admin.html`, `css/styles.css` y 3 PNG. **No hay archivos `.js` originales**: `store.js`, `cart.js`, `supabase-client.js` y `admin.js` fueron reconstruidos y validados con `node --check`.

---

## 2. Estado actual

Último commit: `66918c4` — *Fix admin login with duplicate emails, transfer payment and image URL handling*. Ya pusheado a `origin/main`.

Historial relevante:

```text
66918c4 Fix admin login with duplicate emails, transfer payment and image URL handling
f8f78fc Replicate admin.html 1:1, add Resend checkout notification with payment receipt
8d881d2 Configurar variables de entorno, estilos base y conexion Supabase
d917d8c Load all sensitive config from environment and use dj-database-url
5a1fe7c Excluir entorno virtual y .env en .gitignore
c0cf356 Replicate refvisual/index.html 1:1 in Django storefront and wire DB products
15f39e9 Initial project structure with Django, Supabase integration, and visual designs
```

Verificaciones ya pasadas:

- `python manage.py check` → sin errores.
- `node --check static/js/*.js` → OK.
- Diff del `<head>` y scripts finales del admin contra `refvisual/admin.html` → **0 líneas de diferencia** normalizando `{% static %}`.
- Login con emails duplicados → las 4 combinaciones de usuario/correo + contraseña funcionan.
- Checkout end-to-end con backend en memoria → 1 correo a `ADMIN_EMAIL` con adjunto.
- Guardado de imagen local → `image.name = products/2/main/prueba.png`, `src = /media/products/2/main/prueba.png`, sin `/media/media/`.

---

## 3. Decisiones tomadas

### Frontend / Admin
- El admin **no hereda** `templates/base.html`: tiene `templates/admin_panel/base_admin.html` propio para no traer navbar/footer de la tienda.
- `admin.html` se partió en `base_admin.html` + `login.html` + `dashboard.html`, conservando el markup exacto de cada bloque.
- Login con `authenticate()` / `login()` de Django y usuarios `is_staff`. Se eliminaron credenciales hardcodeadas (`admin@volantinesstrong.cl / admin123`).
- Logout por POST con CSRF.

### Checkout
- Comprobante **obligatorio**.
- Guardado en bucket `payment-receipts` de Supabase Storage, con fallback a `MEDIA_ROOT` local.
- Estado inicial del pedido: `pendiente`. El admin verifica y cambia a `pago_confirmado`.
- Precios se validan contra `Product` en BD; **no se confía** en `cart_json` del cliente.
- Medio de pago: **sólo transferencia bancaria**. Webpay y Mercado Pago quedaron deshabilitados con texto “próximamente”.

### Correo
- Resend vía API HTTP, sin SDK oficial (usa `httpx`, ya incluido por Supabase).
- Variables: `RESEND_API_KEY`, `ADMIN_EMAIL`, `DEFAULT_FROM_EMAIL`.
- Sin key, se usa backend de consola para desarrollo.
- El correo al dueño incluye el comprobante **adjunto** en base64.

### Storage
- Imágenes de producto: bucket `product-images`.
- Comprobantes: bucket `payment-receipts`.
- `image_url` (URL remota) se usa primero; si no, `image.url` local. Nunca se guarda una URL dentro de `ImageField`.
- Si falla Supabase, se guarda localmente y se muestra un `messages.warning` con el error real.

---

## 4. Problemas que se resolvieron (y cómo)

1. **No podía entrar al admin propio** pero sí al `/admin/` de Django.
   - Causa: el input era `type="email"` y el código buscaba un solo usuario por email.
   - Fix: input `type="text"` con label “Usuario o correo administrador”, campo `admin_identifier`, y el view itera `User.objects.filter(email__iexact=identifier)` probando contraseña en cada uno. Funciona aunque haya dos superusuarios con el mismo correo.

2. **Medio de pago**: antes aparecían Webpay y Mercado Pago.
   - Fix: opción activa `transferencia` + datos genéricos de Banco Estado; las otras dos opciones `disabled` con “próximamente”.
   - Esos datos también se agregan al correo al dueño.

3. **Imágenes que no aparecían**.
   - Causa: se guardaba el resultado de `default_storage.url()` (tipo `/media/...`) dentro del `ImageField`, y Django le agregaba otro `/media/` → `/media/media/...`. Además el bucket no existía y el error se silenciaba.
   - Fix: `_upload_image()` devuelve `(remote_url, local_path, error)`. Remota → `image_url`; local → ruta en `image`. Migración `products/0004_*`.

4. **`DATABASE_URL=` vacía** hacía que `dj_database_url.config()` devolviera una config vacía.
   - Fix: en `settings.py`, si la variable está vacía se usa SQLite explícitamente.

5. **Supabase inalcanzable desde esta máquina**: `Network is unreachable` al IPv6 del host.
   - Workaround: dejar `DATABASE_URL=` vacío y usar SQLite local. En otro PC con IPv6 podría funcionar directo.

6. **Buckets**: `check_storage` reportó `FALTA` para ambos; `--create` dio `403 Unauthorized · new row violates row-level security policy` con la key actual (no es service_role). Hay que crearlos a mano en el dashboard.

---

## 5. Archivos clave

| Archivo | Rol |
| --- | --- |
| `refvisual/index.html`, `refvisual/admin.html` | Fuente visual única. |
| `templates/base.html` | Checkout global (names, `enctype`, `cart_json`, `receipt`). |
| `templates/storefront/index.html` | Tienda 1:1. |
| `templates/admin_panel/base_admin.html` | Head exacto, estilos inline y scripts finales del admin. |
| `templates/admin_panel/login.html` | Login con `admin_identifier`, `admin_password`, CSRF. |
| `templates/admin_panel/dashboard.html` | Catálogo, stock, ventas, filas dinámicas. |
| `admin_panel/views.py` | Auth, CRUD de productos, acciones de pedidos, `_upload_image`. |
| `admin_panel/management/commands/check_storage.py` | Verifica/crea buckets. |
| `orders/views.py` | `checkout_submit`: valida carrito, crea orden, sube comprobante, envía correo. |
| `orders/services.py` | `upload_receipt()` y `send_owner_notification()`. |
| `config/email_backends.py` | `ResendEmailBackend` vía `httpx`. |
| `config/settings.py` | Env, DB, media, Resend, `LOGIN_URL`. |
| `static/js/cart.js` | Envía `FormData` al checkout y limpia carrito. |
| `static/js/admin.js` | Exportar Excel, estados, notificar, eliminar, editar, preview galería. |
| `.env.example` | Plantilla sin valores sensibles. |

---

## 6. Variables de entorno (sin valores)

No leer ni imprimir `.env`. Completar a mano a partir de `.env.example`:

```text
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
DATABASE_URL=
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_STORAGE_BUCKET=product-images
SUPABASE_RECEIPTS_BUCKET=payment-receipts
ADMIN_EMAIL=
DEFAULT_FROM_EMAIL=
RESEND_API_KEY=
EMAIL_BACKEND=   # opcional
```

---

## 7. Pendientes / validación en otro PC

1. Clonar el repo y recrear `.venv` (no copiar el virtualenv).
2. Copiar `.env.example` → `.env` y completar valores.
3. Crear en Supabase → Storage → Buckets, **públicos**:
   - `product-images`
   - `payment-receipts`
4. Aplicar migraciones contra Supabase (en la máquina original falló por IPv6):
   ```bash
   python manage.py migrate
   ```
5. Crear/confirmar el superusuario que se quiera usar:
   ```bash
   python manage.py createsuperuser
   ```
   Para borrar el duplicado:
   ```bash
   python manage.py shell -c "from django.contrib.auth.models import User; [print(u.id, u.username, u.email) for u in User.objects.filter(is_superuser=True)]"
   python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(id=ID).delete()"
   ```
   Usuarios observados en local: `id=1 username='5625' email='ctorresj@utem.cl'` e `id=2 username='admin@volantinesstrong.cl' email=''` (no se borró ninguno; falta decisión del usuario).
6. Verificar remitente en Resend y configurar `ADMIN_EMAIL`.
7. Probar flujo completo: carrito → checkout con comprobante → correo → pedido en `03 / VENTAS`.
8. Probar admin 1:1 contra `refvisual/admin.html`: login, alta/edición/eliminación de producto, galería, cambio de estado, notificar, exportar Excel, logout.

---

## 8. Comandos de verificación

```bash
python manage.py check
python manage.py check_storage
python manage.py makemigrations --check --dry-run
for f in static/js/*.js; do node --check "$f"; done
git status --short
git log --oneline -3
```

Checklist de seguridad antes de publicar:

```bash
git log --all --oneline -- .env        # debe salir vacío
git check-ignore -v .env .venv db.sqlite3 media/
git ls-tree -r --name-only HEAD | grep -E '^\.env$'   # debe salir vacío
```

---

## 9. Notas para la sesión siguiente

- El usuario escribe en español: responder en español.
- Usar siempre `.venv/bin/python` (o activar `.venv`), no `/home/christiant/venv`.
- `SECRET_KEY` sin valor lanza `ImproperlyConfigured` al cargar settings.
- No simplificar el HTML de referencia bajo ningún concepto; los diffs permitidos son sólo `{% static %}`, CSRF, `action`, `name` y filas dinámicas.
- El chat **no** viaja en el repo: este `CONTEXTO.md` reemplaza al transcript.
