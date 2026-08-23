"""
Flask webhook entry point for the trading automation system.

Portfolio flow:

TradingView -> Webhook -> Validation -> Routing -> Execution
"""

from flask import Flask, jsonify, request

from config import ACCOUNTS
from logging_config import configure_logging, get_logger
from router import AccountConfig, SignalRouter, TradingSignal
from validation import ValidationError, validate_signal_payload


configure_logging()
logger = get_logger(__name__)

app = Flask(__name__)


router_accounts = {
    account.name: AccountConfig(
        name=account.name,
        risk_percent=account.risk_percent,
        enabled=account.enabled,
    )
    for account in ACCOUNTS
}


router = SignalRouter(router_accounts)


execution_services = {
    account.name: ExecutionService(
        account_name=account.name,
        equity=account.equity,
    )
    for account in ACCOUNTS
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

    logger.info("WEBHOOK_RECEIVED")

    if payload is None:
        logger.warning("SIGNAL_REJECTED invalid_json")
        return jsonify({"error": "Invalid JSON payload"}), 400

    try:
        validated = validate_signal_payload(payload)

        logger.info(
            "SIGNAL_VALIDATED symbol=%s side=%s",
            validated["symbol"],
            validated["side"],
        )

        signal = TradingSignal(
            symbol=validated["symbol"],
            side=validated["side"].upper(),
            stop_distance=validated["stop_distance"],
            target_distance=validated["target_distance"],
        )

        routes = router.route(signal)

        logger.info(
            "SIGNAL_ROUTED symbol=%s targets=%s",
            signal.symbol,
            len(routes),
        )

        results = []

        for route in routes:
            account_name = route["account"]
            service = execution_services[account_name]

            execution_request = ExecutionRequest(
                symbol=signal.symbol,
                side=signal.side,
                risk_percent=route["risk_percent"],
                stop_distance=signal.stop_distance,
                target_distance=signal.target_distance,
            )

            try:
                result = service.execute(execution_request)

                logger.info(
                    "EXECUTION_SUCCESS account=%s symbol=%s side=%s",
                    result.account,
                    result.symbol,
                    result.side,
                )

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

            except (ValueError, RuntimeError) as error:
                logger.exception(
                    "EXECUTION_FAILED account=%s symbol=%s",
                    account_name,
                    signal.symbol,
                )

                results.append(
                    {
                        "account": account_name,
                        "symbol": signal.symbol,
                        "side": signal.side,
                        "success": False,
                        "message": str(error),
                    }
                )

        successful = sum(
            1 for item in results if item["success"]
        )

        failed = len(results) - successful

        return jsonify(
            {
                "status": "processed",
                "successful_executions": successful,
                "failed_executions": failed,
                "executions": results,
            }
        )

    except (ValidationError, ValueError, TypeError) as error:
        logger.warning(
            "SIGNAL_REJECTED reason=%s",
            error,
        )

        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
