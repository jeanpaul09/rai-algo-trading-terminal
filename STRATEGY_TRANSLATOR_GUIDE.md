# Strategy Translator Guide

## Overview

The Strategy Translator (AGENT 2) converts Strategy Blueprint JSON files into production-ready Python code for the RAI-ALGO framework.

## How to Use

### Step 1: Create a Strategy Blueprint JSON

Create a JSON file following this structure:

```json
{
  "name": "my_strategy",
  "description": "Strategy description",
  "parameters": {
    "param1": 10,
    "param2": "value"
  },
  "indicators": [
    {
      "name": "indicator_name",
      "type": "SMA|EMA|RSI|MACD|...",
      "params": {
        "period": 14
      }
    }
  ],
  "entry_rules": {
    "long": ["condition1", "condition2"],
    "short": ["condition1"]
  },
  "exit_rules": {
    "long": ["exit_condition"],
    "short": ["exit_condition"]
  },
  "risk_management": {
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.05,
    "max_position_size": 0.2,
    "risk_per_trade": 0.02
  }
}
```

### Step 2: Translate Blueprint to Python

```bash
python translate_blueprint.py blueprints/my_strategy.json strategies/my_strategy.py
```

Or use the Python API:

```python
from rai_algo.blueprint_translator import translate_blueprint

translate_blueprint("blueprints/my_strategy.json", "strategies/my_strategy.py")
```

### Step 3: Review and Refine Generated Code

The translator generates a complete strategy class, but you may need to:

1. **Implement complex entry/exit logic**: The blueprint rules are translated to code structure with TODO comments
2. **Add custom indicators**: If using unsupported indicator types, implement the calculation function
3. **Refine signal confidence**: Adjust confidence calculation based on your strategy logic
4. **Add additional validation**: Add checks for edge cases

### Step 4: Test Your Strategy

```python
from strategies.my_strategy import MyStrategy
from strategies.backtest_example import run_backtest, generate_sample_data
from decimal import Decimal

# Create strategy instance
strategy = MyStrategy(
    initial_capital=Decimal("10000"),
    stop_loss_pct=Decimal("0.02"),
    take_profit_pct=Decimal("0.05")
)

# Generate test data
market_data = generate_sample_data("BTC/USD", days=30)

# Run backtest
results = run_backtest(strategy, market_data)

# Review results
print(f"Total Return: {results['total_return_pct']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
```

## Blueprint Field Reference

### Required Fields

- **name** (string): Strategy identifier (used for class name)

### Optional Fields

- **description** (string): Strategy description
- **parameters** (object): Strategy-specific parameters
- **indicators** (array): List of indicators to calculate
- **entry_rules** (object): Entry conditions for long/short
- **exit_rules** (object): Exit conditions for long/short
- **risk_management** (object): Risk management settings

### Indicator Types

Currently supported:
- **SMA**: Simple Moving Average
- **EMA**: Exponential Moving Average
- **RSI**: Relative Strength Index

To add support for more indicators, extend `BlueprintTranslator.INDICATOR_TEMPLATES`.

### Entry/Exit Rules Format

Rules are described as strings that will be translated to code structure. Examples:

- `"fast_ma > slow_ma"` → Code checks if fast_ma > slow_ma
- `"rsi < 30"` → Code checks if RSI < 30
- `"fast_ma crosses above slow_ma"` → Code detects crossover

**Note**: Complex logic (crossovers, multiple conditions) may need manual implementation after translation.

## Example: Complete Workflow

### 1. Create Blueprint

`blueprints/rsi_strategy.json`:
```json
{
  "name": "rsi_mean_reversion",
  "description": "RSI Mean Reversion Strategy",
  "parameters": {
    "rsi_period": 14,
    "oversold": 30,
    "overbought": 70
  },
  "indicators": [
    {
      "name": "rsi",
      "type": "RSI",
      "params": {"period": 14}
    }
  ],
  "entry_rules": {
    "long": ["rsi < 30"],
    "short": ["rsi > 70"]
  },
  "exit_rules": {
    "long": ["rsi > 50"],
    "short": ["rsi < 50"]
  },
  "risk_management": {
    "stop_loss_pct": 0.03,
    "take_profit_pct": 0.04,
    "max_position_size": 0.15
  }
}
```

### 2. Translate

```bash
python translate_blueprint.py blueprints/rsi_strategy.json strategies/rsi_strategy.py
```

### 3. Review Generated Code

Open `strategies/rsi_strategy.py` and implement the TODO sections:

```python
# In generate_signal method, replace TODO with:
if not current_position:
    rsi = indicators.get("rsi")
    if rsi and rsi.value > 0:
        if rsi.value < Decimal("30"):  # Oversold
            return Signal(
                signal_type=SignalType.BUY,
                timestamp=timestamp,
                symbol=symbol,
                price=current_price,
                confidence=Decimal("0.7"),
                reason=f"RSI oversold: {rsi.value}"
            )
        elif rsi.value > Decimal("70"):  # Overbought
            return Signal(
                signal_type=SignalType.SELL,
                timestamp=timestamp,
                symbol=symbol,
                price=current_price,
                confidence=Decimal("0.7"),
                reason=f"RSI overbought: {rsi.value}"
            )
```

### 4. Test

```python
from strategies.rsi_strategy import RsiMeanReversion
# ... run backtest
```

## Assumptions and Limitations

### What the Translator Does

✅ Generates complete strategy class structure  
✅ Implements indicator calculations (SMA, EMA, RSI)  
✅ Sets up risk management parameters  
✅ Creates entry/exit rule code structure  
✅ Adds type hints and docstrings  

### What You Need to Do

⚠️ Implement complex entry/exit logic (crossovers, multiple conditions)  
⚠️ Add custom indicators not in the template library  
⚠️ Refine signal confidence calculations  
⚠️ Add edge case handling  
⚠️ Test and validate strategy logic  

### Assumptions Made

1. **Market Data Format**: Assumes OHLCV (Open, High, Low, Close, Volume)
2. **Indicator Periods**: Minimum data required = indicator period
3. **Position Sizing**: Defaults to risk-based with stop loss
4. **Signal Confidence**: Starts at 0.5-0.9 range, adjust as needed
5. **Backtesting**: Simplified (no slippage/fees in example)

## Tips for Best Results

1. **Start Simple**: Begin with basic indicators (SMA, EMA, RSI)
2. **Test Incrementally**: Test each indicator calculation separately
3. **Validate Logic**: Manually verify entry/exit conditions
4. **Backtest Thoroughly**: Use historical data to validate strategy
5. **Refine Confidence**: Adjust confidence based on backtest results
6. **Add Logging**: Add logging to debug signal generation

## Next Steps

After translating a blueprint:

1. Review generated code
2. Implement TODO sections
3. Add unit tests for indicators
4. Run backtests with historical data
5. Refine parameters based on results
6. Deploy to paper trading
7. Monitor and optimize

## Support

For questions or issues:
- Review example strategies in `strategies/`
- Check `rai_algo/README.md` for framework documentation
- Review blueprint examples in `blueprints/`


