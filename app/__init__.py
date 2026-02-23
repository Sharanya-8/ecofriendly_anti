from flask import Flask
from .config import Config
from .database import init_app as db_init_app
from .routes.auth import auth_bp
from .routes.main import main_bp
from .routes.crops import crops_bp
from .routes.irrigation import irrigation_bp


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_class)

    # ── Database ───────────────────────────────────────────────────────────────
    db_init_app(app)

    # ── Blueprints ─────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(crops_bp)
    app.register_blueprint(irrigation_bp)

    return app
