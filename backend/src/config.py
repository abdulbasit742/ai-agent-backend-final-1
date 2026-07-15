from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping

_TRUTHY = {"1", "true", "yes", "on"}
_PLACEHOLDER_MARKERS = (
    "change-me",
    "change_this",
    "please-change",
    "replace-me",
    "your-secret",
    "your-very-secret",
)


class ConfigurationError(RuntimeError):
    """Raised when security-sensitive application settings are invalid."""


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in _TRUTHY


def _as_int(value: str | None, default: int, *, minimum: int, maximum: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigurationError(f"Expected an integer, received {value!r}.") from exc
    if parsed < minimum or parsed > maximum:
        raise ConfigurationError(f"Integer setting must be between {minimum} and {maximum}.")
    return parsed


def _origins(value: str | None, *, production: bool) -> tuple[str, ...]:
    if value is None or not value.strip():
        if production:
            raise ConfigurationError("CORS_ORIGINS is required in production.")
        return ("http://localhost:5173", "http://127.0.0.1:5173")

    origins = tuple(part.strip().rstrip("/") for part in value.split(",") if part.strip())
    if not origins:
        raise ConfigurationError("CORS_ORIGINS must contain at least one origin.")
    if "*" in origins:
        raise ConfigurationError("Wildcard CORS origins are not allowed.")
    if production and any(not origin.startswith("https://") for origin in origins):
        raise ConfigurationError("Production CORS origins must use HTTPS.")
    return origins


def _secret(name: str, value: str | None, *, production: bool) -> str:
    candidate = (value or "").strip()
    if len(candidate) < 32:
        raise ConfigurationError(f"{name} must contain at least 32 characters.")
    lowered = candidate.lower()
    if production and any(marker in lowered for marker in _PLACEHOLDER_MARKERS):
        raise ConfigurationError(f"{name} still contains a placeholder value.")
    return candidate


@dataclass(frozen=True)
class Settings:
    environment: str
    secret_key: str
    jwt_secret_key: str
    database_url: str
    cors_origins: tuple[str, ...]
    jwt_access_token_expires: int
    allow_public_registration: bool
    registration_min_password_length: int
    max_content_length: int
    host: str
    port: int
    debug: bool

    @property
    def production(self) -> bool:
        return self.environment == "production"

    def to_flask_config(self) -> dict[str, object]:
        return {
            "APP_ENV": self.environment,
            "SECRET_KEY": self.secret_key,
            "JWT_SECRET_KEY": self.jwt_secret_key,
            "JWT_ACCESS_TOKEN_EXPIRES": self.jwt_access_token_expires,
            "SQLALCHEMY_DATABASE_URI": self.database_url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "CORS_ORIGINS": self.cors_origins,
            "ALLOW_PUBLIC_REGISTRATION": self.allow_public_registration,
            "REGISTRATION_MIN_PASSWORD_LENGTH": self.registration_min_password_length,
            "MAX_CONTENT_LENGTH": self.max_content_length,
        }


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    env = dict(os.environ if environ is None else environ)
    environment = env.get("APP_ENV", env.get("FLASK_ENV", "development")).strip().lower()
    production = environment == "production"

    jwt_secret = _secret("JWT_SECRET_KEY", env.get("JWT_SECRET_KEY"), production=production)
    flask_secret = _secret(
        "SECRET_KEY",
        env.get("SECRET_KEY") or jwt_secret,
        production=production,
    )
    database_url = (env.get("DATABASE_URL") or "sqlite:///ai_agent_system.db").strip()
    if not database_url:
        raise ConfigurationError("DATABASE_URL cannot be empty.")

    return Settings(
        environment=environment,
        secret_key=flask_secret,
        jwt_secret_key=jwt_secret,
        database_url=database_url,
        cors_origins=_origins(env.get("CORS_ORIGINS"), production=production),
        jwt_access_token_expires=_as_int(
            env.get("JWT_ACCESS_TOKEN_EXPIRES"),
            3600,
            minimum=300,
            maximum=86_400,
        ),
        allow_public_registration=_as_bool(env.get("ALLOW_PUBLIC_REGISTRATION"), False),
        registration_min_password_length=_as_int(
            env.get("REGISTRATION_MIN_PASSWORD_LENGTH"),
            12,
            minimum=12,
            maximum=128,
        ),
        max_content_length=_as_int(
            env.get("MAX_CONTENT_LENGTH"),
            1_048_576,
            minimum=16_384,
            maximum=10_485_760,
        ),
        host=env.get("HOST", "0.0.0.0").strip(),
        port=_as_int(env.get("PORT"), 5000, minimum=1, maximum=65_535),
        debug=_as_bool(env.get("FLASK_DEBUG"), False) and not production,
    )
