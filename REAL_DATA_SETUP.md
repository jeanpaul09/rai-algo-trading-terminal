# Real Data Setup - Quick Start

## What's Built

✅ **Real Market Data** - Fetches from Binance public API
✅ **Liquidations Viewer** - Shows long/short liquidations in real-time
✅ **Positions Viewer** - Shows all open positions from active traders
✅ **Run Backtest Button** - Visible on strategy pages, uses real data

## Setup (2 Steps)

### 1. Install Python Dependencies

```bash
pip3 install requests fastapi uvicorn
```

### 2. Start Servers

**Terminal 1 - API Server:**
```bash
python3 api_server.py
```

**Terminal 2 - Dashboard:**
```bash
cd ui/web
npm run dev
```

## What You'll See

1. **Dashboard** (`http://localhost:3001`)
   - Real equity curves from Binance BTC/USDT data
   - Job status tracking
   - Real-time updates

2. **Strategies Page** → Click any strategy
   - **"Run Backtest"** button (top right)
   - **"Start Live Trading"** button
   - Uses real market data from Binance

3. **Liquidations Page** (new!)
   - Real-time liquidation data
   - Long/Short breakdown
   - Open interest data
   - Updates every 5 seconds

4. **Live Trading Page**
   - Real positions from active traders
   - Real-time PnL
   - Updates every 2 seconds

## API Endpoints (Real Data)

- `GET /api/market/data?symbol=BTC/USDT&days=30` - Real OHLCV data
- `GET /api/liquidations?exchange=binance` - Real liquidation data
- `GET /api/positions` - Real positions from traders
- `POST /api/backtest/run` - Runs backtest with real data

## Testing

1. Go to http://localhost:3001
2. Click "Strategies" → Click any strategy
3. You'll see **"Run Backtest"** and **"Start Live Trading"** buttons
4. Click "Liquidations" in sidebar to see liquidation data
5. Run a backtest - it uses real Binance data!

## Notes

- Market data fetches from Binance public API (no API key needed)
- Liquidations data from Binance Futures API
- All data updates in real-time
- No mock data - everything is real!


