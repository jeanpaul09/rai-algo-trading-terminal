"""
Example trading strategies for RAI-ALGO framework.
"""
import numpy as np
from datetime import datetime
from typing import List, Optional

from rai_algo.base import BaseStrategy
from rai_algo.data_types import MarketData, Signal, SignalType, Position


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy.
    
    Parameters:
        ma_fast: Fast moving average period (default: 10)
        ma_slow: Slow moving average period (default: 30)
        stop_loss_pct: Stop loss percentage (default: 0.02 = 2%)
        take_profit_pct: Take profit percentage (default: 0.05 = 5%)
    """
    
    def __init__(self, name: str = "MA_Crossover", parameters: Optional[dict] = None):
        super().__init__(name, parameters)
        self.ma_fast_period = self.get_parameter('ma_fast', 10)
        self.ma_slow_period = self.get_parameter('ma_slow', 30)
    
    def get_required_history_length(self) -> int:
        """Require enough history for slow MA."""
        return max(self.ma_fast_period, self.ma_slow_period) + 1
    
    def generate_signal(
        self,
        market_data: MarketData,
        history: List[MarketData],
        current_position: Optional[Position] = None,
    ) -> Signal:
        """Generate signal based on MA crossover."""
        if len(history) < self.ma_slow_period:
            return Signal(
                timestamp=market_data.timestamp,
                signal_type=SignalType.HOLD,
                price=market_data.price,
            )
        
        # Calculate moving averages
        prices = [d.close for d in history[-self.ma_slow_period:]]
        ma_fast = np.mean(prices[-self.ma_fast_period:])
        ma_slow = np.mean(prices)
        
        # Previous values for crossover detection
        if len(history) >= self.ma_slow_period + 1:
            prev_prices = [d.close for d in history[-self.ma_slow_period-1:-1]]
            prev_ma_fast = np.mean(prev_prices[-self.ma_fast_period:])
            prev_ma_slow = np.mean(prev_prices)
        else:
            prev_ma_fast = ma_fast
            prev_ma_slow = ma_slow
        
        # Crossover logic
        if current_position is None:
            # No position: look for entry
            if prev_ma_fast <= prev_ma_slow and ma_fast > ma_slow:
                # Golden cross: buy signal
                return Signal(
                    timestamp=market_data.timestamp,
                    signal_type=SignalType.BUY,
                    price=market_data.price,
                    strength=min(1.0, abs(ma_fast - ma_slow) / ma_slow),
                )
            elif prev_ma_fast >= prev_ma_slow and ma_fast < ma_slow:
                # Death cross: sell signal (short)
                return Signal(
                    timestamp=market_data.timestamp,
                    signal_type=SignalType.SELL,
                    price=market_data.price,
                    strength=min(1.0, abs(ma_fast - ma_slow) / ma_slow),
                )
        else:
            # Have position: check for exit
            if current_position.signal_type == SignalType.BUY:
                # Long position: exit on death cross
                if prev_ma_fast >= prev_ma_slow and ma_fast < ma_slow:
                    return Signal(
                        timestamp=market_data.timestamp,
                        signal_type=SignalType.CLOSE,
                        price=market_data.price,
                    )
            else:
                # Short position: exit on golden cross
                if prev_ma_fast <= prev_ma_slow and ma_fast > ma_slow:
                    return Signal(
                        timestamp=market_data.timestamp,
                        signal_type=SignalType.CLOSE,
                        price=market_data.price,
                    )
        
        return Signal(
            timestamp=market_data.timestamp,
            signal_type=SignalType.HOLD,
            price=market_data.price,
        )


class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) strategy.
    
    Parameters:
        rsi_period: RSI calculation period (default: 14)
        rsi_oversold: Oversold threshold (default: 30)
        rsi_overbought: Overbought threshold (default: 70)
        stop_loss_pct: Stop loss percentage
        take_profit_pct: Take profit percentage
    """
    
    def __init__(self, name: str = "RSI", parameters: Optional[dict] = None):
        super().__init__(name, parameters)
        self.rsi_period = self.get_parameter('rsi_period', 14)
        self.rsi_oversold = self.get_parameter('rsi_oversold', 30)
        self.rsi_overbought = self.get_parameter('rsi_overbought', 70)
    
    def get_required_history_length(self) -> int:
        """Require enough history for RSI calculation."""
        return self.rsi_period + 1
    
    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI from price list."""
        if len(prices) < self.rsi_period + 1:
            return 50.0  # Neutral
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-self.rsi_period:])
        avg_loss = np.mean(losses[-self.rsi_period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signal(
        self,
        market_data: MarketData,
        history: List[MarketData],
        current_position: Optional[Position] = None,
    ) -> Signal:
        """Generate signal based on RSI."""
        if len(history) < self.rsi_period:
            return Signal(
                timestamp=market_data.timestamp,
                signal_type=SignalType.HOLD,
                price=market_data.price,
            )
        
        prices = [d.close for d in history[-self.rsi_period-1:]] + [market_data.close]
        rsi = self._calculate_rsi(prices)
        
        if current_position is None:
            # No position: look for entry
            if rsi < self.rsi_oversold:
                # Oversold: buy signal
                strength = (self.rsi_oversold - rsi) / self.rsi_oversold
                return Signal(
                    timestamp=market_data.timestamp,
                    signal_type=SignalType.BUY,
                    price=market_data.price,
                    strength=min(1.0, strength),
                )
            elif rsi > self.rsi_overbought:
                # Overbought: sell signal (short)
                strength = (rsi - self.rsi_overbought) / (100 - self.rsi_overbought)
                return Signal(
                    timestamp=market_data.timestamp,
                    signal_type=SignalType.SELL,
                    price=market_data.price,
                    strength=min(1.0, strength),
                )
        else:
            # Have position: check for exit
            if current_position.signal_type == SignalType.BUY:
                # Long position: exit when RSI becomes overbought
                if rsi > self.rsi_overbought:
                    return Signal(
                        timestamp=market_data.timestamp,
                        signal_type=SignalType.CLOSE,
                        price=market_data.price,
                    )
            else:
                # Short position: exit when RSI becomes oversold
                if rsi < self.rsi_oversold:
                    return Signal(
                        timestamp=market_data.timestamp,
                        signal_type=SignalType.CLOSE,
                        price=market_data.price,
                    )
        
        return Signal(
            timestamp=market_data.timestamp,
            signal_type=SignalType.HOLD,
            price=market_data.price,
        )


class TrendFollowingStrategy(BaseStrategy):
    """
    Trend following strategy with volatility filter.
    
    Parameters:
        ma_period: Moving average period (default: 20)
        volatility_period: Period for volatility calculation (default: 20)
        volatility_threshold: Minimum volatility to trade (default: 0.02 = 2%)
        trend_strength_threshold: Minimum trend strength (default: 0.01 = 1%)
        stop_loss_pct: Stop loss percentage
        take_profit_pct: Take profit percentage
    """
    
    def __init__(self, name: str = "TrendFollowing", parameters: Optional[dict] = None):
        super().__init__(name, parameters)
        self.ma_period = self.get_parameter('ma_period', 20)
        self.volatility_period = self.get_parameter('volatility_period', 20)
        self.volatility_threshold = self.get_parameter('volatility_threshold', 0.02)
        self.trend_strength_threshold = self.get_parameter('trend_strength_threshold', 0.01)
    
    def get_required_history_length(self) -> int:
        """Require enough history for MA and volatility."""
        return max(self.ma_period, self.volatility_period) + 1
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate volatility (std dev of returns)."""
        if len(prices) < 2:
            return 0.0
        
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns)
    
    def generate_signal(
        self,
        market_data: MarketData,
        history: List[MarketData],
        current_position: Optional[Position] = None,
    ) -> Signal:
        """Generate signal based on trend and volatility."""
        if len(history) < max(self.ma_period, self.volatility_period):
            return Signal(
                timestamp=market_data.timestamp,
                signal_type=SignalType.HOLD,
                price=market_data.price,
            )
        
        # Calculate moving average
        prices = [d.close for d in history[-self.ma_period:]] + [market_data.close]
        ma = np.mean(prices[-self.ma_period:])
        
        # Calculate volatility
        vol_prices = [d.close for d in history[-self.volatility_period:]] + [market_data.close]
        volatility = self._calculate_volatility(vol_prices)
        
        # Check volatility filter
        if volatility < self.volatility_threshold:
            return Signal(
                timestamp=market_data.timestamp,
                signal_type=SignalType.HOLD,
                price=market_data.price,
                metadata={"reason": "low_volatility", "volatility": volatility},
            )
        
        # Calculate trend strength
        trend_strength = abs(market_data.price - ma) / ma
        
        # Check trend strength filter
        if trend_strength < self.trend_strength_threshold:
            return Signal(
                timestamp=market_data.timestamp,
                signal_type=SignalType.HOLD,
                price=market_data.price,
                metadata={"reason": "weak_trend", "trend_strength": trend_strength},
            )
        
        if current_position is None:
            # No position: enter trend
            if market_data.price > ma * (1 + self.trend_strength_threshold):
                # Uptrend: buy
                return Signal(
                    timestamp=market_data.timestamp,
                    signal_type=SignalType.BUY,
                    price=market_data.price,
                    strength=min(1.0, trend_strength / 0.05),
                )
            elif market_data.price < ma * (1 - self.trend_strength_threshold):
                # Downtrend: sell (short)
                return Signal(
                    timestamp=market_data.timestamp,
                    signal_type=SignalType.SELL,
                    price=market_data.price,
                    strength=min(1.0, trend_strength / 0.05),
                )
        else:
            # Have position: exit on trend reversal
            if current_position.signal_type == SignalType.BUY:
                if market_data.price < ma:
                    return Signal(
                        timestamp=market_data.timestamp,
                        signal_type=SignalType.CLOSE,
                        price=market_data.price,
                    )
            else:
                if market_data.price > ma:
                    return Signal(
                        timestamp=market_data.timestamp,
                        signal_type=SignalType.CLOSE,
                        price=market_data.price,
                    )
        
        return Signal(
            timestamp=market_data.timestamp,
            signal_type=SignalType.HOLD,
            price=market_data.price,
        )

