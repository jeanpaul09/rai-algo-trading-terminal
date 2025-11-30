# Verify Real Data is Working

## Quick Test

```bash
# 1. Check API server is running
curl http://localhost:8000/

# 2. Check overview endpoint (should show "real")
curl "http://localhost:8000/api/overview" | jq '.data_source, .btc_price'

# 3. Check market data endpoint (should show "real")
curl "http://localhost:8000/api/market/data?symbol=BTC/USDT&days=7" | jq '.data_source'
```

## Expected Output

### Overview:
```json
"real"
91129.13381234003
```

### Market Data:
```json
"real"
```

## In Dashboard

1. **Header Bar** should show:
   - BTC/USD: $91,129.13 (real price)
   - Data Source: REAL ✅ (green text)

2. **Equity Curve** should show real BTC price movements

3. **All Charts** should use real data

## If Still Shows MOCK

1. **Hard Refresh Browser**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

2. **Check Browser Console** (F12):
   - Look for "✅ Fetched from /api/overview: real"
   - If you see errors, API server might not be running

3. **Restart API Server**:
   ```bash
   pkill -f api_server_simple.py
   python3 api_server_simple.py
   ```

4. **Check Environment Variable**:
   - Make sure `NEXT_PUBLIC_API_URL=http://localhost:8000` is set
   - Or dashboard will default to `http://localhost:8000`

## API Server Logs

Check if API server is getting real data:
```bash
tail -f /tmp/api_server.log
```

You should see:
```
✅ Got REAL CoinGecko data: 91 data points, BTC: $91,129.13
```

If you see "⚠️ Using mock data fallback", CoinGecko API might be rate-limited. Wait a minute and try again.

## Current Status

✅ API server is returning REAL data
✅ Dashboard is configured to display it
✅ Market data endpoint uses real data

**Refresh your browser to see REAL data!** 🎉
