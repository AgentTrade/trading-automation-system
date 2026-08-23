"""
Validation layer for incoming TradingView webhook payloads.

Portfolio version:
- no credentials
- no broker account data
- no proprietary trading rules
"""

from typing import Any, Dict


REQUIRED_FIELDS = {
    "symbol",
    "side",
    "stop_distance",
    "target_distance",
}


class ValidationError(ValueError):
    """Raised when an incoming trading signal is invalid."""


def validate_signal_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize an incoming TradingView webhook payload.

    Expected example:
    {
        "symbol": "EURUSD",
        "side": "buy",
        "stop_distance": 25.0,
        "target_distance": 50.0
    }
    """

    if not isinstance(payload, dict):
        raise ValidationError("Payload must be a JSON object.")

    missing = REQUIRED_FIELDS - payload.keys()

    if missing:
        raise ValidationError(
            f"Missing required fields: {', '.join(sorted(missing))}"
        )

    symbol = str(payload["symbol"]).strip().upper()
    side = str(payload["side"]).strip().lower()

    if not symbol:
        raise ValidationError("Symbol cannot be empty.")

    if side not in {"buy", "sell"}:
        raise ValidationError("Side must be either 'buy' or 'sell'.")

    try:
        stop_distance = float(payload["stop_distance"])
        target_distance = float(payload["target_distance"])
    except (TypeError, ValueError):
        raise ValidationError(
            "Stop and target distances must be numeric."
        )

    if stop_distance <= 0:
        raise ValidationError("Stop distance must be greater than zero.")

    if target_distance <= 0:
        raise ValidationError("Target distance must be greater than zero.")

    return {
        "symbol": symbol,
        "side": side,
        "stop_distance": stop_distance,
        "target_distance": target_distance,
    }
