# Connecting Real Data to the Dashboard

This guide shows you how to connect the dashboard to actual RAI-ALGO data.

## Quick Start (3 Steps)

### Step 1: Copy the Implementation

```bash
cp api_server_implementation.py api_server.py
```

### Step 2: Save Backtest Results

When you run backtests, save them using the pattern in `BACKTEST_STORAGE_EXAMPLE.py`:

```python
from BACKTEST_STORAGE_EXAMPLE import save_backtest_result

# After running a backtest
save_backtest_result(
    result=backtest_result,
    strategy_name="ExampleMAStrategy",
    market="BTC/USD",
    start_date="2024-01-01",
    end_date="2024-03-31",
)
```

### Step 3: Start Both Servers

**Terminal 1 - API Server:**
```bash
python api_server.py
```

**Terminal 2 - Dashboard:**
```bash
cd ui/web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open http://localhost:3001 - you'll see real data!

## Overview

The dashboard expects data from these sources:
1. **Strategies** - From `rai_algo/strategies/` or blueprints
2. **Backtest Results** - From saved JSON files in `backtest_results/`
3. **Live Trading** - From `LiveTrader` instances

## Implementation Details

### 1. Strategy Discovery

The implementation automatically discovers:
- ✅ Python strategy classes in `rai_algo/strategies/`
- ✅ Blueprint JSON files in `blueprints/`

### 2. Backtest Result Storage

**Recommended**: Save to JSON files in `backtest_results/` directory.

See `BACKTEST_STORAGE_EXAMPLE.py` for the exact format.

### 3. Live Trader Integration

Register `LiveTrader` instances in the API server:

```python
# In your trading script
from api_server import _live_traders

trader = LiveTrader(config)
trader.start()
_live_traders["my_trader"] = trader
```

## Data Flow

```
RAI-ALGO Modules → API Server → Dashboard
     ↓                ↓            ↓
Strategies      →  /api/strategies → Strategy Lab
BacktestResults →  /api/experiments → Experiment Lab  
LiveTrader      →  /api/live/status → Live Lab
```

## Files Reference

- `api_server.py` - Current stub (mock data)
- `api_server_implementation.py` - **Complete implementation with real data**
- `BACKTEST_STORAGE_EXAMPLE.py` - How to save backtest results
- `CONNECTING_REAL_DATA.md` - This file

## Next Steps

1. ✅ Copy `api_server_implementation.py` to `api_server.py`
2. ✅ Run some backtests and save results
3. ✅ Start the API server
4. ✅ Start the dashboard with `NEXT_PUBLIC_API_URL` set
5. 🎉 View real data in the dashboard!

