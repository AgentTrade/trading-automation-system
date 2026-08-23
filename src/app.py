"""
Flask webhook entry point for the trading automation system.

Portfolio flow:

TradingView -> Webhook -> Validation -> Routing -> Execution
"""

from flask import Flask, jsonify, request

from execution import ExecutionRequest, ExecutionService
from router import AccountConfig, SignalRouter, TradingSignal
from validation import ValidationError, validate_signal_payload


app = Flask(__name__)


ACCOUNTS = {
    "account_primary": AccountConfig(
        name="account_primary",
        risk_percent=0.5,
        enabled=True,
    ),
    "account_secondary": AccountConfig(
        name="account_secondary",
        risk_percent=0.25,
        enabled=True,
    ),
}


router = SignalRouter(ACCOUNTS)


execution_services = {
    "account_primary": ExecutionService(
        account_name="account_primary",
        equity=10_000,
    ),
    "account_secondary": ExecutionService(
        account_name="account_secondary",
        equity=25_000,
    ),
}


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "trading-automation-system",
        }
    )


@app.post("/webhook")
def webhook():
    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({"error": "Invalid JSON payload"}), 400

    try:
        validated = validate_signal_payload(payload)

        signal = TradingSignal(
            symbol=validated["symbol"],
            side=validated["side"].upper(),
            stop_distance=validated["stop_distance"],
            target_distance=validated["target_distance"],
        )

        routes = router.route(signal)

        results = []

        for route in routes:
            service = execution_services[route["account"]]

            execution_request = ExecutionRequest(
                symbol=signal.symbol,
                side=signal.side,
                risk_percent=route["risk_percent"],
                stop_distance=signal.stop_distance,
                target_distance=signal.target_distance,
            )

            result = service.execute(execution_request)

            results.append(
                {
                    "account": result.account,
                    "symbol": result.symbol,
                    "side": result.side,
                    "volume": result.volume,
                    "success": result.success,
                    "message": result.message,
                }
            )

        return jsonify(
            {
                "status": "processed",
                "executions": results,
            }
        )

    except (ValidationError, ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
