"""
Example usage of AGENT 5 — ENSEMBLE BUILDER

Demonstrates how to combine multiple strategy backtests into robust ensembles.
"""

import numpy as np
import json
from rai_algo.ensemble_builder import build_ensemble_from_backtests, EnsembleBuilder, StrategyBacktest


def generate_sample_backtest_results():
    """Generate sample backtest results for demonstration."""
    
    np.random.seed(42)
    n_periods = 252  # 1 year of daily data
    
    # Strategy 1: Momentum strategy (trending)
    momentum_returns = np.random.normal(0.0008, 0.015, n_periods)  # High return, high vol
    momentum_returns[0:50] += 0.002  # Strong trend early
    momentum_returns[200:252] += 0.001  # Another trend
    
    # Strategy 2: Mean reversion strategy (contrarian)
    mean_reversion_returns = np.random.normal(0.0005, 0.012, n_periods)
    # Negative correlation with momentum
    mean_reversion_returns = -0.3 * momentum_returns + 0.954 * mean_reversion_returns
    
    # Strategy 3: Low volatility strategy
    low_vol_returns = np.random.normal(0.0004, 0.008, n_periods)
    # Low correlation with others
    low_vol_returns = 0.1 * momentum_returns + 0.1 * mean_reversion_returns + 0.894 * low_vol_returns
    
    # Strategy 4: High Sharpe strategy (good risk-adjusted returns)
    high_sharpe_returns = np.random.normal(0.0006, 0.010, n_periods)
    # Moderate correlation
    high_sharpe_returns = 0.2 * momentum_returns + 0.2 * mean_reversion_returns + 0.775 * high_sharpe_returns
    
    # Strategy 5: Poor performing strategy (will be removed)
    poor_returns = np.random.normal(-0.0002, 0.018, n_periods)
    # High negative correlation (hurts portfolio)
    poor_returns = -0.5 * momentum_returns + 0.866 * poor_returns
    
    strategies = [
        {
            "name": "momentum_trend",
            "returns": momentum_returns.tolist(),
            "sharpe": 1.2,
            "max_drawdown": 0.18,
            "volatility": 0.24,
            "total_return": 0.20,
            "metadata": {"type": "momentum", "description": "Trend-following strategy"}
        },
        {
            "name": "mean_reversion",
            "returns": mean_reversion_returns.tolist(),
            "sharpe": 0.9,
            "max_drawdown": 0.15,
            "volatility": 0.19,
            "total_return": 0.13,
            "metadata": {"type": "mean_reversion", "description": "Contrarian strategy"}
        },
        {
            "name": "low_volatility",
            "returns": low_vol_returns.tolist(),
            "sharpe": 1.5,
            "max_drawdown": 0.10,
            "volatility": 0.13,
            "total_return": 0.15,
            "metadata": {"type": "low_vol", "description": "Low volatility strategy"}
        },
        {
            "name": "high_sharpe",
            "returns": high_sharpe_returns.tolist(),
            "sharpe": 1.8,
            "max_drawdown": 0.12,
            "volatility": 0.16,
            "total_return": 0.18,
            "metadata": {"type": "balanced", "description": "High Sharpe ratio strategy"}
        },
        {
            "name": "poor_performer",
            "returns": poor_returns.tolist(),
            "sharpe": -0.3,
            "max_drawdown": 0.25,
            "volatility": 0.28,
            "total_return": -0.05,
            "metadata": {"type": "unknown", "description": "Underperforming strategy"}
        }
    ]
    
    return strategies


def example_basic_usage():
    """Basic example: Build ensemble from backtest results."""
    print("=" * 60)
    print("AGENT 5 — ENSEMBLE BUILDER - Basic Example")
    print("=" * 60)
    
    # Get sample backtest results
    backtest_results = generate_sample_backtest_results()
    
    print(f"\nInput: {len(backtest_results)} strategies")
    for result in backtest_results:
        print(f"  - {result['name']}: Sharpe={result['sharpe']:.2f}, "
              f"Drawdown={result['max_drawdown']:.2%}, "
              f"Return={result['total_return']:.2%}")
    
    # Build ensemble
    ensemble = build_ensemble_from_backtests(
        backtest_results=backtest_results,
        method="sharpe_optimized",
        risk_free_rate=0.02,  # 2% risk-free rate
        remove_harmful=True
    )
    
    # Print results
    print("\n" + "=" * 60)
    print("ENSEMBLE RESULTS")
    print("=" * 60)
    print(json.dumps(ensemble, indent=2))
    
    return ensemble


def example_advanced_usage():
    """Advanced example: Custom ensemble building with different methods."""
    print("\n" + "=" * 60)
    print("AGENT 5 — ENSEMBLE BUILDER - Advanced Example")
    print("=" * 60)
    
    backtest_results = generate_sample_backtest_results()
    
    # Convert to StrategyBacktest objects
    strategies = []
    for result in backtest_results:
        strategies.append(StrategyBacktest(
            name=result["name"],
            returns=np.array(result["returns"]),
            sharpe=result["sharpe"],
            max_drawdown=result["max_drawdown"],
            volatility=result["volatility"],
            total_return=result["total_return"],
            metadata=result.get("metadata", {})
        ))
    
    # Create builder
    builder = EnsembleBuilder(
        strategies=strategies,
        risk_free_rate=0.02,
        max_exposure=0.35  # Max 35% per strategy
    )
    
    # Compare different methods
    methods = ["sharpe_optimized", "volatility_adjusted", "equal"]
    
    print("\nComparing weighting methods:")
    print("-" * 60)
    
    for method in methods:
        ensemble = builder.build_ensemble(method=method, remove_harmful=True)
        print(f"\n{method.upper()}:")
        print(f"  Portfolio Sharpe: {ensemble['portfolio_sharpe']}")
        print(f"  Portfolio Drawdown: {ensemble['portfolio_drawdown']}")
        print(f"  Members: {', '.join(ensemble['ensemble_members'])}")
        print(f"  Weights: {ensemble['weights']}")
    
    # Show correlation matrix
    corr_matrix = builder.compute_correlation_matrix()
    print("\n" + "=" * 60)
    print("CORRELATION MATRIX")
    print("=" * 60)
    strategy_names = [s.name for s in strategies]
    print(f"{'Strategy':<20}", end="")
    for name in strategy_names:
        print(f"{name[:10]:>12}", end="")
    print()
    for i, name1 in enumerate(strategy_names):
        print(f"{name1:<20}", end="")
        for j, name2 in enumerate(strategy_names):
            print(f"{corr_matrix[i, j]:>12.3f}", end="")
        print()


def example_regime_switching():
    """Example: Regime-based ensemble switching."""
    print("\n" + "=" * 60)
    print("AGENT 5 — ENSEMBLE BUILDER - Regime Switching Example")
    print("=" * 60)
    
    backtest_results = generate_sample_backtest_results()
    strategies = []
    for result in backtest_results:
        strategies.append(StrategyBacktest(
            name=result["name"],
            returns=np.array(result["returns"]),
            sharpe=result["sharpe"],
            max_drawdown=result["max_drawdown"],
            volatility=result["volatility"],
            total_return=result["total_return"],
            metadata=result.get("metadata", {})
        ))
    
    builder = EnsembleBuilder(strategies=strategies, risk_free_rate=0.02)
    
    # Build ensemble with regime switching
    ensemble = builder.build_ensemble(method="sharpe_optimized", remove_harmful=True)
    
    print(f"\nCurrent Regime: {ensemble['regime_map']}")
    print(f"\nExecution Rules:\n{ensemble['execution_rules']}")


if __name__ == "__main__":
    # Run examples
    example_basic_usage()
    example_advanced_usage()
    example_regime_switching()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


