"""
Broker-side execution layer for the trading automation system.

Portfolio version:
- no credentials
- no broker account data
- no proprietary trading rules
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionRequest:
    symbol: str
    side: str
    risk_percent: float
    stop_distance: float
    target_distance: float


@dataclass
class ExecutionResult:
    success: bool
    account: str
    symbol: str
    side: str
    volume: float
    message: str


class ExecutionService:
    """
    Converts a validated trading signal into a broker-side execution request.

    The production implementation connects this layer to MetaTrader 5.
    This portfolio version demonstrates the execution and risk-management
    architecture without exposing broker credentials or proprietary logic.
    """

    def __init__(self, account_name: str, equity: float):
        self.account_name = account_name
        self.equity = equity

    def calculate_position_size(
        self,
        risk_percent: float,
        stop_distance: float,
        value_per_point: float = 1.0,
    ) -> float:
        if risk_percent <= 0:
            raise ValueError("risk_percent must be greater than zero")

        if stop_distance <= 0:
            raise ValueError("stop_distance must be greater than zero")

        risk_amount = self.equity * (risk_percent / 100)

        volume = risk_amount / (
            stop_distance * value_per_point
        )

        return round(volume, 2)

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        side = request.side.upper()

        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        volume = self.calculate_position_size(
            risk_percent=request.risk_percent,
            stop_distance=request.stop_distance,
        )

        return ExecutionResult(
            success=True,
            account=self.account_name,
            symbol=request.symbol,
            side=side,
            volume=volume,
            message=(
                "Portfolio simulation: execution request validated."
            ),
        )

    def close_position(
        self,
        symbol: str,
        reason: Optional[str] = None,
    ) -> dict:
        return {
            "account": self.account_name,
            "symbol": symbol,
            "action": "CLOSE",
            "reason": reason or "exit condition reached",
        }

    def move_to_break_even(
        self,
        symbol: str,
    ) -> dict:
        return {
            "account": self.account_name,
            "symbol": symbol,
            "action": "MOVE_TO_BREAK_EVEN",
        }
