"""
Flask webhook entry point for the trading automation system.

Portfolio version demonstrating the flow:

TradingView -> Webhook -> Validation -> Routing -> Execution
"""

from flask import Flask, jsonify, request

from router import AccountConfig, SignalRouter, TradingSignal
from execution import ExecutionRequest, ExecutionService


app = Flask(__name__)


ACCOUNTS = [
    AccountConfig(
        name="account_primary",
        risk_percent=0.5,
        enabled=True,
    ),
    AccountConfig(
        name="account_secondary",
        risk_percent=0.25,
        enabled=True,
    ),
]


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

    if not payload:
        return jsonify({"error": "Invalid JSON payload"}), 400

    required_fields = {
        "symbol",
        "side",
        "stop_distance",
        "target_distance",
    }

    missing = required_fields - payload.keys()

    if missing:
        return jsonify(
            {
                "error": "Missing required fields",
                "fields": sorted(missing),
            }
        ), 400

    try:
        signal = TradingSignal(
            symbol=str(payload["symbol"]),
            side=str(payload["side"]).upper(),
            stop_distance=float(payload["stop_distance"]),
            target_distance=float(payload["target_distance"]),
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

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
