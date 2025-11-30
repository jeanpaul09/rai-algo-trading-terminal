"""
Performance metrics for backtesting results.
"""
import logging
from typing import Union, Dict, Any, List, TYPE_CHECKING
import math

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl
    import numpy as np

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None  # type: ignore
    PANDAS_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    pl = None  # type: ignore
    POLARS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None  # type: ignore
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


def evaluate_performance(
    equity_curve: Union[Any, Any, List[float]],  # Union[pd.Series, pl.Series, List[float]]
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252,
) -> Dict[str, float]:
    """
    Calculate comprehensive performance metrics from equity curve.
    
    Args:
        equity_curve: Series or list of portfolio values over time
        risk_free_rate: Annual risk-free rate (default 2%)
        periods_per_year: Number of periods per year (252 for daily, 365 for hourly, etc.)
        
    Returns:
        Dictionary with performance metrics
    """
    # Convert to list if needed
    if PANDAS_AVAILABLE and pd is not None and isinstance(equity_curve, pd.Series):
        equity_values = equity_curve.values.tolist()
    elif POLARS_AVAILABLE and pl is not None and isinstance(equity_curve, pl.Series):
        equity_values = equity_curve.to_list()
    else:
        equity_values = list(equity_curve)
    
    if len(equity_values) < 2:
        raise ValueError("Equity curve must have at least 2 values")
    
    initial_value = equity_values[0]
    final_value = equity_values[-1]
    
    # Calculate returns
    if NUMPY_AVAILABLE:
        equity_array = np.array(equity_values)
        returns = np.diff(equity_array) / equity_array[:-1]
    else:
        returns = [
            (equity_values[i+1] - equity_values[i]) / equity_values[i]
            for i in range(len(equity_values) - 1)
        ]
    
    # Total return
    total_return = (final_value - initial_value) / initial_value
    
    # CAGR
    n_periods = len(equity_values) - 1
    years = n_periods / periods_per_year
    if years > 0:
        cagr = ((final_value / initial_value) ** (1 / years)) - 1
    else:
        cagr = 0.0
    
    # Sharpe ratio
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate, periods_per_year)
    
    # Sortino ratio
    sortino = calculate_sortino_ratio(returns, risk_free_rate, periods_per_year)
    
    # Max drawdown
    max_dd, max_dd_pct = calculate_max_drawdown(equity_values)
    
    return {
        'total_return': total_return,
        'total_return_pct': total_return * 100,
        'cagr': cagr,
        'cagr_pct': cagr * 100,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown': max_dd,
        'max_drawdown_pct': max_dd_pct,
        'initial_value': initial_value,
        'final_value': final_value,
    }


def calculate_sharpe_ratio(
    returns: Union[List[float], Any],  # Union[List[float], Any]
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate annualized Sharpe ratio.
    
    Args:
        returns: List or array of period returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year
        
    Returns:
        Annualized Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0
    
    if NUMPY_AVAILABLE:
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array, ddof=1)
    else:
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        std_return = math.sqrt(variance)
    
    if std_return == 0:
        return 0.0
    
    # Annualize
    period_rf_rate = risk_free_rate / periods_per_year
    excess_return = mean_return - period_rf_rate
    annualized_excess = excess_return * periods_per_year
    annualized_std = std_return * math.sqrt(periods_per_year)
    
    if annualized_std == 0:
        return 0.0
    
    return annualized_excess / annualized_std


def calculate_sortino_ratio(
    returns: Union[List[float], Any],
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate annualized Sortino ratio (downside deviation only).
    
    Args:
        returns: List or array of period returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year
        
    Returns:
        Annualized Sortino ratio
    """
    if len(returns) == 0:
        return 0.0
    
    if NUMPY_AVAILABLE:
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        # Only negative returns for downside deviation
        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) == 0:
            downside_std = 0.0
        else:
            downside_std = np.std(downside_returns, ddof=1)
    else:
        mean_return = sum(returns) / len(returns)
        downside_returns = [r for r in returns if r < 0]
        if len(downside_returns) == 0:
            downside_std = 0.0
        else:
            downside_mean = sum(downside_returns) / len(downside_returns)
            downside_variance = sum((r - downside_mean) ** 2 for r in downside_returns) / (len(downside_returns) - 1)
            downside_std = math.sqrt(downside_variance)
    
    if downside_std == 0:
        return float('inf') if mean_return > risk_free_rate / periods_per_year else 0.0
    
    # Annualize
    period_rf_rate = risk_free_rate / periods_per_year
    excess_return = mean_return - period_rf_rate
    annualized_excess = excess_return * periods_per_year
    annualized_downside_std = downside_std * math.sqrt(periods_per_year)
    
    if annualized_downside_std == 0:
        return 0.0
    
    return annualized_excess / annualized_downside_std


def calculate_max_drawdown(
    equity_curve: Union[List[float], Any, Any],  # Union[List[float], pd.Series, pl.Series]
) -> tuple[float, float]:
    """
    Calculate maximum drawdown.
    
    Args:
        equity_curve: List or Series of portfolio values
        
    Returns:
        Tuple of (max_drawdown_absolute, max_drawdown_percentage)
    """
    if PANDAS_AVAILABLE and pd is not None and isinstance(equity_curve, pd.Series):
        values = equity_curve.values
    elif POLARS_AVAILABLE and pl is not None and isinstance(equity_curve, pl.Series):
        values = equity_curve.to_numpy()
    else:
        values = list(equity_curve)
    
    if len(values) == 0:
        return 0.0, 0.0
    
    peak = values[0]
    max_dd = 0.0
    max_dd_pct = 0.0
    
    for value in values:
        if value > peak:
            peak = value
        drawdown = peak - value
        drawdown_pct = (drawdown / peak) * 100 if peak > 0 else 0.0
        
        if drawdown > max_dd:
            max_dd = drawdown
            max_dd_pct = drawdown_pct
    
    return max_dd, max_dd_pct


def calculate_cagr(
    initial_value: float,
    final_value: float,
    years: float,
) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).
    
    Args:
        initial_value: Starting value
        final_value: Ending value
        years: Number of years
        
    Returns:
        CAGR as decimal (e.g., 0.15 for 15%)
    """
    if years <= 0 or initial_value <= 0:
        return 0.0
    
    return ((final_value / initial_value) ** (1 / years)) - 1


def calculate_win_rate(trades: List[Any]) -> Dict[str, float]:
    """
    Calculate win rate and related statistics from trades.
    
    Args:
        trades: List of Trade objects with 'pnl' attribute
        
    Returns:
        Dictionary with win_rate, avg_win, avg_loss, profit_factor
    """
    if len(trades) == 0:
        return {
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
        }
    
    winning_trades = [t for t in trades if hasattr(t, 'pnl') and t.pnl > 0]
    losing_trades = [t for t in trades if hasattr(t, 'pnl') and t.pnl <= 0]
    
    win_rate = len(winning_trades) / len(trades) if trades else 0.0
    
    avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
    avg_loss = abs(sum(t.pnl for t in losing_trades) / len(losing_trades)) if losing_trades else 0.0
    
    total_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0.0
    total_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0.0
    
    profit_factor = total_profit / total_loss if total_loss > 0 else (float('inf') if total_profit > 0 else 0.0)
    
    return {
        'win_rate': win_rate,
        'win_rate_pct': win_rate * 100,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
    }


def calculate_profit_factor(trades: List[Any]) -> float:
    """
    Calculate profit factor (total profit / total loss).
    
    Args:
        trades: List of Trade objects with 'pnl' attribute
        
    Returns:
        Profit factor
    """
    if len(trades) == 0:
        return 0.0
    
    winning_trades = [t for t in trades if hasattr(t, 'pnl') and t.pnl > 0]
    losing_trades = [t for t in trades if hasattr(t, 'pnl') and t.pnl <= 0]
    
    total_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0.0
    total_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0.0
    
    if total_loss == 0:
        return float('inf') if total_profit > 0 else 0.0
    
    return total_profit / total_loss


