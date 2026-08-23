import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from router import AccountConfig, SignalRouter, TradingSignal


class TestSignalRouter(unittest.TestCase):

    def setUp(self):
        self.router = SignalRouter(
            {
                "active": AccountConfig(
                    name="active",
                    risk_percent=0.5,
                    enabled=True,
                ),
                "disabled": AccountConfig(
                    name="disabled",
                    risk_percent=0.25,
                    enabled=False,
                ),
            }
        )

    def test_routes_only_to_enabled_accounts(self):
        signal = TradingSignal(
            symbol="EURUSD",
            side="BUY",
            stop_distance=25,
            target_distance=50,
        )

        routes = self.router.route(signal)

        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["account"], "active")
        self.assertEqual(routes[0]["risk_percent"], 0.5)

    def test_rejects_invalid_side(self):
        signal = TradingSignal(
            symbol="EURUSD",
            side="HOLD",
            stop_distance=25,
            target_distance=50,
        )

        with self.assertRaises(ValueError):
            self.router.route(signal)

    def test_rejects_non_positive_target(self):
        signal = TradingSignal(
            symbol="EURUSD",
            side="SELL",
            stop_distance=25,
            target_distance=0,
        )

        with self.assertRaises(ValueError):
            self.router.route(signal)


if __name__ == "__main__":
    unittest.main()
