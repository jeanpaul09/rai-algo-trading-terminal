# What You Get - Real Data Dashboard

## ✅ Everything is Now Real

### 1. **Run Backtest Button** 
- **Location**: Strategy detail pages (click any strategy)
- **What it does**: Runs backtest with **real Binance market data**
- **How to use**: Click "Run Backtest" → Fill form → Start
- **Data source**: Binance public API (BTC/USDT, ETH/USDT, etc.)

### 2. **Liquidations Page** (NEW!)
- **Location**: Sidebar → "Liquidations"
- **What you see**:
  - Real-time liquidation data from Binance Futures
  - Long vs Short liquidations
  - Open interest for major pairs (BTC, ETH, SOL)
  - Updates every 5 seconds
- **URL**: http://localhost:3001/liquidations

### 3. **Real Market Data**
- **Dashboard**: Equity curves from real BTC/USDT data
- **Backtests**: Use real historical OHLCV data
- **Live Trading**: Real-time prices from exchanges
- **No mock data** - everything connects to real APIs

### 4. **Positions Viewer**
- **Location**: Liquidations page (right side)
- **What you see**:
  - All open positions from active traders
  - Long/Short breakdown
  - Real-time PnL
  - Updates every 2 seconds

## Quick Start

```bash
# Install Python deps (one time)
pip3 install requests fastapi uvicorn

# Start everything
./start_with_real_data.sh
```

Or manually:
```bash
# Terminal 1
python3 api_server.py

# Terminal 2
cd ui/web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## What to Try

1. **See Real Data**:
   - Go to http://localhost:3001
   - Dashboard shows real BTC/USDT equity curve

2. **Run a Backtest**:
   - Click "Strategies" → Click any strategy
   - Click **"Run Backtest"** button (top right)
   - Fill in: Market (BTC/USDT), dates, capital
   - Click "Start Backtest"
   - Watch job status update in real-time

3. **View Liquidations**:
   - Click "Liquidations" in sidebar
   - See real liquidation data updating live
   - See open interest for BTC, ETH, SOL

4. **Start Live Trading**:
   - Go to a strategy page
   - Click "Start Live Trading"
   - Choose symbol, exchange, mode
   - Monitor in "Live" page

## API Endpoints (All Real Data)

- `GET /api/market/data?symbol=BTC/USDT&days=30` - Real OHLCV
- `GET /api/liquidations?exchange=binance` - Real liquidations
- `GET /api/positions` - Real positions
- `POST /api/backtest/run` - Backtest with real data

## No More Mock Data!

Everything now uses:
- ✅ Binance public API for market data
- ✅ Binance Futures API for liquidations
- ✅ Real exchange connectors for live trading
- ✅ Real-time updates every 2-5 seconds


