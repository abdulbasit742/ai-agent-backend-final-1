from __future__ import annotations

import unittest

from backend.src.config import ConfigurationError, load_settings


BASE = {
    "APP_ENV": "testing",
    "JWT_SECRET_KEY": "test-jwt-secret-that-is-longer-than-thirty-two-characters",
    "SECRET_KEY": "test-flask-secret-that-is-longer-than-thirty-two-characters",
    "CORS_ORIGINS": "http://localhost:5173",
}


class ConfigTests(unittest.TestCase):
    def test_secure_settings_load(self):
        settings = load_settings(BASE)
        self.assertEqual(("http://localhost:5173",), settings.cors_origins)
        self.assertFalse(settings.allow_public_registration)
        self.assertFalse(settings.debug)

    def test_missing_jwt_secret_fails_closed(self):
        env = dict(BASE)
        env.pop("JWT_SECRET_KEY")
        with self.assertRaises(ConfigurationError):
            load_settings(env)

    def test_wildcard_cors_is_rejected(self):
        env = dict(BASE, CORS_ORIGINS="*")
        with self.assertRaises(ConfigurationError):
            load_settings(env)

    def test_production_requires_https_cors(self):
        env = dict(BASE, APP_ENV="production")
        with self.assertRaises(ConfigurationError):
            load_settings(env)

    def test_production_rejects_placeholder_secret(self):
        env = dict(
            BASE,
            APP_ENV="production",
            CORS_ORIGINS="https://app.example.com",
            JWT_SECRET_KEY="your-secret-key-change-me-12345678901234567890",
        )
        with self.assertRaises(ConfigurationError):
            load_settings(env)

    def test_registration_password_floor_cannot_be_weakened(self):
        env = dict(BASE, REGISTRATION_MIN_PASSWORD_LENGTH="8")
        with self.assertRaises(ConfigurationError):
            load_settings(env)


if __name__ == "__main__":
    unittest.main()
