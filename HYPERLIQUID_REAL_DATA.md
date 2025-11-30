# Hyperliquid Real Data Integration

## ✅ APIs Being Used

### 1. Hyperliquid Public API
**Base URL**: `https://api.hyperliquid.xyz`

**Endpoints**:
- **All Prices**: `POST /info` with `{"type": "allMids"}`
  - Returns: Dict of symbol -> price (e.g., `{"BTC": 90934.5, "ETH": 3040.75}`)
  - **NO API KEY NEEDED** ✅

- **Meta Data**: `POST /info` with `{"type": "meta"}`
  - Returns: Universe info, leverage, OI data
  - **NO API KEY NEEDED** ✅

- **Candle Data**: `POST /info` with `{"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1h", "n": 1000}}`
  - Returns: OHLCV candles for backtesting
  - **NO API KEY NEEDED** ✅

### 2. Binance Public API
**Base URL**: `https://api.binance.com/api/v3` and `https://fapi.binance.com/fapi/v1`

**Endpoints**:
- **OHLCV**: `GET /klines?symbol=BTCUSDT&interval=1h&limit=1000`
- **Liquidations**: `GET /forceOrders?symbol=BTCUSDT&limit=20`
- **NO API KEY NEEDED** ✅

## What Data is Available

### ✅ Available (Public, No Auth)
- **Market Prices**: All symbol prices from Hyperliquid
- **OHLCV Data**: Historical candles for backtesting
- **Open Interest**: From meta endpoint
- **Binance Liquidations**: Public liquidation events

### ⚠️ Requires Auth/WebSocket
- **Hyperliquid Liquidations**: Requires WebSocket feed or user-specific endpoints
- **User Positions**: Requires wallet authentication
- **User Orders**: Requires wallet authentication

## Current Implementation

The API server now:
1. ✅ Fetches real prices from Hyperliquid (`allMids`)
2. ✅ Fetches real OHLCV for backtesting
3. ✅ Fetches real liquidations from Binance Futures (as fallback)
4. ✅ Fetches real OI data from Hyperliquid meta

## Testing

### Test Hyperliquid API
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

### Test API Server
```bash
# Get liquidations (uses Binance for now)
curl "http://localhost:8000/api/liquidations?exchange=hyperliquid"

# Get market data
curl "http://localhost:8000/api/market/data?symbol=BTC&days=7&exchange=hyperliquid"
```

## Next Steps for Full Hyperliquid Integration

1. **WebSocket Integration**: Connect to `wss://api.hyperliquid.xyz/ws` for real-time liquidations
2. **User Auth**: Add wallet signing for user-specific data
3. **Liquidation Feed**: Subscribe to liquidation events via WebSocket

## Documentation

- Hyperliquid API: https://hyperliquid.gitbook.io/hyperliquid-docs/
- Binance API: https://binance-docs.github.io/apidocs/

All APIs are PUBLIC - no keys needed for market data! 🎉


