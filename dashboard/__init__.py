from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask
from dashboard.router import dashboard_bp
from dashboard.loping import money, number, percent


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.register_blueprint(dashboard_bp)

    app.jinja_env.filters["money"] = money
    app.jinja_env.filters["number"] = number
    app.jinja_env.filters["percent"] = percent

    configure_logging(app)
    return app


def configure_logging(app: Flask) -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    handler = RotatingFileHandler(
        log_dir / "dashboard.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",)
    
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
