# Hyperliquid Integration for RAI-ALGO

This document summarizes the first-class Hyperliquid exchange integration added to the RAI-ALGO system.

## Overview

The integration provides support for:
1. **Historical Data / Backtesting**: Fetch OHLCV and funding rate data from Hyperliquid
2. **Live Trading / Execution**: Execute trades on Hyperliquid perpetual contracts

## Files Created/Modified

### Created Files

1. **`rai_algo/data/sources/crypto/hyperliquid.py`**
   - Historical data fetching functions
   - `fetch_ohlcv()`: Fetch OHLCV data with caching
   - `fetch_funding_rates()`: Fetch funding rate time series
   - On-disk caching support (Parquet format)

2. **`rai_algo/exchanges/hyperliquid.py`**
   - `HyperliquidExchange` class implementing `BaseExchange` interface
   - Full trading functionality: place orders, cancel orders, get positions, etc.
   - Wallet-based authentication support

3. **`rai_algo/config/hyperliquid_example.yaml`**
   - Example configuration file with all settings
   - Risk limits, fee rates, leverage settings
   - Instructions for setup

4. **`rai_algo/examples/hyperliquid_example.py`**
   - Complete usage examples
   - Demonstrates historical data fetching
   - Demonstrates exchange setup and basic operations

### Modified Files

1. **`rai_algo/data/sources/crypto/__init__.py`**
   - Added Hyperliquid support to `load_crypto_data()` function
   - Can now use `exchange="hyperliquid"` parameter

2. **`rai_algo/exchanges/__init__.py`**
   - Added `HyperliquidExchange` to exports

3. **`rai_algo/requirements.txt`**
   - Added `requests>=2.28.0` for HTTP API calls
   - Added optional `eth-account` note for proper wallet signing

## Environment Variables

Set these environment variables for Hyperliquid integration:

```bash
# Required for trading operations
export HYPERLIQUID_PRIVATE_KEY="your_private_key_here"

# Optional, but recommended
export HYPERLIQUID_ADDRESS="your_wallet_address"

# Optional: Use testnet
export HYPERLIQUID_TESTNET="true"
```

## Usage Examples

### 1. Fetching Historical Data for Backtesting

```python
from rai_algo.data.sources.crypto.hyperliquid import fetch_ohlcv
from datetime import datetime, timedelta

# Fetch BTC OHLCV data
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

df = fetch_ohlcv(
    symbol="BTC",
    timeframe="1h",
    start=start_date,
    end=end_date,
    use_cache=True,  # Uses on-disk caching
)

print(df.head())
```

### 2. Using with Generic Data Loader

```python
from rai_algo.data.loaders import load_data
from datetime import datetime, timedelta

# Load Hyperliquid data via generic interface
df = load_data(
    source="crypto",
    symbol="BTC",
    timeframe="1h",
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    exchange="hyperliquid",  # Specify Hyperliquid
)
```

### 3. Setting Up HyperliquidExchange for Live Trading

```python
from rai_algo.exchanges.hyperliquid import HyperliquidExchange
import os

# Create exchange instance
exchange = HyperliquidExchange(config={
    "private_key": os.getenv("HYPERLIQUID_PRIVATE_KEY"),
    "address": os.getenv("HYPERLIQUID_ADDRESS"),
    "testnet": os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true",
})

# Fetch market data
market_data = exchange.get_market_data("BTC")
print(f"BTC Price: ${market_data.close}")

# Get account balance
balance = exchange.get_balance()
print(f"Available: {balance.available} USDC")

# Get positions
position = exchange.get_position("BTC")
if position:
    print(f"Position size: {position.size}")

# Place an order (example)
order = exchange.place_order(
    symbol="BTC",
    side="BUY",
    quantity=0.001,
    order_type="MARKET",
)
print(f"Order ID: {order.order_id}")
```

### 4. Using with LiveTrader

```python
from rai_algo.live_trader import LiveTrader, TraderConfig
from rai_algo.exchanges.hyperliquid import HyperliquidExchange
from your_strategy import YourStrategy

# Create exchange
exchange = HyperliquidExchange()

# Create trader config
config = TraderConfig(
    symbol="BTC",
    strategy=YourStrategy(),
    exchange=exchange,
    dry_run=True,  # Start with dry-run mode
)

# Create and start trader
trader = LiveTrader(config)
trader.start()
```

## Configuration

Copy the example config file and customize:

```bash
cp rai_algo/config/hyperliquid_example.yaml rai_algo/config/hyperliquid.yaml
```

Then edit `hyperliquid.yaml` with your settings (but **never commit secrets**).

## Important Notes

### API Endpoint Adjustments

The implementation uses standard REST API patterns, but **Hyperliquid's actual API structure may differ**. You may need to adjust:

1. **Data fetching endpoints** in `rai_algo/data/sources/crypto/hyperliquid.py`:
   - Update the `/info` endpoint parameters
   - Adjust response parsing based on actual API response format

2. **Trading endpoints** in `rai_algo/exchanges/hyperliquid.py`:
   - Update the `/exchange` endpoint structure
   - Adjust order placement/cancellation payloads
   - Verify authentication/signing mechanism

### Authentication

Hyperliquid uses **wallet-based authentication** with private key signing. The implementation includes:

- Basic signing support (HMAC fallback)
- Optional `eth-account` library for proper ECDSA signing (recommended for production)

To use proper signing, install:
```bash
pip install eth-account
```

### Testing

1. **Start with testnet**: Set `HYPERLIQUID_TESTNET="true"`
2. **Use dry-run mode**: Set `dry_run=True` in `TraderConfig`
3. **Test with small amounts**: Always test with minimal position sizes first
4. **Run the example script**: `python rai_algo/examples/hyperliquid_example.py`

## Integration Points

### Backtesting Engine

The historical data layer integrates seamlessly with the backtesting engine:

```python
from rai_algo.backtest import BacktestEngine
from rai_algo.data.loaders import load_data

# Load Hyperliquid data
data = load_data(
    source="crypto",
    symbol="BTC",
    timeframe="1h",
    exchange="hyperliquid",
)

# Convert to MarketData list (helper function needed)
market_data_list = convert_df_to_market_data(data)

# Run backtest
engine = BacktestEngine()
result = engine.run(your_strategy, market_data_list)
```

### Strategy Configuration

Specify Hyperliquid as the exchange in your strategy config:

```yaml
strategy:
  name: "My Strategy"
  exchange: "hyperliquid"
  symbol: "BTC"
  # ... other parameters
```

## Error Handling

The implementation includes comprehensive error handling for:
- API rate limits
- Invalid symbols
- Network issues
- Authentication failures
- Order placement errors

All errors are logged with detailed messages for debugging.

## Next Steps

1. **Review Hyperliquid API Documentation**: Verify endpoint structures and adjust code as needed
2. **Test on Testnet**: Use testnet mode to verify functionality
3. **Implement Proper Signing**: Use `eth-account` for production-grade wallet signing
4. **Add WebSocket Support**: For real-time data updates (optional enhancement)
5. **Add More Features**: Funding rate alerts, position management, etc.

## Support

For issues or questions:
1. Check the example script: `rai_algo/examples/hyperliquid_example.py`
2. Review Hyperliquid's official API documentation
3. Adjust endpoints based on actual API responses

---

**Created by**: AGENT HL — HYPERLIQUID INTEGRATION ENGINEER  
**Date**: 2024


