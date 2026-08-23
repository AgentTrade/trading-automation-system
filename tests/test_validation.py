import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from validation import validate_signal_payload


class TestSignalValidation(unittest.TestCase):

    def test_valid_payload(self):
        payload = {
            "symbol": "EURUSD",
            "side": "BUY",
            "stop_distance": 25,
            "target_distance": 50,
        }

        result = validate_signal_payload(payload)

        self.assertEqual(result["symbol"], "EURUSD")
        self.assertEqual(result["side"], "BUY")
        self.assertEqual(result["stop_distance"], 25.0)
        self.assertEqual(result["target_distance"], 50.0)

    def test_side_is_normalized(self):
        payload = {
            "symbol": "EURUSD",
            "side": "sell",
            "stop_distance": 20,
            "target_distance": 40,
        }

        result = validate_signal_payload(payload)

        self.assertEqual(result["side"], "SELL")

    def test_invalid_side(self):
        payload = {
            "symbol": "EURUSD",
            "side": "HOLD",
            "stop_distance": 20,
            "target_distance": 40,
        }

        with self.assertRaises(ValueError):
            validate_signal_payload(payload)

    def test_negative_stop_distance(self):
        payload = {
            "symbol": "EURUSD",
            "side": "BUY",
            "stop_distance": -10,
            "target_distance": 40,
        }

        with self.assertRaises(ValueError):
            validate_signal_payload(payload)

    def test_missing_symbol(self):
        payload = {
            "side": "BUY",
            "stop_distance": 20,
            "target_distance": 40,
        }

        with self.assertRaises(ValueError):
            validate_signal_payload(payload)


if __name__ == "__main__":
    unittest.main()
