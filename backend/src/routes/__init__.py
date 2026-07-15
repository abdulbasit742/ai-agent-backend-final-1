"""Blueprint registration for the AI Agent backend."""

from __future__ import annotations

from flask import Flask


def register_routes(app: Flask) -> None:
    """Register every API blueprint exactly once."""

    from .auth import auth_bp
    from .chat import chat_bp
    from .tasks import tasks_bp
    from .telegram import telegram_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(telegram_bp, url_prefix="/api/telegram")
