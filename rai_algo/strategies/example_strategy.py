"""
Example trading strategy for RAI-ALGO framework.
Simple moving average crossover strategy.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from rai_algo.base import BaseStrategy
from rai_algo.data_types import MarketData, Signal, SignalType, Position


class ExampleStrategy(BaseStrategy):
    """
    Example moving average crossover strategy.
    
    Parameters:
    - fast_period: Fast MA period (default: 10)
    - slow_period: Slow MA period (default: 30)
    - stop_loss: Stop loss percentage (default: 0.02 = 2%)
    - take_profit: Take profit percentage (default: 0.05 = 5%)
    """
    
    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(name="ExampleMAStrategy", parameters=parameters)
        self.fast_period = self.get_parameter("fast_period", 10)
        self.slow_period = self.get_parameter("slow_period", 30)
        self.stop_loss = self.get_parameter("stop_loss", 0.02)
        self.take_profit = self.get_parameter("take_profit", 0.05)
    
    def get_required_history_length(self) -> int:
        """Require enough history for slow MA."""
        return self.slow_period + 5
    
    def _calculate_ma(self, prices: List[float], period: int) -> float:
        """Calculate simple moving average."""
        if len(prices) < period:
            return 0.0
        return sum(prices[-period:]) / period
    
    def generate_signal(
        self,
        market_data: MarketData,
        history: List[MarketData],
        current_position: Optional[Position] = None,
    ) -> Signal:
        """Generate trading signal based on MA crossover."""
        # Need enough history
        if len(history) < self.slow_period:
            return Signal(
                signal_type=SignalType.HOLD,
                strength=0.0,
                price=market_data.price,
                timestamp=datetime.now(),
            )
        
        # Extract prices
        prices = [md.close for md in history]
        
        # Calculate MAs
        fast_ma = self._calculate_ma(prices, self.fast_period)
        slow_ma = self._calculate_ma(prices, self.slow_period)
        
        # Previous MAs for crossover detection
        prev_prices = prices[:-1] if len(prices) > 1 else prices
        prev_fast_ma = self._calculate_ma(prev_prices, self.fast_period) if len(prev_prices) >= self.fast_period else fast_ma
        prev_slow_ma = self._calculate_ma(prev_prices, self.slow_period) if len(prev_prices) >= self.slow_period else slow_ma
        
        # Check for stop loss or take profit on existing position
        if current_position and current_position.is_open:
            # Check stop loss
            if current_position.stop_loss and market_data.price <= current_position.stop_loss:
                return Signal(
                    signal_type=SignalType.CLOSE,
                    strength=1.0,
                    price=market_data.price,
                    timestamp=datetime.now(),
                )
            
            # Check take profit
            if current_position.take_profit and market_data.price >= current_position.take_profit:
                return Signal(
                    signal_type=SignalType.CLOSE,
                    strength=1.0,
                    price=market_data.price,
                    timestamp=datetime.now(),
                )
        
        # Crossover signals
        # Bullish crossover: fast MA crosses above slow MA
        if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
            if current_position is None or not current_position.is_open:
                stop_loss_price = market_data.price * (1 - self.stop_loss)
                take_profit_price = market_data.price * (1 + self.take_profit)
                
                return Signal(
                    signal_type=SignalType.BUY,
                    strength=0.8,
                    price=market_data.price,
                    timestamp=datetime.now(),
                    metadata={"stop_loss": stop_loss_price, "take_profit": take_profit_price},
                )
        
        # Bearish crossover: fast MA crosses below slow MA
        if prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
            if current_position and current_position.is_open:
                return Signal(
                    signal_type=SignalType.CLOSE,
                    strength=0.8,
                    price=market_data.price,
                    timestamp=datetime.now(),
                )
        
        # Default: hold
        return Signal(
            signal_type=SignalType.HOLD,
            strength=0.5,
            price=market_data.price,
            timestamp=datetime.now(),
        )

