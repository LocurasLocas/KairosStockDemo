# Kairos Burgers — Guía de Deploy en Railway

## Estructura del proyecto

```
kairos-burgers/
├── app.py
├── app/
│   ├── __init__.py             # Application factory
│   ├── models.py               # Modelos SQLAlchemy
│   ├── routes/
│   │   ├── auth.py             # Login, logout
│   │   ├── main.py             # Dashboard
│   │   ├── inventory.py        # Productos (menú) con fotos y promos
│   │   ├── delivery.py         # Integración Rappi / PedidosYa
│   │   ├── users.py            # Usuarios y email config
│   │   └── webhooks.py         # Webhooks de pedidos externos
│   └── utils/
│       ├── email.py            # Notificaciones por email
│       ├── images.py           # Upload y resize de fotos de productos
│       └── delivery_api.py     # Clientes API Rappi y PedidosYa
├── templates/
│   ├── product_form.html       # Formulario con foto + promociones
│   ├── delivery_integrations.html
│   └── email_settings.html
├── static/
│   ├── uploads/                # Fotos de productos (ignoradas por git)
│   └── kairos-logo.png
├── requirements.txt
└── railway.json
```

---

## Paso 1 — Subir a GitHub

```bash
git init
git add .
git commit -m "Kairos Burgers — initial commit"
git remote add origin https://github.com/TU_USUARIO/kairos-burgers.git
git branch -M main
git push -u origin main
```

---

## Paso 2 — Crear proyecto en Railway

1. Entrá a [railway.app](https://railway.app) → logueate con GitHub.
2. **New Project** → **Deploy from GitHub repo** → seleccioná el repo.

---

## Paso 3 — Agregar PostgreSQL

**+ New** → **Database** → **PostgreSQL**.  
Railway agrega `DATABASE_URL` automáticamente.

---

## Paso 4 — Variables de entorno

En Railway → tu servicio → **Variables**:

| Variable | Descripción | Obligatoria |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Flask | ✅ |
| `UPLOAD_FOLDER` | Ruta de fotos (ej: `/app/static/uploads`) | ✅ |
| `MAX_IMAGE_SIZE_KB` | Tamaño máximo de imagen en KB (def: 2000) | — |
| `MAIL_USERNAME` | Email para notificaciones | — |
| `MAIL_PASSWORD` | App Password de Gmail | — |
| `MAIL_DEFAULT_SENDER` | Email remitente | — |
| `RAPPI_WEBHOOK_SECRET` | Secret para validar webhooks de Rappi | — |
| `PEDIDOSYA_WEBHOOK_SECRET` | Secret para validar webhooks de PedidosYa | — |

> ⚠️ `SECRET_KEY` es obligatoria. Generala con:  
> `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Paso 5 — Primer login

- Usuario: `admin`  
- Contraseña: `admin123`  
- El sistema pedirá cambio de contraseña en el primer acceso.

---

## Paso 6 — Configurar integraciones de delivery

### Rappi
1. Accedé al **Portal de Aliados Rappi** de tu país.
2. Ve a **Integraciones → API** y generá credenciales.
3. En Kairos Burgers → **Delivery** → completá Store ID y API Key.
4. Configurá la webhook URL en Rappi: `https://TU_APP.railway.app/webhooks/rappi/orders`

### PedidosYa
1. Accedé al **Panel de Socios PedidosYa**.
2. Ve a **Configuración → Integraciones** y creá una integración.
3. En Kairos Burgers → **Delivery** → completá Restaurant ID, Client ID y Client Secret.
4. Configurá la webhook URL: `https://TU_APP.railway.app/webhooks/pedidosya/orders`

---

## Paso 7 — Fotos de productos

- Formatos soportados: JPG, PNG, WEBP
- Tamaño recomendado: 800×600 px
- Las imágenes se almacenan en `UPLOAD_FOLDER` y se sirven desde `/static/uploads/`
- En Railway se recomienda usar un bucket S3/R2 para persistencia (ver `utils/images.py`)

---

## Menú lateral — secciones activas

| Sección | Ruta |
|---|---|
| Dashboard | `/` |
| Menú / Productos | `/productos` |
| Pedidos delivery | `/delivery` |
| Integraciones | `/delivery/configuracion` |
| Usuarios | `/usuarios` |
| Email | `/configuracion/email` |

> ❌ Importar/Exportar y Presupuestos fueron removidos de esta versión.

---

## Deploy automático

Cada `git push` a `main` dispara un redeploy automático. 🚀
