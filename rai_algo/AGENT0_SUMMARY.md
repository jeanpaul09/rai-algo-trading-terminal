# AGENT 0 — DATA & BACKTEST INFRA Summary

## Overview

This document summarizes the reusable data and backtesting infrastructure built for the RAI-ALGO framework. This foundation supports trading across crypto, stocks, and prediction markets.

## Files Created

### Data Layer

#### Core Data Module (`data/`)
- **`data/__init__.py`**: Main exports for data layer
- **`data/schema.py`**: Common time series schema with validation
  - `TimeSeriesSchema`: Defines required columns (timestamp, open, high, low, close, volume)
  - Supports both Pandas and Polars DataFrames
  - Validation and normalization functions

- **`data/loaders.py`**: Data loading and caching utilities
  - `load_data()`: Unified data loading interface
  - `save_data()`: Save DataFrames to disk (Parquet/CSV)
  - `get_cached_data()`: Retrieve cached data
  - `clear_cache()`: Clear cache by source/symbol
  - Automatic caching to `.cache/rai_algo/data/`

#### Data Sources (`data/sources/`)
- **`data/sources/crypto/__init__.py`**: Crypto data via CCXT
  - `load_crypto_data()`: Load from exchanges (Binance, Coinbase, etc.)
  - Supports all CCXT-compatible exchanges
  - Configurable via environment variables

- **`data/sources/stocks/__init__.py`**: Stock data via yfinance
  - `load_stock_data()`: Load stock historical data
  - Supports multiple timeframes
  - No API keys required for basic usage

- **`data/sources/prediction_markets/__init__.py`**: Prediction market data
  - `load_prediction_market_data()`: Generic interface
  - Placeholder implementations for Polymarket and Kalshi
  - Ready for API integration

### Backtest Engine (`backtest/`)

- **`backtest/__init__.py`**: Main exports for backtest module

- **`backtest/core.py`**: Generic bar-based backtesting engine
  - `BacktestEngine`: Main engine class
  - `FeeModel`: Abstract fee model (with `FixedFeeModel` implementation)
  - `SlippageModel`: Abstract slippage model (with `FixedSlippageModel` implementation)
  - `Trade`: Trade record class
  - Supports strategy callbacks (function-based, not class-based)
  - Works with Pandas DataFrames

- **`backtest/metrics.py`**: Performance metrics
  - `evaluate_performance()`: Comprehensive metrics calculation
  - `calculate_sharpe_ratio()`: Annualized Sharpe ratio
  - `calculate_sortino_ratio()`: Annualized Sortino ratio
  - `calculate_max_drawdown()`: Maximum drawdown
  - `calculate_cagr()`: Compound Annual Growth Rate
  - `calculate_win_rate()`: Win rate and trade statistics
  - `calculate_profit_factor()`: Profit factor

- **`backtest/utils.py`**: Example usage and helpers
  - `simple_sma_crossover_strategy()`: Example SMA crossover strategy
  - `run_example_backtest()`: Complete example backtest workflow

### Configuration (`config/`)

- **`config/data_config_example.yaml`**: Example configuration file
  - Cache settings
  - Crypto exchange configurations
  - Stock provider settings
  - Prediction market platform settings
  - Backtest defaults

### Dependencies

Updated **`requirements.txt`** with:
- `pandas>=1.5.0`
- `polars>=0.19.0` (optional, for faster operations)
- `pyarrow>=10.0.0` (for Parquet support)
- `ccxt>=4.0.0` (crypto data)
- `yfinance>=0.2.0` (stock data)
- `pyyaml>=6.0` (config files)

## Usage Examples

### Example 1: Load Crypto Data

```python
from rai_algo.data.sources.crypto import load_crypto_data
from datetime import datetime, timedelta

# Load BTC/USDT data from Binance
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

df = load_crypto_data(
    symbol="BTC/USDT",
    timeframe="1h",
    start_date=start_date,
    end_date=end_date,
    exchange="binance",  # or use env var RAI_ALGO_CRYPTO_EXCHANGE
    use_polars=False,  # Set to True for Polars DataFrame
)

print(df.head())
```

### Example 2: Load Stock Data

```python
from rai_algo.data.sources.stocks import load_stock_data
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

df = load_stock_data(
    symbol="AAPL",
    timeframe="1d",
    start_date=start_date,
    end_date=end_date,
)

print(df.head())
```

### Example 3: Run a Simple Backtest

```python
from rai_algo.backtest.core import BacktestEngine, FixedFeeModel, FixedSlippageModel
from rai_algo.backtest.metrics import evaluate_performance, calculate_win_rate
import pandas as pd

# Load your data (or use mock data)
# df = load_crypto_data("BTC/USDT", "1h", ...)

# Define a simple strategy
def my_strategy(data_slice, current_index, state):
    """Simple momentum strategy."""
    if len(data_slice) < 20:
        return 0.0
    
    # Go long if price is above 20-period SMA
    sma_20 = data_slice['close'].rolling(20).mean().iloc[-1]
    current_price = data_slice['close'].iloc[-1]
    
    if current_price > sma_20:
        return 1.0  # Long
    else:
        return 0.0  # No position

# Initialize engine
engine = BacktestEngine(
    initial_capital=10000.0,
    fee_model=FixedFeeModel(0.001),  # 0.1% fee
    slippage_model=FixedSlippageModel(0.0005),  # 0.05% slippage
)

# Run backtest
results = engine.run(
    price_data=df,
    strategy=my_strategy,
    verbose=True,
)

# Calculate metrics
equity_curve = results['equity_curve']
metrics = evaluate_performance(equity_curve, periods_per_year=252)
trade_stats = calculate_win_rate(results['trades'])

print(f"Total Return: {metrics['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
print(f"Win Rate: {trade_stats['win_rate_pct']:.2f}%")
```

### Example 4: Using the Example Backtest Function

```python
from rai_algo.backtest.utils import run_example_backtest

# Run with mock data
results = run_example_backtest(
    data_source="mock",
    symbol="BTC/USDT",
    timeframe="1h",
    days=30,
    initial_capital=10000.0,
)

# Or with real crypto data (requires CCXT)
results = run_example_backtest(
    data_source="crypto",
    symbol="BTC/USDT",
    timeframe="1h",
    days=30,
    initial_capital=10000.0,
)
```

### Example 5: Custom Strategy with State

```python
def advanced_strategy(data_slice, current_index, state):
    """Strategy that maintains state across bars."""
    # Initialize state on first call
    if 'position' not in state:
        state['position'] = 0.0
        state['entry_price'] = None
    
    if len(data_slice) < 50:
        return state['position']
    
    # Calculate indicators
    sma_20 = data_slice['close'].rolling(20).mean().iloc[-1]
    sma_50 = data_slice['close'].rolling(50).mean().iloc[-1]
    current_price = data_slice['close'].iloc[-1]
    
    # Strategy logic
    if sma_20 > sma_50 and state['position'] <= 0:
        state['position'] = 1.0  # Go long
        state['entry_price'] = current_price
    elif sma_20 < sma_50 and state['position'] >= 0:
        state['position'] = -1.0  # Go short
        state['entry_price'] = current_price
    
    return state['position']
```

## Environment Variables

Set these environment variables for API access:

```bash
# Crypto exchanges
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
export RAI_ALGO_CRYPTO_EXCHANGE="binance"  # Default exchange

# Stock providers (yfinance doesn't need keys for basic usage)
# For Alpaca:
export ALPACA_API_KEY="your_key"
export ALPACA_API_SECRET="your_secret"

# Prediction markets
export POLYMARKET_API_KEY="your_key"
export KALSHI_API_KEY="your_key"
export KALSHI_API_SECRET="your_secret"
export RAI_ALGO_PREDICTION_PLATFORM="polymarket"  # Default platform

# Cache directory (optional)
export RAI_ALGO_CACHE_DIR=".cache/rai_algo/data"
```

## Design Principles

1. **Reusability**: All components are designed to be reused by other agents and strategies
2. **Flexibility**: Supports both Pandas and Polars DataFrames
3. **Extensibility**: Easy to add new data sources or fee/slippage models
4. **No Hard-coded Secrets**: All credentials come from environment variables
5. **Caching**: Automatic data caching to disk for performance
6. **Type Hints**: Full type hints for better IDE support
7. **Logging**: Uses Python logging module throughout

## Next Steps for Other Agents

Other agents can now:

1. **Load Data**: Use `load_data()` or source-specific functions
2. **Define Strategies**: Create strategy functions that take `(data_slice, current_index, state)`
3. **Run Backtests**: Use `BacktestEngine` with their strategies
4. **Evaluate Performance**: Use metrics functions to assess results
5. **Extend Data Sources**: Add new sources by implementing similar interfaces

## Notes

- Prediction market loaders are placeholders and need real API implementations
- The backtest engine uses Pandas internally but can accept Polars DataFrames (converted automatically)
- All file I/O uses Parquet format by default for efficiency
- The engine supports long and short positions via positive/negative position signals


