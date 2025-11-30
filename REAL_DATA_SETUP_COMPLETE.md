# Real Data Setup - Complete Guide

## ✅ YES - Real APIs Work on Localhost!

The API server runs on localhost and fetches **REAL data** from Binance public APIs. No API keys needed for market data and liquidations.

## Quick Start (2 Steps)

### Step 1: Start API Server (REAL DATA)

```bash
# Install dependencies (one time)
pip3 install requests fastapi uvicorn

# Start API server
python3 api_server.py
```

**OR use the script:**
```bash
./START_REAL_API.sh
```

You should see:
```
🚀 Starting RAI-ALGO API Server with Real Market Data...
🐍 Starting API server on port 8000...
```

### Step 2: Start Dashboard

```bash
cd ui/web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## What's Real

### ✅ Real Market Data
- **Source**: Binance Public API (`https://api.binance.com/api/v3/klines`)
- **No API key needed** - Public endpoint
- **Real OHLCV data** for BTC/USDT, ETH/USDT, etc.
- Used for backtests and equity curves

### ✅ Real Liquidations Data
- **Source**: Binance Futures API (`https://fapi.binance.com/fapi/v1/forceOrders`)
- **No API key needed** - Public endpoint
- **Real liquidation events** from Binance Futures
- Updates every 5 seconds

### ✅ Real Open Interest
- **Source**: Binance Futures API (`https://fapi.binance.com/fapi/v1/openInterest`)
- **Real OI data** for BTC, ETH, SOL
- Shows actual market positions

## Verify It's Working

### Test API Server
```bash
# Test market data
curl "http://localhost:8000/api/market/data?symbol=BTC/USDT&days=7"

# Test liquidations
curl "http://localhost:8000/api/liquidations?exchange=binance"

# Test overview
curl "http://localhost:8000/api/overview"
```

### Or use the test script:
```bash
python3 test_api.py
```

## Troubleshooting

### "Failed to fetch" Error

**Problem**: API server isn't running or not accessible

**Solution**:
1. Check API server is running:
   ```bash
   curl http://localhost:8000/
   ```
   Should return: `{"message": "RAI-ALGO API Server", ...}`

2. If not running, start it:
   ```bash
   python3 api_server.py
   ```

3. Check for errors in API server console

### No Data Showing

**Problem**: API calls failing silently

**Solution**:
1. Open browser console (F12)
2. Check Network tab for failed requests
3. Check API server console for errors
4. Verify Binance API is accessible:
   ```bash
   curl "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
   ```

### CORS Errors

**Problem**: Browser blocking requests

**Solution**: API server has CORS enabled for `localhost:3001`. If you see CORS errors, check:
- API server is running
- Dashboard URL is `http://localhost:3001`
- `NEXT_PUBLIC_API_URL` is set correctly

## What You'll See

1. **Dashboard**: Real BTC/USDT equity curve (last 90 days from Binance)
2. **Liquidations Page**: Real liquidation events from Binance Futures
3. **Run Backtest**: Uses real historical data from Binance
4. **All data is REAL** - No mocks, no fake data

## API Endpoints (All Real Data)

- `GET /api/market/data?symbol=BTC/USDT&days=30` → Real Binance OHLCV
- `GET /api/liquidations?exchange=binance` → Real Binance Futures liquidations
- `GET /api/overview` → Real equity curves from market data
- `POST /api/backtest/run` → Runs with real historical data

## Important Notes

- ✅ **No API keys needed** for market data (public endpoints)
- ✅ **Real data** from Binance (not mocked)
- ✅ **Works on localhost** - API server proxies to Binance
- ✅ **Updates in real-time** - Liquidations refresh every 5 seconds

Everything is REAL! 🎉


