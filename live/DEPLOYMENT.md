# Live Trading Bot Deployment Guide

This guide explains how to deploy and run live trading bots using the RAI-ALGO framework.

## Overview

The live trading system consists of:
- **Exchange Connectors**: Interface with trading exchanges (Binance, etc.)
- **Strategies**: Trading logic (MA crossover, etc.)
- **Risk Manager**: Position limits, daily loss limits, auto-kill switch
- **Live Trader**: Main bot that orchestrates everything

## Quick Start

### 1. Install Dependencies

```bash
pip install requests hmac hashlib
```

### 2. Set Environment Variables

Create a `.env` file or export variables:

```bash
# Exchange Credentials (REQUIRED)
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_api_secret_here"
export BINANCE_TESTNET="true"  # Use testnet for testing

# Trading Configuration
export TRADING_SYMBOL="BTC/USDT"
export DRY_RUN="true"  # Set to "false" for live trading
export ENABLE_AUTO_TRADING="true"

# Strategy Parameters
export FAST_MA_PERIOD="10"
export SLOW_MA_PERIOD="30"
export STOP_LOSS="0.02"  # 2%
export TAKE_PROFIT="0.05"  # 5%

# Risk Management
export MAX_DAILY_LOSS="0.05"  # 5% max daily loss
export MAX_POSITION_SIZE="0.10"  # 10% per position
export MAX_TOTAL_EXPOSURE="0.50"  # 50% total exposure
export MAX_DRAWDOWN="0.15"  # 15% max drawdown
export MAX_ORDERS_PER_DAY="100"
export MAX_ORDERS_PER_HOUR="20"

# Bot Configuration
export DATA_INTERVAL="1.0"  # Seconds between data fetches
export HEARTBEAT_INTERVAL="30.0"  # Seconds between heartbeat checks
```

### 3. Run the Bot

```bash
# Make executable
chmod +x live/example_strategy_bot.py

# Run in dry-run mode first (recommended)
DRY_RUN=true python live/example_strategy_bot.py

# Run live (after testing)
DRY_RUN=false python live/example_strategy_bot.py
```

## Environment Variables Reference

### Exchange Credentials

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BINANCE_API_KEY` | Yes | Binance API key | `abc123...` |
| `BINANCE_API_SECRET` | Yes | Binance API secret | `xyz789...` |
| `BINANCE_TESTNET` | No | Use testnet (true/false) | `true` |

### Trading Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TRADING_SYMBOL` | No | `BTC/USDT` | Trading pair symbol |
| `DRY_RUN` | No | `false` | Enable dry-run mode (no real orders) |
| `ENABLE_AUTO_TRADING` | No | `true` | Enable automatic order execution |

### Strategy Parameters

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FAST_MA_PERIOD` | No | `10` | Fast moving average period |
| `SLOW_MA_PERIOD` | No | `30` | Slow moving average period |
| `STOP_LOSS` | No | `0.02` | Stop loss percentage (2%) |
| `TAKE_PROFIT` | No | `0.05` | Take profit percentage (5%) |

### Risk Management

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAX_DAILY_LOSS` | No | `0.05` | Max daily loss (5% of account) |
| `MAX_POSITION_SIZE` | No | `0.10` | Max position size (10% of account) |
| `MAX_TOTAL_EXPOSURE` | No | `0.50` | Max total exposure (50% of account) |
| `MAX_DRAWDOWN` | No | `0.15` | Max drawdown (15%) |
| `MAX_ORDERS_PER_DAY` | No | `100` | Max orders per day |
| `MAX_ORDERS_PER_HOUR` | No | `20` | Max orders per hour |

### Bot Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATA_INTERVAL` | No | `1.0` | Seconds between market data fetches |
| `HEARTBEAT_INTERVAL` | No | `30.0` | Seconds between heartbeat checks |

## Creating Your Own Strategy Bot

### Step 1: Create Your Strategy

```python
# rai_algo/strategies/my_strategy.py
from rai_algo.base import BaseStrategy
from rai_algo.types import MarketData, Signal, SignalType

class MyStrategy(BaseStrategy):
    def generate_signal(self, market_data, history, current_position):
        # Your trading logic here
        return Signal(
            signal_type=SignalType.BUY,
            symbol=market_data.symbol,
            timestamp=datetime.now(),
        )
```

### Step 2: Create Bot File

```python
# live/my_strategy_bot.py
from rai_algo.live_trader import LiveTrader, TraderConfig
from rai_algo.strategies.my_strategy import MyStrategy
from rai_algo.exchanges.binance import BinanceExchange

def main():
    strategy = MyStrategy(parameters={...})
    exchange = BinanceExchange()
    config = TraderConfig(
        symbol="BTC/USDT",
        strategy=strategy,
        exchange=exchange,
        ...
    )
    trader = LiveTrader(config=config)
    trader.start()
    # ... keep running
```

### Step 3: Run Your Bot

```bash
python live/my_strategy_bot.py
```

## Safety Features

### 1. Max Daily Loss
- Automatically stops trading if daily loss exceeds limit
- Default: 5% of starting balance

### 2. Max Position Size
- Limits individual position size
- Default: 10% of account per position

### 3. Auto-Kill Switch
- Automatically kills trading if:
  - Daily loss limit exceeded
  - Max drawdown exceeded
  - Balance below minimum
- Requires manual reset to resume

### 4. Heartbeat Monitoring
- Monitors bot health
- Logs status every heartbeat interval
- Alerts if heartbeat is stale

### 5. Order Rate Limiting
- Limits orders per day and per hour
- Prevents excessive trading

## Monitoring

### Logs
- Logs are written to: `trader_{strategy_name}_{date}.log`
- Console output shows real-time status

### Status Check
The bot logs status every heartbeat interval:
```
💓 Heartbeat: {
    "symbol": "BTC/USDT",
    "balance": 10000.0,
    "positions": 1,
    "trades": 5,
    "daily_pnl": 150.0
}
```

### Risk Manager Status
Check risk manager status:
```python
status = trader.get_status()
print(status["risk_manager"])
```

## Best Practices

### 1. Start with Testnet
- Always test on testnet first
- Use `BINANCE_TESTNET=true`

### 2. Use Dry-Run Mode
- Test strategies in dry-run before going live
- Set `DRY_RUN=true`

### 3. Conservative Risk Limits
- Start with small position sizes
- Use tight stop losses
- Monitor closely

### 4. Gradual Deployment
- Start with small capital
- Increase gradually as confidence grows
- Monitor performance

### 5. Regular Monitoring
- Check logs regularly
- Monitor risk manager status
- Review daily performance

## Troubleshooting

### Bot Not Starting
- Check API credentials are correct
- Verify exchange health check passes
- Check logs for errors

### Orders Not Executing
- Check `ENABLE_AUTO_TRADING` is true
- Verify not in dry-run mode (if you want real orders)
- Check risk manager hasn't killed trading
- Verify sufficient balance

### Risk Manager Killed Trading
- Check kill reason in logs
- Review risk limits
- Manually reset kill switch if needed:
  ```python
  trader.risk_manager.reset_kill_switch()
  ```

### Exchange Connection Issues
- Check network connectivity
- Verify API keys are valid
- Check exchange status page
- Review API rate limits

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=RAI-ALGO Trading Bot
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/path/to/agent-builder
EnvironmentFile=/path/to/.env
ExecStart=/usr/bin/python3 /path/to/live/example_strategy_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "live/example_strategy_bot.py"]
```

Build and run:
```bash
docker build -t trading-bot .
docker run -d --env-file .env trading-bot
```

## Security Notes

⚠️ **IMPORTANT**: Never hard-code API keys or secrets in code!

- Use environment variables
- Use secret management services (AWS Secrets Manager, etc.)
- Restrict API key permissions (read-only if possible)
- Use IP whitelisting on exchange
- Enable 2FA on exchange account
- Regularly rotate API keys

## Support

For issues or questions:
1. Check logs: `trader_{strategy_name}_{date}.log`
2. Review risk manager status
3. Check exchange API status
4. Verify configuration


