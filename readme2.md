# Volantines Strong — Guía completa (readme2.md)

> Documento único para que cualquier persona pueda clonar, configurar, desplegar y mantener la tienda **Volantines Strong** en otra PC o en Vercel. Resume todo lo avanzado hasta ahora: correo con Gmail SMTP, almacenamiento con Cloudinary, base de datos en Supabase y despliegue en Vercel.

---

## 1. ¿Qué es este proyecto?

Tienda online de volantines + panel de administración, hecha en **Django**. El frontend es una réplica 1:1 de los diseños en `refvisual/` (`index.html` para la tienda y `admin.html` para el admin).

Incluye:
- Carrito persistido en base de datos.
- Checkout con **comprobante de pago obligatorio**.
- Aviso por correo al dueño vía **Gmail SMTP** (con el comprobante adjunto).
- Confirmación automática al cliente.
- Notificación cuando el pedido está listo.
- Personalizador de carretes en Canvas.
- Consulta de estado por código.
- Reportes en el admin.
- Login real de Django.

---

## 2. Stack tecnológico

| Componente | Tecnología |
| --- | --- |
| Backend | Django 6.1.3 / Python 3.12+ |
| Base de datos | PostgreSQL de Supabase (fallback a SQLite local) |
| Almacenamiento de archivos | **Cloudinary** (imágenes, comprobantes, diseños) |
| Correo | **Gmail SMTP** (backend estándar de Django, sin SDK extra) |
| Frontend | Tailwind (CDN) + JS vanilla reconstruido desde `refvisual/` |
| Despliegue | Vercel (serverless) |

> Nota: antes se usaba Supabase Storage, pero se migró a Cloudinary para evitar problemas de RLS y límites. La base de datos sigue en Supabase.

---

## 3. Instalación local (paso a paso)

### 3.1 Clonar y preparar entorno

```bash
git clone https://github.com/Christian01215/Volantines-strong.git
cd Volantines-strong

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3.2 Crear el archivo `.env`

Crea un archivo `.env` en la raíz (nunca lo subas a Git). Mínimo necesario:

```env
SECRET_KEY=tu_clave_larga_y_aleatoria
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (vacía = SQLite local)
DATABASE_URL=

# Cloudinary (almacenamiento)
CLOUDINARY_URL=cloudinary://TU_API_KEY:TU_API_SECRET@wf6wixyl
ALLOW_LOCAL_STORAGE_FALLBACK=True

# Negocio
WHATSAPP_NUMBER=+56 9 1234 5678
BANK_NAME=Banco Estado
BANK_ACCOUNT_TYPE=Cuenta Vista
BANK_RUT=12.345.678-9
BANK_ACCOUNT=12345678
BUSINESS_ADDRESS=Calle Ejemplo 123, Santiago

# Correo (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_cuenta@gmail.com
EMAIL_HOST_PASSWORD=contraseña_de_aplicacion_16_chars
DEFAULT_FROM_EMAIL=Volantines Strong <tu_cuenta@gmail.com>
ADMIN_EMAIL=tu_cuenta@gmail.com
SEND_CUSTOMER_CONFIRMATION=True
```

### 3.3 Migraciones y superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

Si `SECRET_KEY` no está definida, Django falla al arrancar a propósito.

---

## 4. Variables de entorno (referencia completa)

| Variable | Uso |
| --- | --- |
| `SECRET_KEY` | Obligatoria. Clave larga y aleatoria de Django. |
| `DEBUG` | `False` por defecto. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,0.0.0.0,.vercel.app` por defecto. |
| `DATABASE_URL` | Cadena de Supabase Postgres. Vacía = SQLite local. |
| `CLOUDINARY_URL` | URL de Cloudinary: `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`. |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Alternativa a `CLOUDINARY_URL`. |
| `ALLOW_LOCAL_STORAGE_FALLBACK` | Permite guardar en `media/` si Cloudinary falla. En Vercel debe ser `False`. |
| `WHATSAPP_NUMBER` | Número usado en enlaces `wa.me`. |
| `BANK_NAME` / `BANK_ACCOUNT_TYPE` / `BANK_RUT` / `BANK_ACCOUNT` | Datos de transferencia. |
| `BUSINESS_ADDRESS` | Dirección de retiro. |
| `ADMIN_EMAIL` | Destinatario del aviso de compra. Por defecto `ctorresj@utem.cl`. |
| `DEFAULT_FROM_EMAIL` | Remitente. Debe coincidir con `EMAIL_HOST_USER`. |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` en producción. |
| `EMAIL_HOST` / `EMAIL_PORT` | `smtp.gmail.com` / `587`. |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | TLS `True`, SSL `False` para Gmail. |
| `EMAIL_HOST_USER` | Cuenta de Google que autentica el envío. |
| `EMAIL_HOST_PASSWORD` | Contraseña de aplicación de 16 caracteres (sin espacios). |
| `EMAIL_TIMEOUT` | Timeout SMTP (15 s por defecto). |
| `SEND_CUSTOMER_CONFIRMATION` | Envía confirmación al comprador. `True` por defecto. |

---

## 5. Cloudinary (almacenamiento de imágenes)

1. Crea una cuenta en https://cloudinary.com.
2. En el **Dashboard**, copia el **Cloud name** exacto (respetando mayúsculas/minúsculas).
3. Copia la **API Key** y **API Secret**.
4. Arma la URL:
   ```
   CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
   ```
5. Ponla en `.env` (local) y en Vercel (Production y Preview).

El código en `config/storage.py` usa `cloudinary.uploader.upload()` con `overwrite=False` (no sobrescribe). Si Cloudinary no está configurado y `ALLOW_LOCAL_STORAGE_FALLBACK=True`, guarda en `media/` local.

---

## 6. Gmail SMTP (correo)

1. Activa la verificación en dos pasos en tu cuenta de Google.
2. Ve a **Seguridad → Contraseñas de aplicaciones** y genera una contraseña de 16 caracteres.
3. Ponla en `EMAIL_HOST_PASSWORD` (sin espacios).
4. `EMAIL_HOST_USER` debe ser la cuenta de Google.
5. `DEFAULT_FROM_EMAIL` debe ser la misma cuenta o un alias verificado en Gmail → “Enviar como”.

### Probar el correo

```bash
python manage.py check_email --no-send   # solo conexión/autenticación
python manage.py check_email             # envía a ADMIN_EMAIL
python manage.py check_email --to otro@correo.cl
```

---

## 7. Base de datos (Supabase)

- Crea un proyecto en Supabase.
- Copia la cadena **Transaction pooler** (puerto 6543) en `DATABASE_URL`.
- Si `DATABASE_URL` está vacía, se usa SQLite local (ideal para desarrollo).

---

## 8. Despliegue en Vercel

### 8.1 Requisitos
- `vercel.json` ya configurado con `buildCommand` que ejecuta `migrate` y `collectstatic`.
- `config/wsgi.py` expone `application` y `app`.
- `STATIC_ROOT` configurado.

### 8.2 Variables en Vercel
Carga en **Project Settings → Environment Variables** (Production y Preview):
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `CLOUDINARY_URL`
- `ALLOW_LOCAL_STORAGE_FALLBACK=False`
- `ADMIN_EMAIL`, `DEFAULT_FROM_EMAIL`
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_TIMEOUT`
- Datos de negocio (`WHATSAPP_NUMBER`, `BANK_*`, `BUSINESS_ADDRESS`)

### 8.3 Deploy
```bash
# Vincular repo (primera vez)
vercel link

# Bajar variables a local
vercel env pull

# Deploy a producción
vercel --prod
```

O simplemente haz push a `main` y Vercel desplegará automáticamente.

### 8.4 Promover de Preview a Production
1. Vercel → Deployments → selecciona el deployment de Preview.
2. `...` → **Promote to Production**.

---

## 9. Rutas principales

| Ruta | Descripción |
| --- | --- |
| `/` | Tienda. |
| `/producto/<slug>/` | Detalle de producto. |
| `/personalizar/<slug>/` | Personalizador de carretes (Canvas). |
| `/cart/carrito/` | Carrito persistido en BD. |
| `/cart/api/` | API JSON del carrito. |
| `/orders/checkout/` | Checkout con comprobante. |
| `/orders/pedido/` | Consulta de estado por código `VC########`. |
| `/admin-panel/login/` | Login del panel propio. |
| `/admin-panel/dashboard/` | Catálogo, stock, ventas y reportes. |
| `/admin/` | Admin nativo de Django. |

---

## 10. Comandos útiles

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test tests
python manage.py check_email --no-send
python manage.py loaddata categories
```

---

## 11. Estructura del proyecto

```text
BASE/
├── admin_panel/        # login, dashboard, comandos
├── cart/               # carrito en BD + API JSON
├── config/             # settings, urls, storage (Cloudinary), validators
├── orders/             # Order, OrderItem, checkout, correos
├── products/           # Category, Product, ProductImage, personalizador
├── refvisual/          # fuente visual única (no editar)
├── static/             # css y js
├── templates/          # base, storefront, products, cart, orders, admin_panel
├── tests/              # pruebas smoke/integración
├── requirements.txt
└── vercel.json
```

---

## 12. Seguridad

- `.env`, `.env.local`, `.vercel/`, `.venv/`, `db.sqlite3`, `media/` y `staticfiles/` están en `.gitignore`.
- Nunca compartas `.env` ni lo pegues en un chat.
- Si alguna clave llegó a un commit anterior, rótala antes de publicar.
- La contraseña de aplicación de Gmail debe rotarse si se expuso.

---

## 13. Cómo se llegó aquí (historial de cambios)

1. **Fase 0 — Baseline**: 33 tests OK, `manage.py check` OK, backup de datos, verificación de límite de Vercel (4.5 MB).
2. **Migración de correo**: de Resend a Gmail SMTP. Se eliminó `config/email_backends.py`, se agregó `check_email`, `Reply-To` en correos. Commit `41de526`.
3. **Migración de storage**: de Supabase Storage a Cloudinary. Se reescribió `config/storage.py`, se actualizaron callers y tests. Commit `9ce19ec`.
4. **Fix de deploy**: se agregó `SECRET_KEY` a variables de Vercel, se hizo merge a `main` (commit `5046667`) y se promovió a Production.
5. **Resultado**: tienda operativa en Vercel con imágenes en Cloudinary y correos vía Gmail SMTP.

---

Para contexto detallado de decisiones, ver `CONTEXTO.md`.
Para instrucciones originales, ver `README.md`.
