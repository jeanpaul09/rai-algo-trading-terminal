"""
Type definitions and utilities for RAI-ALGO framework.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class SignalType(Enum):
    """Trading signal types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"


@dataclass
class MarketData:
    """Market data point."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def price(self) -> float:
        """Current price (close)."""
        return self.close


@dataclass
class Signal:
    """Trading signal."""
    signal_type: SignalType
    strength: float  # 0.0 to 1.0
    price: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Position:
    """Trading position."""
    entry_price: float
    size: float
    entry_time: datetime
    current_price: Optional[float] = None
    
    # Exit information
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    signal_type: SignalType = SignalType.BUY
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def is_open(self) -> bool:
        """Check if position is open."""
        return self.exit_time is None
    
    @property
    def pnl(self) -> Optional[float]:
        """Profit and loss (if closed)."""
        if self.exit_price is None:
            return None
        
        if self.signal_type == SignalType.BUY:
            return (self.exit_price - self.entry_price) * self.size
        else:  # SELL (short)
            return (self.entry_price - self.exit_price) * self.size
    
    @property
    def pnl_pct(self) -> Optional[float]:
        """Profit and loss percentage (if closed)."""
        if self.exit_price is None:
            return None
        
        if self.signal_type == SignalType.BUY:
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SELL (short)
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100
    
    def update_exit(self, timestamp: datetime, price: float):
        """Update position with exit information."""
        self.exit_time = timestamp
        self.exit_price = price


@dataclass
class IndicatorResult:
    """Indicator calculation result."""
    value: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BacktestResult:
    """Backtest results."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    avg_trade_duration: float  # in hours
    trades: List[Position]
    equity_curve: List[float]
    drawdown_curve: List[float]
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": round(self.win_rate, 4),
            "total_return": round(self.total_return, 2),
            "total_return_pct": round(self.total_return_pct, 4),
            "sharpe_ratio": round(self.sharpe_ratio, 4),
            "max_drawdown": round(self.max_drawdown, 2),
            "max_drawdown_pct": round(self.max_drawdown_pct, 4),
            "avg_win": round(self.avg_win, 2),
            "avg_loss": round(self.avg_loss, 2),
            "profit_factor": round(self.profit_factor, 4),
            "avg_trade_duration": round(self.avg_trade_duration, 2),
            "parameters": self.parameters,
        }


@dataclass
class OptimizationResult:
    """Parameter optimization result."""
    best_parameters: Dict[str, Any]
    best_score: float
    best_backtest: BacktestResult
    all_results: List[tuple[Dict[str, Any], BacktestResult]]  # (params, result)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "best_parameters": self.best_parameters,
            "best_score": round(self.best_score, 4),
            "best_backtest": self.best_backtest.to_dict(),
        }


__all__ = [
    "MarketData",
    "IndicatorResult",
    "Signal",
    "SignalType",
    "Position",
    "BacktestResult",
    "OptimizationResult",
]
