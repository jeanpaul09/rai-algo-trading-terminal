# AGENT 5 — ENSEMBLE BUILDER

Takes a list of strategies with backtest results and combines them into robust ensembles.

## Features

1. **Identifies Complementary Strategies**: Finds low-correlation strategy pairs for better diversification
2. **Constructs Ensembles**:
   - Weighted blends (Sharpe-optimized, volatility-adjusted, equal-weight)
   - Volatility-adjusted allocation (inverse volatility weighting)
   - Switching regimes (momentum when trending, mean reversion when flat)
3. **Evaluates Portfolio-Level Performance**:
   - Sharpe ratio
   - Max drawdown
   - Correlation matrix
   - Exposure limits
4. **Removes Harmful Strategies**: Automatically removes strategies that hurt ensemble performance

## Quick Start

```python
from rai_algo.ensemble_builder import build_ensemble_from_backtests

# Your backtest results
backtest_results = [
    {
        "name": "momentum_strategy",
        "returns": [0.01, -0.02, 0.03, ...],  # List of period returns
        "sharpe": 1.5,
        "max_drawdown": 0.15,
        "volatility": 0.20,
        "total_return": 0.25,
        "metadata": {"type": "momentum"}  # Optional
    },
    # ... more strategies
]

# Build ensemble
ensemble = build_ensemble_from_backtests(
    backtest_results=backtest_results,
    method="sharpe_optimized",  # or "volatility_adjusted" or "equal"
    risk_free_rate=0.02,
    remove_harmful=True
)

# Output format
print(ensemble)
# {
#   "ensemble_members": ["momentum_strategy", "mean_reversion_strategy"],
#   "weights": {"momentum_strategy": 0.6, "mean_reversion_strategy": 0.4},
#   "portfolio_sharpe": "1.8234",
#   "portfolio_drawdown": "0.1234",
#   "correlations": {...},
#   "regime_map": "trending",
#   "execution_rules": "..."
# }
```

## Advanced Usage

### Custom Ensemble Builder

```python
from rai_algo.ensemble_builder import EnsembleBuilder, StrategyBacktest
import numpy as np

# Create StrategyBacktest objects
strategies = [
    StrategyBacktest(
        name="strategy_1",
        returns=np.array([0.01, -0.02, 0.03, ...]),
        sharpe=1.5,
        max_drawdown=0.15,
        volatility=0.20,
        total_return=0.25,
        metadata={"type": "momentum"}
    ),
    # ... more strategies
]

# Create builder with custom parameters
builder = EnsembleBuilder(
    strategies=strategies,
    risk_free_rate=0.02,
    min_correlation=-0.3,
    max_correlation=0.7,
    max_exposure=0.4  # Max 40% per strategy
)

# Build ensemble
ensemble = builder.build_ensemble(
    method="sharpe_optimized",
    remove_harmful=True,
    target_volatility=None
)
```

### Weighting Methods

1. **`sharpe_optimized`** (default): Optimizes weights to maximize Sharpe ratio using mean-variance optimization
2. **`volatility_adjusted`**: Inverse volatility weighting (lower volatility = higher weight)
3. **`equal`**: Equal weights for all strategies

### Regime Detection

The ensemble builder automatically detects market regimes:
- **`trending`**: Positive momentum, favors momentum strategies
- **`mean_reverting`**: High volatility or negative autocorrelation, favors mean reversion strategies
- **`neutral`**: Balanced allocation

Regime-specific weights are included in the output for dynamic allocation.

## Output Format

```python
{
    "ensemble_members": ["strategy1", "strategy2"],  # Strategies in final ensemble
    "weights": {"strategy1": 0.6, "strategy2": 0.4},  # Allocation weights
    "portfolio_sharpe": "1.8234",  # Portfolio Sharpe ratio
    "portfolio_drawdown": "0.1234",  # Portfolio max drawdown
    "correlations": {  # Full correlation matrix
        "strategy1": {"strategy1": 1.0, "strategy2": 0.2, ...},
        "strategy2": {"strategy1": 0.2, "strategy2": 1.0, ...},
        ...
    },
    "regime_map": "trending",  # Current market regime
    "execution_rules": "..."  # Human-readable execution rules
}
```

## Key Rules

- **Favors stable, low-correlation combinations**: Strategies with correlation < 0.5 are preferred
- **Removes harmful strategies**: If a strategy hurts the ensemble (reduces Sharpe), it's automatically removed
- **Exposure limits**: Maximum weight per strategy (default 40%) to prevent over-concentration
- **Regime-aware**: Adjusts allocation based on market conditions

## Example

See `ensemble_example.py` for complete examples including:
- Basic usage
- Advanced customization
- Regime switching
- Correlation analysis

## Dependencies

- `numpy`: For numerical computations
- Standard library: `typing`, `dataclasses`, `collections`, `json`

## Notes

- All strategy returns must have the same length
- Returns should be period returns (e.g., daily returns)
- Volatility is assumed to be annualized
- Sharpe ratio calculation uses annualized returns and volatility


