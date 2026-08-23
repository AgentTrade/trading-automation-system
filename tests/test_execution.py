import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from execution import ExecutionRequest, ExecutionService


class TestExecutionService(unittest.TestCase):

    def setUp(self):
        self.service = ExecutionService(
            account_name="test_account",
            equity=10_000,
        )

    def test_position_size_calculation(self):
        volume = self.service.calculate_position_size(
            risk_percent=1.0,
            stop_distance=100,
        )

        self.assertEqual(volume, 1.0)

    def test_execution_request(self):
        request = ExecutionRequest(
            symbol="TEST",
            side="BUY",
            risk_percent=0.5,
            stop_distance=50,
            target_distance=100,
        )

        result = self.service.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.account, "test_account")
        self.assertEqual(result.symbol, "TEST")
        self.assertEqual(result.side, "BUY")

    def test_invalid_side(self):
        request = ExecutionRequest(
            symbol="TEST",
            side="INVALID",
            risk_percent=0.5,
            stop_distance=50,
            target_distance=100,
        )

        with self.assertRaises(ValueError):
            self.service.execute(request)

    def test_zero_stop_distance(self):
        with self.assertRaises(ValueError):
            self.service.calculate_position_size(
                risk_percent=0.5,
                stop_distance=0,
            )


if __name__ == "__main__":
    unittest.main()
