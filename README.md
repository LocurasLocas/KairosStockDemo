# Fogo Hamburguesería — Sistema de Gestión

## Qué incluye

- 🔥 Branding Fogo (tema oscuro rojo/fuego)
- 🍔 Menú con foto por producto
- 💰 Precios con descuentos y etiquetas de promo (2x1, combo, etc.)
- 🛵 Módulo Apps de Delivery (Rappi, PedidosYa, etc.)
- 📦 Inventario de insumos y stock
- 🧾 Caja / punto de venta
- 👥 Usuarios y control de acceso
- 🏪 Tienda online pública

## Categorías preconfiguradas
Hamburguesas, Combos, Bebidas, Acompañamientos, Postres, Ingredientes

## Cambios vs versión anterior
- Quitado: Presupuestos, Importar/Exportar Excel de la barra lateral
- Agregado: Foto por producto (URL), Promo/Descuento por producto
- Agregado: Módulo Apps de Delivery
- Branding: tema oscuro Fogo con colores rojo y naranja/fuego

## Deploy Railway

```bash
git init && git add . && git commit -m "Fogo inicial"
git remote add origin https://github.com/TU_USUARIO/fogo.git
git push -u origin main
```

### Variables obligatorias en Railway
| Variable | Valor |
|---|---|
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |

### Primer login
- Usuario: `admin`
- Contraseña: `admin123`
- El sistema pedirá cambiar la contraseña al ingresar.
