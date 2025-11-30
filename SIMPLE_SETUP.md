# Simple Setup - NO API Keys, NO Server Needed

## ✅ What This Does

1. **Runs locally** - No cloud server needed
2. **No API keys** - Uses public APIs only
3. **Mock fallbacks** - Always works, even if APIs fail
4. **Zero setup** - Just run and go

## Quick Start

### Option 1: Use the script
```bash
./START_SIMPLE.sh
```

### Option 2: Manual
```bash
# Install deps (one time)
pip3 install requests fastapi uvicorn

# Start server
python3 api_server_simple.py
```

Then in another terminal:
```bash
cd ui/web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## How It Works

### Real Data (When Available)
- **Binance Public API**: Tries to fetch real BTC/USDT prices
- **Binance Futures**: Tries to fetch real liquidations
- **No API keys needed** - All public endpoints

### Mock Data (Fallback)
- If APIs fail or are unavailable, uses mock data
- Dashboard always works
- You'll see "data_source": "mock" in responses

## What You'll See

1. **Dashboard**: Equity curve (real if Binance works, mock otherwise)
2. **Liquidations**: Real liquidations if Binance Futures works, mock otherwise
3. **Market Data**: Real OHLCV if available, mock otherwise
4. **Everything works** - No errors, no broken UI

## Test It

```bash
# Test API server
curl http://localhost:8000/

# Test overview
curl http://localhost:8000/api/overview

# Test liquidations
curl http://localhost:8000/api/liquidations
```

## Troubleshooting

### "Connection refused"
- API server isn't running
- Run: `python3 api_server_simple.py`

### "No data showing"
- Check browser console for errors
- Check API server terminal for errors
- Mock data should still show

### APIs not working
- That's OK! Mock data will be used
- Dashboard still works
- You can develop/test without internet

## Important

- ✅ **No API keys needed**
- ✅ **No server setup needed**
- ✅ **Works offline** (uses mock data)
- ✅ **Always works** (never crashes)

This is the simplest possible setup! 🎉


