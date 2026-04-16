"""Delivery apps integration (Rappi, PedidosYa, etc.)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, DeliveryApp, utcnow
from app.utils.decorators import admin_required, editor_required

delivery_bp = Blueprint('delivery', __name__)

KNOWN_APPS = {
    'rappi': {
        'display_name': 'Rappi',
        'color': '#ff441f',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Rappi_logo.svg/320px-Rappi_logo.svg.png',
        'base_url': 'https://www.rappi.com.ar',
        'description': 'La app de delivery más usada en Argentina. Pedidos en minutos.',
    },
    'pedidosya': {
        'display_name': 'PedidosYa',
        'color': '#fa0050',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/PedidosYa_logo.svg/320px-PedidosYa_logo.svg.png',
        'base_url': 'https://www.pedidosya.com.ar',
        'description': 'Una de las apps de delivery más grandes de Latinoamérica.',
    },
    'mercadopedidos': {
        'display_name': 'Mercado Pedidos',
        'color': '#fff159',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/MercadoLibre_logo.svg/320px-MercadoLibre_logo.svg.png',
        'base_url': 'https://www.mercadolibre.com.ar',
        'description': 'Delivery integrado en el ecosistema Mercado Libre.',
    },
    'ifood': {
        'display_name': 'iFood',
        'color': '#ea1d2c',
        'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/IFood_logo.svg/320px-IFood_logo.svg.png',
        'base_url': 'https://www.ifood.com.br',
        'description': 'Presente en Brasil y expandiéndose en Latinoamérica.',
    },
    'otro': {
        'display_name': 'Otra App',
        'color': '#6366f1',
        'logo': '',
        'base_url': '',
        'description': 'Otra plataforma de delivery.',
    },
}


@delivery_bp.route('/delivery')
@login_required
def delivery_apps():
    apps = DeliveryApp.query.order_by(DeliveryApp.id).all()
    return render_template('delivery.html', apps=apps, known_apps=KNOWN_APPS)


@delivery_bp.route('/delivery/nueva', methods=['POST'])
@login_required
@editor_required
def new_delivery_app():
    name = request.form.get('name', '').strip().lower()
    meta = KNOWN_APPS.get(name, KNOWN_APPS['otro'])
    app_obj = DeliveryApp(
        name=name,
        display_name=request.form.get('display_name', meta['display_name']).strip(),
        store_url=request.form.get('store_url', '').strip(),
        commission_pct=float(request.form.get('commission_pct') or 0),
        logo_url=request.form.get('logo_url', meta.get('logo', '')).strip(),
        notes=request.form.get('notes', '').strip(),
        is_active=True,
    )
    db.session.add(app_obj)
    db.session.commit()
    flash(f'App {app_obj.display_name} agregada.', 'success')
    return redirect(url_for('delivery.delivery_apps'))


@delivery_bp.route('/delivery/<int:id>/editar', methods=['POST'])
@login_required
@editor_required
def edit_delivery_app(id):
    app_obj = DeliveryApp.query.get_or_404(id)
    app_obj.display_name = request.form.get('display_name', app_obj.display_name).strip()
    app_obj.store_url = request.form.get('store_url', '').strip()
    app_obj.commission_pct = float(request.form.get('commission_pct') or 0)
    app_obj.logo_url = request.form.get('logo_url', '').strip()
    app_obj.notes = request.form.get('notes', '').strip()
    app_obj.is_active = 'is_active' in request.form
    db.session.commit()
    flash('Actualizado.', 'success')
    return redirect(url_for('delivery.delivery_apps'))


@delivery_bp.route('/delivery/<int:id>/toggle', methods=['POST'])
@login_required
@editor_required
def toggle_delivery_app(id):
    app_obj = DeliveryApp.query.get_or_404(id)
    app_obj.is_active = not app_obj.is_active
    db.session.commit()
    return jsonify({'active': app_obj.is_active})


@delivery_bp.route('/delivery/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_delivery_app(id):
    app_obj = DeliveryApp.query.get_or_404(id)
    db.session.delete(app_obj)
    db.session.commit()
    flash('App eliminada.', 'success')
    return redirect(url_for('delivery.delivery_apps'))
