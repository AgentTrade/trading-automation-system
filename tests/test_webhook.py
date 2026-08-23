import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

import app as app_module
from app import app


class TestWebhook(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["configured_accounts"], 1)

    def test_valid_signal(self):
        response = self.client.post(
            "/webhook",
            json={
                "symbol": "EURUSD",
                "side": "buy",
                "stop_distance": 25,
                "target_distance": 50,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "processed")
        self.assertGreater(len(data["executions"]), 0)
        self.assertEqual(data["failed_executions"], 0)
        self.assertEqual(
            data["successful_executions"],
            len(data["executions"]),
        )

    def test_partial_execution_failure_is_isolated(self):
        failing_service = app_module.execution_services["account_primary"]

        with patch.object(
            failing_service,
            "execute",
            side_effect=RuntimeError("simulated broker failure"),
        ):
            response = self.client.post(
                "/webhook",
                json={
                    "symbol": "EURUSD",
                    "side": "buy",
                    "stop_distance": 25,
                    "target_distance": 50,
                },
            )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "processed")
        self.assertEqual(data["failed_executions"], 1)
        self.assertGreaterEqual(data["successful_executions"], 1)
        self.assertEqual(len(data["executions"]), 2)

        failed = [item for item in data["executions"] if not item["success"]]
        self.assertEqual(failed[0]["account"], "account_primary")
        self.assertIn("simulated broker failure", failed[0]["message"])

    def test_missing_field(self):
        response = self.client.post(
            "/webhook",
            json={
                "symbol": "EURUSD",
                "side": "buy",
                "stop_distance": 25,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_side(self):
        response = self.client.post(
            "/webhook",
            json={
                "symbol": "EURUSD",
                "side": "hold",
                "stop_distance": 25,
                "target_distance": 50,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_negative_stop_distance(self):
        response = self.client.post(
            "/webhook",
            json={
                "symbol": "EURUSD",
                "side": "sell",
                "stop_distance": -10,
                "target_distance": 50,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_json(self):
        response = self.client.post(
            "/webhook",
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
