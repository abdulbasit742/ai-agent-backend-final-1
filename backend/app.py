from __future__ import annotations

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

if os.environ.get("RENDER", "").lower() != "true":
    load_dotenv()

if __package__:
    from .src.config import load_settings
    from .src.models import db
else:
    from src.config import load_settings
    from src.models import db


def create_app(test_config: dict[str, object] | None = None, *, environ: dict[str, str] | None = None) -> Flask:
    """Create a validated Flask application instance."""

    settings = load_settings(environ)
    app = Flask(__name__)
    app.config.update(settings.to_flask_config())
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    JWTManager(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": list(app.config["CORS_ORIGINS"])}},
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    if __package__:
        from .src.routes import register_routes
        from .src.models import task as _task_model  # noqa: F401
        from .src.models import user as _user_model  # noqa: F401
    else:
        from src.routes import register_routes
        from src.models import task as _task_model  # noqa: F401
        from src.models import user as _user_model  # noqa: F401

    register_routes(app)

    @app.before_request
    def enforce_registration_policy():
        if request.method != "POST" or request.path != "/api/auth/register":
            return None

        if not app.config["ALLOW_PUBLIC_REGISTRATION"]:
            return jsonify({
                "status": "error",
                "message": "Public registration is disabled.",
            }), 403

        payload = request.get_json(silent=True) or {}
        if payload.get("role") not in (None, "team"):
            return jsonify({
                "status": "error",
                "message": "Public registration can only create team accounts.",
            }), 403

        password = payload.get("password")
        minimum = int(app.config["REGISTRATION_MIN_PASSWORD_LENGTH"])
        if not isinstance(password, str) or len(password) < minimum:
            return jsonify({
                "status": "error",
                "message": f"Password must contain at least {minimum} characters.",
            }), 400

        payload["role"] = "team"
        return None

    @app.after_request
    def secure_response(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

        if response.status_code >= 500 and response.is_json:
            payload = response.get_json(silent=True)
            if isinstance(payload, dict) and "details" in payload:
                payload.pop("details", None)
                response.set_data(app.json.dumps(payload))
                response.content_type = "application/json"
        return response

    @app.get("/api/health")
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            app.logger.exception("Database readiness check failed")
            return jsonify({
                "status": "degraded",
                "database": "unavailable",
            }), 503

        return jsonify({
            "status": "healthy",
            "database": "available",
            "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "telegram_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_USER_ID")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"status": "error", "message": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"status": "error", "message": "Method not allowed."}), 405

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    runtime = load_settings()
    app.run(host=runtime.host, port=runtime.port, debug=runtime.debug)
