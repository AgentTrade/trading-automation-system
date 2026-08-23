# Trading Automation System

An end-to-end trading automation project built to turn rule-based TradingView signals into automatically managed MetaTrader 5 trades.

The project started with a simple goal: remove manual execution and reduce the human factor from a rule-based trading process.

It evolved from a single TradingView → MT5 connection into a multi-account execution and risk-management system.

## What the system does

The system can:

- detect rule-based trade setups in TradingView
- generate and send webhook signals
- route signals through a Python/Flask execution layer
- execute trades automatically in MetaTrader 5
- calculate position size based on account-specific risk
- manage multiple trading accounts
- close positions automatically when exit conditions are reached
- move positions to break-even when predefined conditions are met
- log and track trade activity
- recover the execution environment after server or terminal restarts

## Architecture

```text
TradingView / Pine Script
          │
          │ Webhook
          ▼
   Python / Flask Router
          │
          ├──► Account / Execution Service
          │        └──► MetaTrader 5
          │
          ├──► Account / Execution Service
          │        └──► MetaTrader 5
          │
          └──► Additional accounts
```

The routing layer separates signal generation from execution and allows different accounts to use different risk and allocation rules.

## Problems solved during development

### Broker price differences

TradingView and MT5 brokers do not always produce identical prices.

Using fixed price distances from the TradingView feed therefore created execution inconsistencies.

I changed the execution logic so protective levels can be calculated using the broker's live price rather than assuming both feeds are identical.

### TradingView state vs. broker state

A trade could appear stopped on TradingView while remaining open at the broker because of differences between price feeds.

This created a state-management problem: the execution system could no longer assume that TradingView's displayed trade state was identical to the real broker position state.

The exit logic was redesigned so execution decisions could account for the actual broker-side position.

### Multi-account risk management

Different accounts required different risk rules.

Instead of duplicating the entire system for every account, I introduced a routing layer that can distribute signals according to account-specific allocation and risk logic.

### Operational recovery

A restart of the server or trading terminals should not require rebuilding the environment manually.

I therefore added a recovery workflow for restarting the required services and terminals and checking that the execution environment is running again.

## Development approach

I built the project iteratively:

Break the trading rules into smaller deterministic components.
Implement individual setup logic.
Connect TradingView alerts to Python.
Connect Python execution to MT5.
Test execution on small live accounts.
Compare TradingView signals with broker-side execution.
Inspect logs and investigate mismatches.
Modify the architecture as real execution problems appeared.
Extend the system to multiple accounts and different risk rules.

AI-assisted development was used as part of the implementation process. My role focused on system design, decomposition of requirements, defining execution logic, testing, debugging and validating behavior against real trading conditions.

## Signal flow

A trading signal moves through several independent layers:

```text
TradingView / Pine Script
        │
        │ webhook JSON
        ▼
Flask API
        │
        ▼
Signal Validation
        │
        ▼
Signal Router
        │
        ├── account-specific risk configuration
        ├── account allocation
        └── enabled / disabled account state
        │
        ▼
Execution Service
        │
        ├── position sizing
        ├── execution request
        └── broker-side order management
        │
        ▼
MetaTrader 5
```

Separating these responsibilities makes it possible to test signal processing, routing and execution logic independently.

## Webhook API

TradingView communicates with the execution system through a Flask webhook endpoint.

### Endpoint

```text
POST /webhook
```

Example payload:

```json
{
  "symbol": "EURUSD",
  "side": "buy",
  "stop_distance": 25.0,
  "target_distance": 50.0
}
```

Before a signal reaches the routing and execution layers, the incoming payload is validated and normalized.

The validation layer checks:

- required fields
- supported trade direction
- symbol formatting
- numeric stop distance
- numeric target distance
- positive stop and target values

Invalid signals are rejected before they can reach the execution layer.

The repository also includes a health endpoint:

```text
GET /health
```

This can be used to verify that the Flask service is running.

## Testing and CI

The portfolio version includes automated tests for the main application layers.

Tests cover areas such as:

- execution-service behavior
- webhook request handling
- signal validation
- invalid payload rejection
- signal normalization
- integration between the Flask endpoint and execution flow

Tests can be run locally with:

```bash
pytest
```

The repository also uses GitHub Actions for continuous integration.

On every push to the repository, the test workflow automatically installs the required dependencies and runs the test suite.

This provides an automated check that changes do not break previously tested behavior.

## Repository structure

```text
trading-automation-system/
│
├── src/
│   ├── app.py
│   ├── execution.py
│   ├── router.py
│   └── validation.py
│
├── tests/
│   └── automated test modules
│
├── .github/
│   └── workflows/
│       └── automated test workflow
│
├── requirements.txt
├── .gitignore
└── README.md
```

The public repository contains a simplified portfolio implementation of the architecture. Production credentials, broker configuration, proprietary strategy rules and sensitive account-specific logic are not included.

## Tech Stack
- Python
- Flask
- Pine Script
- TradingView
- MetaTrader 5
- Webhooks
- REST-style communication
- Rule-based automation
- Risk management
- Multi-account execution

## Project status

The system has progressed from a single-account prototype to an automated multi-account execution architecture and has been tested in live trading environments.

