# API Sources - REAL Data Endpoints

## ✅ All APIs are PUBLIC - No API Keys Needed!

### 1. Hyperliquid API
**Base URL**: `https://api.hyperliquid.xyz`

**Endpoints Used**:
- **Market Data**: `POST /info` with `{"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1h", "n": 1000}}`
- **Liquidations**: `POST /info` with `{"type": "liquidations", "n": 100}`
- **Open Interest**: `POST /info` with `{"type": "meta"}` (includes OI data)
- **Positions**: `POST /info` with `{"type": "allMids"}` (public prices)
- **All Mids**: `POST /info` with `{"type": "allMids"}` (all symbol prices)

**Documentation**: https://hyperliquid.gitbook.io/hyperliquid-docs/

### 2. Binance Public API
**Base URL**: `https://api.binance.com/api/v3`

**Endpoints Used**:
- **Market Data (OHLCV)**: `GET /klines?symbol=BTCUSDT&interval=1h&startTime=...&limit=1000`
- **24hr Ticker**: `GET /ticker/24hr?symbol=BTCUSDT`

**Documentation**: https://binance-docs.github.io/apidocs/spot/en/

### 3. Binance Futures Public API
**Base URL**: `https://fapi.binance.com/fapi/v1`

**Endpoints Used**:
- **Liquidations**: `GET /forceOrders?symbol=BTCUSDT&limit=20`
- **Open Interest**: `GET /openInterest?symbol=BTCUSDT`

**Documentation**: https://binance-docs.github.io/apidocs/futures/en/

## What Data is Real

### ✅ Hyperliquid (Primary for Perps)
- **Liquidations**: Real liquidation events from Hyperliquid perps
- **Open Interest**: Real OI data for all perpetual contracts
- **Market Data**: Real OHLCV data for backtesting
- **Positions**: Public price data (user positions require auth)

### ✅ Binance
- **Market Data**: Real OHLCV for spot markets
- **Liquidations**: Real liquidation events from Binance Futures
- **Prices**: Real-time ticker data

## API Server Endpoints

### Market Data
```
GET /api/market/data?symbol=BTC/USDT&days=30&exchange=hyperliquid
GET /api/market/data?symbol=BTC/USDT&days=30&exchange=binance
```

### Liquidations
```
GET /api/liquidations?exchange=hyperliquid
GET /api/liquidations?exchange=binance
```

### Positions
```
GET /api/positions?exchange=hyperliquid
```

### Overview
```
GET /api/overview
```

## Testing APIs Directly

### Test Hyperliquid
```bash
# Get all prices
curl -X POST "https://api.hyperliquid.xyz/info" \
  -H "Content-Type: application/json" \
  -d '{"type":"allMids"}'

# Get meta (includes OI)
curl -X POST "https://api.hyperliquid.xyz/info" \
  -H "Content-Type: application/json" \
  -d '{"type":"meta"}'
```

### Test Binance
```bash
# Get BTC price
curl "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"

# Get OHLCV
curl "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=10"
```

## Important Notes

1. **All APIs are PUBLIC** - No authentication needed
2. **Hyperliquid uses POST** - Not GET like Binance
3. **Rate Limits** - Both APIs have rate limits (usually generous for public data)
4. **Real Data** - Everything comes from live exchange APIs
5. **No Mock Data** - If API fails, you'll see an error (not fake data)

## Troubleshooting

### "Failed to fetch"
- API server not running: `python3 api_server.py`
- Network issue: Check internet connection
- API down: Check exchange status pages

### No Liquidations Showing
- May be no recent liquidations (check exchange directly)
- API endpoint may have changed (check exchange docs)
- Rate limit hit (wait and retry)

### Wrong Data Format
- Exchange API structure may have changed
- Check exchange API documentation
- Update parsing logic in `api_server.py`


