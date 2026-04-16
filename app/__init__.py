"""
Kairos Stock — Application factory.
"""
import os
import sys

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

from app.models import db

mail = Mail()
login_manager = LoginManager()

# Module-level reference used by utils that need the app object
flask_app = None


def create_app():
    global flask_app

    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # ── Secret key — REQUIRED in production ───────────────────────────────
    secret_key = os.environ.get('SECRET_KEY', '')
    if not secret_key:
        if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RAILWAY_ENVIRONMENT'):
            sys.exit(
                "ERROR: La variable de entorno SECRET_KEY no está definida. "
                "Generá una con: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        import secrets as _s
        secret_key = _s.token_hex(32)
        print("[WARNING] SECRET_KEY no definida — usando clave temporal de desarrollo.")
    app.config['SECRET_KEY'] = secret_key

    # ── Database ───────────────────────────────────────────────────────────
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///kairos_stock.db')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Email ──────────────────────────────────────────────────────────────
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER',
                                                        os.environ.get('MAIL_USERNAME', ''))
    app.config['MAIL_ENABLED'] = bool(os.environ.get('MAIL_USERNAME', ''))

    # ── Extensions ─────────────────────────────────────────────────────────
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # ── Blueprints ─────────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.inventory import inventory_bp
    from app.routes.budgets import budgets_bp
    from app.routes.users import users_bp
    from app.routes.store import store_bp
    from app.routes.caja import caja_bp
    from app.routes.proveedores import proveedores_bp
    from app.routes.plazos import plazos_bp
    from app.routes.delivery import delivery_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(caja_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(plazos_bp)
    app.register_blueprint(delivery_bp)

    with app.app_context():
        _init_db(app)

    flask_app = app
    return app


def _init_db(app):
    try:
        from app.models import BudgetConfig, DeliveryApp  # noqa: ensure tables are registered
        db.create_all()
        from app.models import User, Category
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@fogo.local',
                role='admin',
                must_change_password=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Base de datos inicializada. Usuario admin debe cambiar contraseña.")

        # Categorías para hamburguesería
        for name, desc, color in [
            ('Hamburguesas',   'Nuestras hamburguesas',         '#c0392b'),
            ('Combos',         'Combos y menús completos',      '#e67e22'),
            ('Bebidas',        'Bebidas frías y calientes',     '#2980b9'),
            ('Acompañamientos','Papas, ensaladas y más',        '#27ae60'),
            ('Postres',        'Dulces para cerrar',            '#8e44ad'),
            ('Ingredientes',   'Insumos y materias primas',     '#7f8c8d'),
        ]:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, description=desc, color=color))
        db.session.commit()
    except Exception as e:
        app.logger.warning(f"[init_db] {e}")
