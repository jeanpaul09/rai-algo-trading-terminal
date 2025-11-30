# RAI-ALGO Framework

A clean, exchange-agnostic algorithmic trading framework for Python.

## Architecture Principles

1. **Exchange-Agnostic**: Strategies return signals, not direct trades
2. **Clean Separation**: No exchange-specific logic in strategy files
3. **Type Safety**: Full type hints throughout
4. **Risk Management**: Built-in position sizing and stop loss/take profit
5. **Extensible**: Easy to add new indicators and strategies

## Framework Structure

```
rai_algo/
├── __init__.py          # Framework exports
├── base.py              # BaseStrategy, Signal, Position, MarketData
├── types.py             # Type definitions
├── blueprint_translator.py  # JSON blueprint → Python code
└── README.md

strategies/
├── __init__.py
├── example_moving_average_cross.py  # Example strategy
└── backtest_example.py              # Backtest runner

blueprints/
└── *.json               # Strategy blueprint definitions
```

## Quick Start

### 1. Create a Strategy

```python
from rai_algo import BaseStrategy, MarketData, Signal, SignalType
from decimal import Decimal

class MyStrategy(BaseStrategy):
    def calculate_indicators(self, market_data):
        # Calculate your indicators
        return {"my_indicator": IndicatorResult(...)}
    
    def generate_signal(self, market_data, indicators, current_position):
        # Generate trading signals
        return Signal(
            signal_type=SignalType.BUY,
            timestamp=datetime.now(),
            symbol="BTC/USD",
            price=current_price,
            confidence=Decimal("0.8"),
            reason="Entry conditions met"
        )
```

### 2. Use from Blueprint

```python
from rai_algo.blueprint_translator import translate_blueprint

# Translate blueprint JSON to Python
translate_blueprint("blueprints/my_strategy.json", "strategies/my_strategy.py")

# Import and use
from strategies.my_strategy import MyStrategy

strategy = MyStrategy(
    initial_capital=Decimal("10000"),
    stop_loss_pct=Decimal("0.02"),
    take_profit_pct=Decimal("0.05")
)
```

### 3. Run Backtest

```python
from strategies.backtest_example import run_backtest, generate_sample_data

market_data = generate_sample_data("BTC/USD", days=30)
results = run_backtest(strategy, market_data)

print(f"Total Return: {results['total_return_pct']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
```

## Strategy Blueprint Format

A Strategy Blueprint is a JSON file that defines:

- **name**: Strategy identifier
- **description**: Strategy description
- **parameters**: Strategy-specific parameters
- **indicators**: Technical indicators to calculate
- **entry_rules**: Conditions for entering long/short positions
- **exit_rules**: Conditions for exiting positions
- **risk_management**: Stop loss, take profit, position sizing

### Example Blueprint

```json
{
  "name": "moving_average_cross",
  "description": "MA Crossover Strategy",
  "parameters": {
    "fast_period": 10,
    "slow_period": 30
  },
  "indicators": [
    {
      "name": "fast_ma",
      "type": "SMA",
      "params": {"period": 10}
    }
  ],
  "entry_rules": {
    "long": ["fast_ma > slow_ma"],
    "short": ["fast_ma < slow_ma"]
  },
  "exit_rules": {
    "long": ["fast_ma < slow_ma"]
  },
  "risk_management": {
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.05,
    "max_position_size": 0.2
  }
}
```

## BaseStrategy API

### Required Methods

- `calculate_indicators(market_data: List[MarketData]) -> Dict[str, IndicatorResult]`
- `generate_signal(market_data, indicators, current_position) -> Signal`

### Built-in Methods

- `calculate_position_size(signal, current_capital, risk_per_trade) -> Decimal`
- `check_stop_loss_take_profit(position, current_price) -> Optional[Signal]`
- `process_market_data(market_data) -> List[Signal]`
- `get_strategy_state() -> Dict[str, Any]`

## Signal Types

- `SignalType.BUY`: Enter long position
- `SignalType.SELL`: Enter short position
- `SignalType.CLOSE`: Close current position
- `SignalType.HOLD`: No action

## Risk Management

Strategies support:

- **Stop Loss**: Percentage-based stop loss
- **Take Profit**: Percentage-based take profit
- **Position Sizing**: Based on risk per trade and capital
- **Max Position Size**: Limit position size as fraction of capital

## Notes on Assumptions

When translating blueprints, the following assumptions are made:

1. **Indicator Calculations**: Basic implementations provided for SMA, EMA, RSI. Complex indicators may need manual implementation.

2. **Entry/Exit Rules**: Blueprint rules are translated to code structure, but complex logic (crossovers, multiple conditions) may need manual refinement.

3. **Position Sizing**: Defaults to risk-based sizing with stop loss. Override `calculate_position_size()` for custom logic.

4. **Market Data**: Assumes OHLCV format. Adjust `MarketData` structure if needed.

5. **Backtesting**: Example backtest is simplified. Real backtests should handle:
   - Slippage
   - Fees
   - Order execution delays
   - Margin requirements (for shorts)

## Extending the Framework

### Adding New Indicators

1. Add indicator calculation function to your strategy
2. Return `IndicatorResult` in `calculate_indicators()`
3. Use in `generate_signal()`

### Adding New Signal Types

Extend `SignalType` enum in `base.py`:

```python
class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    HOLD = "HOLD"
    PARTIAL_CLOSE = "PARTIAL_CLOSE"  # New type
```

### Custom Risk Management

Override `calculate_position_size()` in your strategy:

```python
def calculate_position_size(self, signal, current_capital, risk_per_trade):
    # Your custom logic
    return custom_size
```

## License

MIT


