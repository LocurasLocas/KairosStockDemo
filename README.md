# Kairos Stock — Guía de Deploy en Railway

## Estructura del proyecto

```
kairos-stock/
├── app.py                      # Entry point (7 líneas)
├── app/
│   ├── __init__.py             # Application factory
│   ├── models.py               # Todos los modelos SQLAlchemy
│   ├── routes/
│   │   ├── auth.py             # Login, logout, cambio de contraseña
│   │   ├── main.py             # Dashboard y API de búsqueda
│   │   ├── inventory.py        # Productos, categorías, movimientos
│   │   ├── budgets.py          # Presupuestos y PDF
│   │   ├── users.py            # Usuarios, email config, staff
│   │   └── store.py            # Tienda pública y admin
│   └── utils/
│       ├── email.py            # Email y WhatsApp helpers
│       ├── pdf.py              # Generador de PDF (único, sin duplicación)
│       └── decorators.py       # admin_required, editor_required
├── templates/                  # Plantillas HTML
├── static/
│   └── kairos-logo.png         # Logo
├── requirements.txt
├── Procfile
└── .env.example
```

---

## Paso 1 — Subir a GitHub

```bash
git init
git add .
git commit -m "Kairos Stock — initial commit"
git remote add origin https://github.com/TU_USUARIO/kairos-stock.git
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

## Paso 4 — Variables de entorno obligatorias

En Railway → tu servicio → **Variables**:

| Variable | Valor |
|---|---|
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `MAIL_USERNAME` | tu_email@gmail.com *(opcional)* |
| `MAIL_PASSWORD` | App Password de Gmail *(opcional)* |
| `MAIL_DEFAULT_SENDER` | tu_email@gmail.com *(opcional)* |
| `WHATSAPP_PHONE` | +54911... *(opcional)* |
| `CALLMEBOT_APIKEY` | tu apikey *(opcional)* |

> ⚠️ **SECRET_KEY es obligatoria en producción.** Si no está definida, la app no arranca.

---

## Paso 5 — Primer login

- Usuario: `admin`
- Contraseña: `admin123`
- Al ingresar, el sistema pedirá que cambies la contraseña (mínimo 8 caracteres).

---

## Paso 6 — URL pública

Railway → **Settings** → **Networking** → **Generate Domain**.

---

## Deploy automático

Cada `git push` a `main` dispara un redeploy automático. 🚀
