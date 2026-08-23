"""
Signal routing layer for the trading automation system.

Portfolio version:
- no credentials
- no broker account data
- no proprietary trading rules
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TradingSignal:
    symbol: str
    side: str
    stop_distance: float
    target_distance: float


@dataclass
class AccountConfig:
    name: str
    risk_percent: float
    enabled: bool = True


class SignalRouter:
    """
    Routes validated trading signals to enabled execution accounts.

    The production system connects this layer to separate execution
    services responsible for broker-side order management.
    """

    def __init__(self, accounts: Dict[str, AccountConfig]):
        self.accounts = accounts

    def validate_signal(self, signal: TradingSignal) -> None:
        if signal.side not in {"BUY", "SELL"}:
            raise ValueError("Signal side must be BUY or SELL")

        if signal.stop_distance <= 0:
            raise ValueError("Stop distance must be positive")

        if signal.target_distance <= 0:
            raise ValueError("Target distance must be positive")

    def get_active_accounts(self) -> List[AccountConfig]:
        return [
            account
            for account in self.accounts.values()
            if account.enabled
        ]

    def route(self, signal: TradingSignal) -> List[dict]:
        self.validate_signal(signal)

        routed_orders = []

        for account in self.get_active_accounts():
            routed_orders.append(
                {
                    "account": account.name,
                    "symbol": signal.symbol,
                    "side": signal.side,
                    "risk_percent": account.risk_percent,
                    "stop_distance": signal.stop_distance,
                    "target_distance": signal.target_distance,
                }
            )

        return routed_orders
