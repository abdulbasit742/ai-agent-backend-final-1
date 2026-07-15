from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch


TEST_ENV = {
    "APP_ENV": "testing",
    "JWT_SECRET_KEY": "test-jwt-secret-that-is-longer-than-thirty-two-characters",
    "SECRET_KEY": "test-flask-secret-that-is-longer-than-thirty-two-characters",
    "CORS_ORIGINS": "http://localhost:5173",
    "ALLOW_PUBLIC_REGISTRATION": "false",
    "OPENAI_API_KEY": "",
    "TELEGRAM_BOT_TOKEN": "",
    "TELEGRAM_USER_ID": "",
}


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        database_url = f"sqlite:///{cls.tempdir.name}/test.db"
        cls.env_patch = patch.dict(os.environ, {**TEST_ENV, "DATABASE_URL": database_url}, clear=False)
        cls.env_patch.start()
        from backend.app import create_app

        cls.app = create_app({"TESTING": True}, environ={**TEST_ENV, "DATABASE_URL": database_url})
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.env_patch.stop()
        cls.tempdir.cleanup()

    def test_health_reports_database_readiness_without_secrets(self):
        response = self.client.get("/api/health")
        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual("healthy", payload["status"])
        self.assertNotIn("JWT_SECRET_KEY", response.get_data(as_text=True))

    def test_all_blueprints_are_registered(self):
        rules = {rule.rule for rule in self.app.url_map.iter_rules()}
        self.assertIn("/api/auth/login", rules)
        self.assertIn("/api/tasks", rules)
        self.assertIn("/api/chat/generate-tasks", rules)
        self.assertIn("/api/telegram/status", rules)

    def test_public_registration_is_disabled_by_default(self):
        response = self.client.post(
            "/api/auth/register",
            json={"username": "new-user", "email": "new@example.com", "password": "long-enough-password"},
        )
        self.assertEqual(403, response.status_code)

    def test_security_headers_are_present(self):
        response = self.client.get("/api/health")
        self.assertEqual("nosniff", response.headers["X-Content-Type-Options"])
        self.assertEqual("DENY", response.headers["X-Frame-Options"])


if __name__ == "__main__":
    unittest.main()
