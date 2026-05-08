"""Flask application factory."""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import config


def create_app(config_name="development"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # ── Ensure folders exist ──────────────────────────────────────────────────
    for folder in [
        app.config["UPLOAD_FOLDER"],
        app.config["HEATMAP_FOLDER"],
        app.config["REPORT_FOLDER"],
        os.path.join(app.root_path, "static", "models"),
        os.path.dirname(app.config["LOG_FILE"]),
        os.path.dirname(app.config["DATABASE"]),
    ]:
        os.makedirs(folder, exist_ok=True)

    # ── Logging ───────────────────────────────────────────────────────────────
    _setup_logging(app)

    # ── Database ──────────────────────────────────────────────────────────────
    from app.database.db import init_app as db_init_app
    db_init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.analyzer import analyzer_bp
    from app.routes.reports import reports_bp
    from app.routes.sessions import sessions_bp
    from app.routes.settings import settings_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(pages_bp)

    # ── Error Handlers ────────────────────────────────────────────────────────
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)

    app.logger.info("CNN Visual Debugger started successfully.")
    return app


def _setup_logging(app):
    level = getattr(logging, app.config.get("LOG_LEVEL", "DEBUG"))
    handler = RotatingFileHandler(
        app.config["LOG_FILE"], maxBytes=5_000_000, backupCount=5
    )
    handler.setLevel(level)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(level)
