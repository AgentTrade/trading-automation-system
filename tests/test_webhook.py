import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from app import app


class TestWebhook(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

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


if __name__ == "__main__":
    unittest.main()
