from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from backend.src.services.chatgpt_service import ChatGPTService


class ChatGPTServiceTests(unittest.TestCase):
    def test_missing_key_uses_deterministic_fallback(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            service = ChatGPTService()
            tasks = service.generate_task_suggestions({"project_context": "Example"})
        self.assertFalse(service.is_available())
        self.assertEqual(1, len(tasks))
        self.assertFalse(tasks[0]["is_ai_generated"])

    def test_configured_key_initializes_client_without_network_call(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-abcdefghijklmnopqrstuvwxyz123456"}, clear=False):
            service = ChatGPTService()
        self.assertTrue(service.is_available())

    def test_fallback_assignment_prefers_lower_workload(self):
        members = [
            {"username": "busy", "total_tasks_assigned": 10, "total_tasks_completed": 1, "performance_score": 90},
            {"username": "free", "total_tasks_assigned": 2, "total_tasks_completed": 2, "performance_score": 70},
        ]
        result = ChatGPTService._fallback_assignment(members)
        self.assertEqual("free", result["recommended_member"])

    def test_task_cleaning_bounds_untrusted_model_output(self):
        task = ChatGPTService._clean_task({
            "title": "x" * 300,
            "description": "y" * 4000,
            "priority": "impossible",
            "estimated_hours": 9999,
            "difficulty_rating": 50,
        })
        self.assertIsNotNone(task)
        assert task is not None
        self.assertEqual(160, len(task["title"]))
        self.assertEqual("medium", task["priority"])
        self.assertEqual(160, task["estimated_hours"])
        self.assertEqual(5, task["difficulty_rating"])


if __name__ == "__main__":
    unittest.main()
