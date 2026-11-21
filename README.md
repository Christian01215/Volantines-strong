# Volantines Strong

Tienda online de volantines + panel de administración, hecha en Django. El frontend es una réplica 1:1 de los archivos de diseño en `refvisual/` (`index.html` para la tienda y `admin.html` para el admin).

Incluye carrito, checkout con **comprobante de pago obligatorio**, aviso por correo al dueño vía **Resend** (con el comprobante adjunto) y un panel admin con login real de Django.

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
| `ADMIN_EMAIL` | Destinatario del aviso de compra. |
| `DEFAULT_FROM_EMAIL` | Remitente verificado en Resend. |
| `RESEND_API_KEY` | Key de Resend. Sin ella se usa el backend de consola. |
| `EMAIL_BACKEND` | Opcional. Fuerza un backend manualmente. |

> Si `DATABASE_URL` está vacía se usa `db.sqlite3`. Eso es ideal para probar en un PC sin IPv6 (algunas redes no pueden llegar al host de Supabase, que sólo resolvía AAAA).

---

## Supabase Storage

Creá estos dos buckets en **Supabase → Storage → Buckets**, marcados como **públicos**:

- `product-images` → fotos de productos y galería.
- `payment-receipts` → comprobantes de pago.

Para verificarlos:

```bash
python manage.py check_storage
```

Si tenés una `service_role` key podés intentar crearlos automáticamente:

```bash
python manage.py check_storage --create
```

> `products_product` y `products_productimage` son **tablas de base de datos**, no buckets. Los buckets se crean en el dashboard de Supabase.

Si la subida falla, el código guarda el archivo en `media/` y muestra un `messages.warning` con el error real. Las imágenes se guardan como ruta en `ImageField` **o** como URL en `image_url` (nunca una URL dentro del `ImageField`, para evitar `/media/media/...`).

---

## Correo con Resend

Con `RESEND_API_KEY` configurada, el checkout envía a `ADMIN_EMAIL`:

- Datos del cliente, RUT, teléfono y correo.
- Tipo de entrega, fecha, franja horaria, región/comuna/dirección.
- Detalle de productos y total.
- Medio de pago y datos de transferencia.
- Link al comprobante **y el archivo adjunto**.

Sin la key, el correo se imprime en la terminal (backend consola), útil para desarrollo.

En el plan gratuito de Resend, `onboarding@resend.dev` sólo envía al correo de la cuenta: verificá tu propio remitente en `DEFAULT_FROM_EMAIL`.

---

## Medio de pago

Por ahora el único medio habilitado es **Transferencia bancaria**:

```text
Banco: Banco Estado · Cuenta Vista
Titular: Volantines Strong
RUT: 12.345.678-9
N° de cuenta: 12345678901
Asunto: indica el número de pedido que recibirás al confirmar
```

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
| `/cart/` | Carrito. |
| `/orders/checkout/` | Checkout con comprobante. |
| `/admin-panel/login/` | Login del panel propio. |
| `/admin-panel/dashboard/` | Catálogo, stock y ventas. |
| `/admin/` | Admin nativo de Django. |
| `/orders/admin/` | Lista administrativa de pedidos. |

---

## Comandos útiles

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py check_storage
for f in static/js/*.js; do node --check "$f"; done
```

Migraciones incluidas:

- `orders/0002_*` → métodos de pago, entrega y comprobante.
- `products/0003_*` → descripción y galería de imágenes.
- `products/0004_*` → `image_url` e `ImageField` opcional en galería.

---

## Flujo de prueba

1. Levantá el server con `runserver`.
2. Agregá un producto al carrito desde `/`.
3. En checkout completá datos y **adjuntá un comprobante**.
4. Registrá el pedido: debe aparecer un código `VC########`.
5. Revisá el correo en `ADMIN_EMAIL` (o la consola si no configuraste Resend).
6. Entrá a `/admin-panel/dashboard/` → sección `03 / VENTAS`: el pedido debe estar con link al comprobante.
7. Probá cambio de estado, notificación, exportar Excel, editar/eliminar producto y logout.

---

## Estructura

```text
BASE/
├── admin_panel/        # login, dashboard y check_storage
├── cart/               # carrito en sesión
├── config/             # settings, urls, backend de Resend
├── orders/             # Order, OrderItem, checkout y servicios de correo
├── products/           # Category, Product, ProductImage
├── refvisual/          # fuente visual única (no editar)
├── static/             # css y js reconstruidos
├── templates/          # base, storefront y admin_panel
├── .env.example
└── requirements.txt
```

## Seguridad

- `.env`, `.venv/`, `db.sqlite3`, `media/` y `staticfiles/` están en `.gitignore`.
- Nunca compartas `.env` ni lo pegues en un chat.
- Si alguna clave llegó a un commit anterior, rotala antes de publicar.

Para contexto completo de decisiones y cambios, ver [`CONTEXTO.md`](CONTEXTO.md).
