# Backtest Engine

Generic bar-based backtesting engine that works with any strategy function.

## Quick Start

```python
from rai_algo.backtest import BacktestEngine, FixedFeeModel, FixedSlippageModel
from rai_algo.backtest.metrics import evaluate_performance
import pandas as pd

# Define a strategy function
def my_strategy(data_slice, current_index, state):
    """Returns position signal: 1.0 (long), -1.0 (short), or 0.0 (no position)"""
    if len(data_slice) < 20:
        return 0.0
    
    sma = data_slice['close'].rolling(20).mean().iloc[-1]
    current = data_slice['close'].iloc[-1]
    
    return 1.0 if current > sma else 0.0

# Initialize engine
engine = BacktestEngine(
    initial_capital=10000.0,
    fee_model=FixedFeeModel(0.001),  # 0.1% fee
    slippage_model=FixedSlippageModel(0.0005),  # 0.05% slippage
)

# Run backtest
results = engine.run(
    price_data=df,  # DataFrame with OHLCV data
    strategy=my_strategy,
)

# Calculate metrics
metrics = evaluate_performance(results['equity_curve'])
print(f"Total Return: {metrics['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
```

## Strategy Function Signature

Your strategy function must have this signature:

```python
def strategy(data_slice: pd.DataFrame, current_index: int, state: dict) -> float:
    """
    Args:
        data_slice: DataFrame with all data up to current_index (inclusive)
        current_index: Current bar index
        state: Dictionary to persist state across bars
    
    Returns:
        Position signal:
        - 1.0 for long (100% of capital)
        - -1.0 for short (100% of capital)
        - 0.0 for no position
        - Or any value between -1.0 and 1.0 for partial positions
    """
    pass
```

## Performance Metrics

Available metrics:

- `evaluate_performance()`: Comprehensive metrics
- `calculate_sharpe_ratio()`: Annualized Sharpe ratio
- `calculate_sortino_ratio()`: Annualized Sortino ratio
- `calculate_max_drawdown()`: Maximum drawdown
- `calculate_cagr()`: Compound Annual Growth Rate
- `calculate_win_rate()`: Win rate and trade statistics
- `calculate_profit_factor()`: Profit factor

## Custom Fee and Slippage Models

```python
from rai_algo.backtest.core import FeeModel, SlippageModel

class MyFeeModel(FeeModel):
    def calculate_fee(self, price, size, is_entry):
        # Custom fee logic
        return price * size * 0.001

class MySlippageModel(SlippageModel):
    def apply_slippage(self, price, size, is_buy):
        # Custom slippage logic
        return price * 1.0005 if is_buy else price * 0.9995
```

## Example

See `backtest/utils.py` for a complete example with SMA crossover strategy.


