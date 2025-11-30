"""
RAI-ALGO Framework
A clean, exchange-agnostic algorithmic trading framework.
"""

__version__ = "1.0.0"

from rai_algo.base import BaseStrategy
# Types are imported from data_types
from rai_algo.data_types import BacktestResult, OptimizationResult
from rai_algo.backtest import BacktestEngine
from rai_algo.optimizer import Optimizer
from rai_algo.agent4_optimizer import Agent4StrategyOptimizer, WeaknessAnalysis
from rai_algo.exchange import BaseExchange, Order, Balance
from rai_algo.risk import RiskManager, RiskLimits
from rai_algo.live_trader import LiveTrader, TraderConfig

# Try to import ensemble_builder if it exists (optional)
try:
    from rai_algo.ensemble_builder import (
        EnsembleBuilder,
        StrategyBacktest,
        build_ensemble_from_backtests,
    )
    __all__ = [
        "BaseStrategy",
        "Signal",
        "SignalType",
        "Position",
        "MarketData",
        "IndicatorResult",
        "BacktestResult",
        "OptimizationResult",
        "BacktestEngine",
        "Optimizer",
        "Agent4StrategyOptimizer",
        "WeaknessAnalysis",
        "EnsembleBuilder",
        "StrategyBacktest",
        "build_ensemble_from_backtests",
        # Live Trading
        "BaseExchange",
        "Order",
        "Balance",
        "RiskManager",
        "RiskLimits",
        "LiveTrader",
        "TraderConfig",
    ]
except ImportError:
    __all__ = [
        "BaseStrategy",
        "Signal",
        "SignalType",
        "Position",
        "MarketData",
        "IndicatorResult",
        "BacktestResult",
        "OptimizationResult",
        "BacktestEngine",
        "Optimizer",
        "Agent4StrategyOptimizer",
        "WeaknessAnalysis",
        # Live Trading
        "BaseExchange",
        "Order",
        "Balance",
        "RiskManager",
        "RiskLimits",
        "LiveTrader",
        "TraderConfig",
    ]

