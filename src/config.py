"""
Application configuration for the trading automation system.

Portfolio version:
- no credentials
- no real broker account identifiers
- no proprietary allocation rules
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AccountSettings:
    """Configuration for a single trading account."""

    name: str
    equity: float
    risk_percent: float
    enabled: bool = True


ACCOUNTS: List[AccountSettings] = [
    AccountSettings(
        name="account_primary",
        equity=10_000,
        risk_percent=0.5,
        enabled=True,
    ),
    AccountSettings(
        name="account_secondary",
        equity=25_000,
        risk_percent=0.25,
        enabled=True,
    ),
]
