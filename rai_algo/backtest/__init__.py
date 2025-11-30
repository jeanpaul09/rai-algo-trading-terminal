"""
Backtesting engine for RAI-ALGO framework.
"""

from rai_algo.backtest.core import BacktestEngine, FeeModel, SlippageModel
from rai_algo.backtest.metrics import (
    evaluate_performance,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_cagr,
    calculate_win_rate,
    calculate_profit_factor,
)

__all__ = [
    "BacktestEngine",
    "FeeModel",
    "SlippageModel",
    "evaluate_performance",
    "calculate_sharpe_ratio",
    "calculate_sortino_ratio",
    "calculate_max_drawdown",
    "calculate_cagr",
    "calculate_win_rate",
    "calculate_profit_factor",
]


