"""
Base strategy class for RAI-ALGO framework.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from rai_algo.data_types import (
    MarketData,
    Signal,
    SignalType,
    Position,
    IndicatorResult,
)


class BaseStrategy(ABC):
    """
    Base class for trading strategies.
    
    Subclasses should implement:
    - generate_signal(): Generate trading signals based on market data
    - Optional: update_state(): Update internal state with new data
    """
    
    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            parameters: Strategy parameters (e.g., {'stop_loss': 0.02, 'take_profit': 0.05})
        """
        self.name = name
        self.parameters = parameters or {}
        self.state: Dict[str, Any] = {}
        
    @abstractmethod
    def generate_signal(
        self,
        market_data: MarketData,
        history: List[MarketData],
        current_position: Optional[Position] = None,
    ) -> Signal:
        """
        Generate trading signal based on market data.
        
        Args:
            market_data: Current market data point
            history: Historical market data (for indicators)
            current_position: Current open position (if any)
            
        Returns:
            Signal object
        """
        pass
    
    def update_state(self, market_data: MarketData, signal: Signal):
        """
        Update internal strategy state.
        
        Override this if your strategy maintains state between signals.
        """
        pass
    
    def get_required_history_length(self) -> int:
        """
        Return minimum number of historical data points needed.
        
        Override if your strategy requires lookback (e.g., for moving averages).
        """
        return 1
    
    def reset(self):
        """Reset strategy state (useful for backtesting)."""
        self.state = {}
    
    def set_parameter(self, key: str, value: Any):
        """Set a strategy parameter."""
        self.parameters[key] = value
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a strategy parameter."""
        return self.parameters.get(key, default)
