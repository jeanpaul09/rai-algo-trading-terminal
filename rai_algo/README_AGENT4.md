# AGENT 4 — STRATEGY OPTIMIZER

AGENT 4 is a comprehensive strategy optimization system that takes a trading strategy, backtests it, identifies weaknesses, and optimizes parameters.

## Features

1. **Backtesting Engine** (`backtest.py`)
   - Simulates strategy execution on historical data
   - Calculates comprehensive metrics:
     - Total return, Sharpe ratio
     - Max drawdown
     - Win rate, profit factor
     - Average win/loss, trade duration
   - Accounts for commission and slippage

2. **Parameter Optimization** (`optimizer.py`)
   - Grid search parameter optimization
   - Multiple objective functions (Sharpe ratio, total return, profit factor)
   - Constraint-based optimization

3. **AGENT 4 Optimizer** (`agent4_optimizer.py`)
   - Complete optimization workflow
   - Weakness identification:
     - High drawdowns
     - Whipsaw signals
     - Slippage sensitivity
     - Low win rates
     - Poor profit factors
   - Automatic parameter grid generation
   - Comprehensive recommendations

## Usage

### Basic Example

```python
from rai_algo.agent4_optimizer import Agent4StrategyOptimizer
from rai_algo.strategies import MovingAverageCrossoverStrategy
from rai_algo.data_types import MarketData

# Initialize AGENT 4
agent4 = Agent4StrategyOptimizer(
    initial_capital=10000.0,
    commission=0.001,  # 0.1%
    slippage=0.0005,   # 0.05%
)

# Your market data
market_data = [...]  # List of MarketData objects

# Original strategy parameters
original_params = {
    'ma_fast': 10,
    'ma_slow': 30,
    'stop_loss_pct': 0.02,
    'take_profit_pct': 0.05,
}

# Run optimization
result = agent4.optimize_strategy(
    strategy_class=MovingAverageCrossoverStrategy,
    market_data=market_data,
    original_parameters=original_params,
    strategy_name="MA_Crossover",
    verbose=True,
)

# Result format
print(result)
# {
#     "original_results": {...},
#     "weakness_analysis": {...},
#     "optimized_parameters": {...},
#     "improved_results": {...},
#     "recommendations": "...",
#     "final_strategy_variant": "..."
# }
```

### Output Format

The optimizer returns a dictionary with:

```python
{
    "original_results": {
        "total_trades": 45,
        "win_rate": 0.5556,
        "total_return_pct": 12.34,
        "sharpe_ratio": 1.23,
        "max_drawdown_pct": 8.5,
        "profit_factor": 1.45,
        # ... more metrics
    },
    "weakness_analysis": {
        "high_drawdown": False,
        "drawdown_severity": "low",
        "whipsaw_signals": False,
        "slippage_sensitive": False,
        "low_win_rate": False,
        "poor_profit_factor": False,
        "weaknesses": [...],
        "recommendations": [...]
    },
    "optimized_parameters": {
        "stop_loss_pct": 0.015,
        "take_profit_pct": 0.06,
        # ... optimized values
    },
    "improved_results": {
        # Same format as original_results with improved metrics
    },
    "recommendations": "- Consider tighter stop-loss...\n- ...",
    "final_strategy_variant": "# Optimized Strategy\n..."
}
```

## Example Strategies

The framework includes example strategies in `strategies.py`:

1. **MovingAverageCrossoverStrategy** - MA crossover with stop-loss/take-profit
2. **RSIStrategy** - RSI-based mean reversion
3. **TrendFollowingStrategy** - Trend following with volatility filter

## Installation

```bash
pip install numpy
```

## Running the Demo

```bash
python3 -m rai_algo.demo_agent4
```

The demo will:
1. Generate sample market data
2. Test a Moving Average Crossover strategy
3. Identify weaknesses
4. Optimize parameters
5. Show improved results

## Custom Strategies

To create your own strategy:

```python
from rai_algo.base import BaseStrategy
from rai_algo.data_types import MarketData, Signal, SignalType, Position

class MyStrategy(BaseStrategy):
    def generate_signal(
        self,
        market_data: MarketData,
        history: List[MarketData],
        current_position: Optional[Position] = None,
    ) -> Signal:
        # Your signal generation logic
        return Signal(
            timestamp=market_data.timestamp,
            signal_type=SignalType.BUY,
            price=market_data.price,
            strength=1.0,
        )
    
    def get_required_history_length(self) -> int:
        return 20  # How many data points needed
```

## Parameter Grid Customization

You can provide custom parameter grids:

```python
parameter_grid = {
    'stop_loss_pct': [0.01, 0.02, 0.03, 0.05],
    'take_profit_pct': [0.05, 0.10, 0.15, 0.20],
    'ma_fast': [5, 10, 15, 20],
    'ma_slow': [20, 30, 40, 50],
}

result = agent4.optimize_strategy(
    strategy_class=MyStrategy,
    market_data=market_data,
    parameter_grid=parameter_grid,
    # ...
)
```

## Metrics Explained

- **Sharpe Ratio**: Risk-adjusted returns (higher is better, >1 is good)
- **Max Drawdown**: Largest peak-to-trough decline (lower is better)
- **Win Rate**: Percentage of profitable trades (>50% is good)
- **Profit Factor**: Total profit / Total loss (>1.2 is good)
- **Avg Trade Duration**: Average time position is held

## Rules

- Only proposes improvements backed by test results
- Keeps strategies realistic (no overfitting)
- Uses constraints to avoid unrealistic parameter combinations
- Provides actionable recommendations


