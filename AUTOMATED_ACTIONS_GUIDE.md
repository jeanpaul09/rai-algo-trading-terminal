# Automated Actions - Complete Guide

## Overview

The dashboard now supports **automated actions** - you can run backtests, create strategies, start live trading, and optimize parameters directly from the UI!

## What's Built

### ✅ API Server (`api_server.py`)

Automated endpoints:
- `POST /api/backtest/run` - Run backtests
- `POST /api/strategies/create` - Create strategies from blueprints
- `POST /api/live/start` - Start live trading
- `POST /api/live/stop/{id}` - Stop live trading
- `POST /api/optimize/run` - Optimize parameters
- `GET /api/jobs/{id}` - Get job status
- `GET /api/jobs` - List all jobs

### ✅ Dashboard Components

1. **Run Backtest Dialog** - Configure and run backtests
2. **Job Status Panel** - Real-time job tracking
3. **Start Trading Dialog** - Deploy strategies for live trading

## How to Use

### Running a Backtest

1. Go to **Strategies** → Click on a strategy
2. Click **"Run Backtest"** button
3. Fill in the form:
   - Market (e.g., "BTC/USD")
   - Start/End dates
   - Initial capital
   - Data source
4. Click **"Start Backtest"**
5. Watch the job status in the **Recent Jobs** panel on the dashboard

### Starting Live Trading

1. Go to **Strategies** → Click on a strategy
2. Click **"Start Live Trading"** button
3. Configure:
   - Symbol (e.g., "BTC/USD")
   - Exchange
   - Mode (Dry Run or Live)
4. Click **"Start"**
5. Monitor in the **Live Trading Lab** page

### Creating Strategies

1. Use the blueprint translator API
2. POST to `/api/strategies/create` with a blueprint JSON
3. Strategy is automatically saved and available

## Job Tracking

All operations run as background jobs:
- **Queued** - Waiting to start
- **Running** - In progress (shows progress updates)
- **Completed** - Finished successfully
- **Failed** - Error occurred

Jobs are tracked in real-time and appear in the **Recent Jobs** panel on the main dashboard.

## Next Steps

1. ✅ Start API server: `python api_server.py`
2. ✅ Start dashboard: `cd ui/web && npm run dev`
3. ✅ Try running a backtest from the UI!
4. ✅ Start live trading (in dry-run mode first)

## Architecture

```
Dashboard UI → Next.js API Routes → Python FastAPI → RAI-ALGO Modules
     ↓                ↓                    ↓                ↓
  Forms/Buttons → /api/backtest/run → Background Tasks → BacktestEngine
```

All operations are asynchronous and tracked via job IDs.


