# Volantines Strong

Tienda online de volantines + panel de administración, hecha en Django. El frontend es una réplica 1:1 de los archivos de diseño en `refvisual/` (`index.html` para la tienda y `admin.html` para el admin).

Incluye carrito persistido en base de datos, checkout con **comprobante de pago obligatorio**, aviso por correo al dueño vía **Resend** (con el comprobante adjunto), confirmación automática al cliente, notificación cuando el pedido está listo, personalizador de carretes en Canvas, consulta de estado por código, reportes en el admin y login real de Django.

---

## Stack

- Django 6.1.3 / Python 3.12+ (probado con 3.14)
- PostgreSQL de Supabase (con fallback a SQLite local)
- Supabase Storage para imágenes de producto y comprobantes
- Resend para correo (backend HTTP propio, sin SDK extra)
- Tailwind/CDNs y JS vanilla reconstruidos desde el diseño de referencia

---

## Instalación local

```bash
git clone https://github.com/Christian01215/Volantines-strong.git
cd Volantines-strong

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # Windows: copy .env.example .env
# Editá .env a mano con tus valores (NUNCA lo subas al repo)

python manage.py migrate
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

Si `SECRET_KEY` no está definida, Django falla al arrancar a propósito. No hay valores secretos hardcodeados en el código.

---

## Variables de entorno

Copiá `.env.example` como `.env` y completá:

| Variable | Uso |
| --- | --- |
| `SECRET_KEY` | Obligatoria. Clave larga y aleatoria de Django. |
| `DEBUG` | `False` por defecto. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,0.0.0.0,.vercel.app` por defecto. |
| `DATABASE_URL` | Cadena de Supabase Postgres. **Vacía = SQLite local**. |
| `SUPABASE_URL` / `SUPABASE_KEY` | SDK de Supabase (Storage). |
| `SUPABASE_STORAGE_BUCKET` | Bucket de imágenes: `product-images`. |
| `SUPABASE_RECEIPTS_BUCKET` | Bucket de comprobantes: `payment-receipts`. |
| `SUPABASE_DESIGNS_BUCKET` | Bucket de diseños personalizados: `custom-designs`. |
| `ALLOW_LOCAL_STORAGE_FALLBACK` | Permite guardar en `media/` si Supabase falla. Por defecto sigue a `DEBUG`; en Vercel debe quedar en `False`. |
| `WHATSAPP_NUMBER` | Número usado en los enlaces `wa.me`. Vacío = links desactivados. |
| `BANK_NAME` / `BANK_ACCOUNT_TYPE` / `BANK_RUT` / `BANK_ACCOUNT` | Datos de transferencia mostrados en checkout y correos. |
| `BUSINESS_ADDRESS` | Dirección de retiro mostrada en tienda, correos y seguimiento. |
| `ADMIN_EMAIL` | Destinatario del aviso de compra. Por defecto `ctorresj@utem.cl`. |
| `DEFAULT_FROM_EMAIL` | Remitente verificado en Resend. |
| `RESEND_API_KEY` | Key de Resend. Sin ella se usa el backend de consola. |
| `EMAIL_BACKEND` | Opcional. Fuerza un backend manualmente. |

> Si `DATABASE_URL` está vacía se usa `db.sqlite3`. Eso es ideal para probar en un PC sin IPv6 (algunas redes no pueden llegar al host de Supabase, que sólo resolvía AAAA).

---

## Supabase Storage

Creá estos tres buckets en **Supabase → Storage → Buckets**, marcados como **públicos**:

- `product-images` → fotos de productos y galería.
- `payment-receipts` → comprobantes de pago.
- `custom-designs` → PNG exportados por el personalizador de carretes.

Para verificarlos:

```bash
python manage.py check_storage
```

Si tenés una `service_role` key podés intentar crearlos automáticamente:

```bash
python manage.py check_storage --create
```

> `products_product` y `products_productimage` son **tablas de base de datos**, no buckets. Los buckets se crean en el dashboard de Supabase.

Si la subida falla en **local/desarrollo** (`DEBUG=True` o `ALLOW_LOCAL_STORAGE_FALLBACK=True`), el código guarda el archivo en `media/` y muestra un `messages.warning` con el error real. En **producción/Vercel** no existe ese fallback: la vista devuelve un mensaje claro en lugar de un 500, porque el disco efímero no conservaría el archivo. Las imágenes se guardan como ruta en `ImageField` **o** como URL en `image_url` (nunca una URL dentro del `ImageField`, para evitar `/media/media/...`).

---

## Correo con Resend

Con `RESEND_API_KEY` configurada, el checkout envía **dos correos**: uno a `ADMIN_EMAIL` (por defecto `ctorresj@utem.cl`) y una confirmación al correo del comprador. El aviso al dueño incluye:

- Datos del cliente, RUT, teléfono y correo.
- Retiro en taller, fecha y franja horaria (los campos de despacho quedan sólo como datos históricos).
- Detalle de productos, costo, ganancia estimada y total.
- Medio de pago y datos de transferencia.
- Link al comprobante **y el archivo adjunto**.

Además, los cambios de estado a **Pago Confirmado**, **Preparando**, **Listo para Retiro**, **Retirado** y **Cancelado** envían automáticamente un aviso al comprador, una sola vez por estado. El panel permite reenviar el aviso al cliente y también reenviar el aviso de nueva compra al administrador.

Sin la key, los correos se imprimen en la terminal (backend consola), útil para desarrollo.

En el plan gratuito de Resend, `onboarding@resend.dev` sólo envía al correo de la cuenta: verificá tu propio remitente en `DEFAULT_FROM_EMAIL`.

---

## Medio de pago

Por ahora el único medio habilitado es **Transferencia bancaria**:

Los datos se leen de `.env` (`BANK_NAME`, `BANK_ACCOUNT_TYPE`, `BANK_RUT`, `BANK_ACCOUNT`) y se muestran en el checkout y en el correo al dueño. No hay datos bancarios hardcodeados. El asunto del correo debe indicar el número de pedido.

Webpay Plus y Mercado Pago figuran deshabilitados con la leyenda **“próximamente”**.

---

## Usuario administrador

El panel usa autenticación real de Django (`authenticate()` / `login()`), con `is_staff=True`. No hay credenciales hardcodeadas.

```bash
python manage.py createsuperuser
```

Podés iniciar sesión con el **usuario** o con el **correo**. Si hay varios usuarios con el mismo correo, el login prueba cada uno hasta encontrar la contraseña correcta.

Para listar o borrar superusuarios:

```bash
python manage.py shell -c "from django.contrib.auth.models import User; [print(u.id, repr(u.username), repr(u.email), u.is_superuser) for u in User.objects.filter(is_superuser=True)]"
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(id=ID).delete()"
```

---

## Rutas principales

| Ruta | Descripción |
| --- | --- |
| `/` | Tienda (réplica de `refvisual/index.html`). |
| `/producto/<slug>/` | Detalle de producto. |
| `/personalizar/<slug>/` | Personalizador de carretes (Canvas). |
| `/cart/carrito/` | Carrito persistido en BD. |
| `/cart/api/` | API JSON del carrito (`GET`, `POST`). |
| `/orders/checkout/` | Checkout con comprobante. |
| `/orders/pedido/` | Consulta de estado por código `VC########`. |
| `/orders/pedido/<code>/confirmado/` | Confirmación posterior al checkout. |
| `/admin-panel/login/` | Login del panel propio. |
| `/admin-panel/dashboard/` | Catálogo, stock, ventas y `04 / REPORTES`. |
| `/admin/` | Admin nativo de Django. |
| `/orders/admin/` | Lista administrativa de pedidos. |

---

## Comandos útiles

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test tests
python manage.py check_storage
for f in static/js/*.js; do node --check "$f"; done
```

`manage.py test` usa automáticamente `config/settings_test.py` (SQLite en memoria + correo en memoria), por lo que nunca toca la base de producción.

Migraciones incluidas:

- `orders/0002_*` → métodos de pago, entrega y comprobante.
- `orders/0003_*` → diseño personalizado por línea de pedido.
- `orders/0004_*` → costo por línea, aviso al dueño y dedupe de notificaciones.
- `products/0003_*` → descripción y galería de imágenes.
- `products/0004_*` → `image_url` e `ImageField` opcional en galería.
- `products/0005_*` → `cost` para calcular ganancias.
- `cart/0002_*` → `session_key` y diseño en el carrito.
- `cart/0003_*` → `session_key` no único (permite carritos históricos).

Las 5 categorías oficiales (Volantines, Carretes, Hilos, Accesorios, Maletas) se cargan con:

```bash
python manage.py loaddata categories
```

---

## Flujo de prueba

1. Levantá el server con `runserver`.
2. Cargá las categorías con `loaddata categories` y creá productos desde el admin (con imagen principal y galería).
3. Agregá un producto al carrito desde `/`. Probá también `/personalizar/<slug>/` en un carrete: exportar PNG y agregarlo al carrito.
4. En checkout completá datos (RUT válido) y **adjuntá un comprobante** (JPG/PNG/WebP/PDF, máx. 5 MB).
5. Registrá el pedido: debe aparecer un código `VC########` y dos correos (dueño y comprador).
6. Consultá el estado en `/orders/pedido/` con el código recibido.
7. Entrá a `/admin-panel/dashboard/` → sección `03 / VENTAS`: el pedido debe estar con link al comprobante; en `04 / REPORTES` revisá los indicadores.
8. Probá cambio de estado a *Listo para Retiro* (dispara correo automático), notificación manual, exportar Excel, editar/desactivar/reactivar producto y logout.

---

## Preparación para Vercel

El proyecto ya tiene lo que Vercel necesita para detectar Django de forma automática:

- `manage.py` en la raíz y `WSGI_APPLICATION` apuntando a `config.wsgi.application`.
- `config/wsgi.py` expone `application` y `app`.
- `STATIC_ROOT` configurado: Vercel ejecuta `collectstatic` y sirve los archivos por CDN.
- `vercel.json` con `maxDuration: 60` para la función de Python.
- `/health` responde `{"status": "ok"}` para smoke checks.

CLI instalada: `vercel --version` → 66.6.0.

### Token

El token de Vercel **no se sube a Git**. En tu `.env` local dejé placeholders comentados:

```text
# VERCEL_TOKEN=
# VERCEL_ORG_ID=
# VERCEL_PROJECT_ID=
```

Descomentá `VERCEL_TOKEN` y pegá tu token (https://vercel.com/account/tokens). La CLI también lo acepta como variable de entorno:

```powershell
$env:VERCEL_TOKEN = "tu-token"
```

Luego:

```powershell
vercel link          # Vincula el repo y guarda .vercel/project.json (ignorado por Git)
vercel env pull      # Baja las variables a .env.local (ignorado por Git)
vercel deploy        # O `vercel --prod` para producción
```

`config/settings.py` carga `.env.local` antes que `.env`, así que las variables bajadas desde Vercel tienen prioridad en local.

### Variables a configurar en el proyecto de Vercel

Además del token (que es sólo para la CLI), cargá en **Project Settings → Environment Variables**: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL` (Supabase), `SUPABASE_URL`, `SUPABASE_KEY` (service_role), buckets, `ADMIN_EMAIL`, `DEFAULT_FROM_EMAIL`, `RESEND_API_KEY` y los datos de negocio (`WHATSAPP_NUMBER`, `BANK_*`, `BUSINESS_ADDRESS`).

No definas `EMAIL_BACKEND`: el código elige Resend cuando hay `RESEND_API_KEY` y consola cuando no la hay. `ALLOW_LOCAL_STORAGE_FALLBACK` debe quedar en `False` (o sin definir, porque `DEBUG=False`). Usá la cadena **Transaction pooler** de Supabase (`puerto 6543`) en `DATABASE_URL`; el pooler es compatible con funciones serverless. Los buckets `product-images`, `payment-receipts` y `custom-designs` deben existir y ser públicos. Después de publicar, aplicá las migraciones con `vercel env pull && python manage.py migrate`.

---

## Estructura

```text
BASE/
├── admin_panel/        # login, dashboard y check_storage
├── cart/               # carrito en BD + API JSON + servicios
├── config/             # settings, urls, backend de Resend, validadores
├── orders/             # Order, OrderItem, checkout, correos y seguimiento
├── products/           # Category, Product, ProductImage, personalizador
├── refvisual/          # fuente visual única (no editar)
├── static/             # css y js reconstruidos
├── templates/          # base, storefront, products, cart, orders, admin_panel
├── tests/              # 28 pruebas smoke/integración
├── .env.example
├── requirements.txt
└── vercel.json           # configuración de la función Python

```

## Seguridad

- `.env`, `.env.local`, `.vercel/`, `.venv/`, `db.sqlite3`, `media/` y `staticfiles/` están en `.gitignore`.
- Nunca compartas `.env` ni lo pegues en un chat.
- Si alguna clave llegó a un commit anterior, rotala antes de publicar.

Para contexto completo de decisiones y cambios, ver [`CONTEXTO.md`](CONTEXTO.md).
