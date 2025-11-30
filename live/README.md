# Live Trading Bots

This directory contains live trading bot implementations using the RAI-ALGO framework.

## Structure

```
live/
├── example_strategy_bot.py    # Example bot using MA crossover strategy
├── DEPLOYMENT.md               # Deployment guide and instructions
└── README.md                   # This file
```

## Quick Start

1. **Set environment variables** (see `DEPLOYMENT.md`)
2. **Run the example bot**:
   ```bash
   python live/example_strategy_bot.py
   ```

## Creating Your Own Bot

See `DEPLOYMENT.md` for detailed instructions on creating custom strategy bots.

## Safety Features

All bots include:
- ✅ Max daily loss protection
- ✅ Position size limits
- ✅ Auto-kill switch
- ✅ Heartbeat monitoring
- ✅ Order rate limiting
- ✅ Comprehensive logging

## Environment Variables

See `DEPLOYMENT.md` for complete list of required environment variables.

**Minimum required:**
- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`
- `BINANCE_TESTNET=true` (for testing)

## Logs

Logs are written to: `trader_{strategy_name}_{date}.log`

Example: `trader_ExampleMAStrategy_20240115.log`


