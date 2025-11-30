"""
Example: Moving Average Crossover Strategy

This is a simple example strategy demonstrating the RAI-ALGO framework.
It generates BUY signals when a fast MA crosses above a slow MA,
and SELL signals when the fast MA crosses below the slow MA.
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional

from rai_algo.base import (
    BaseStrategy,
    MarketData,
    IndicatorResult,
    Signal,
    SignalType,
    Position,
)


def calculate_sma(prices: List[Decimal], period: int) -> Decimal:
    """
    Calculate Simple Moving Average.
    
    Args:
        prices: List of prices (typically closes)
        period: Period for MA calculation
        
    Returns:
        SMA value
    """
    if len(prices) < period:
        return Decimal("0")
    return sum(prices[-period:]) / Decimal(period)


def calculate_ema(prices: List[Decimal], period: int, previous_ema: Optional[Decimal] = None) -> Decimal:
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices: List of prices
        period: Period for EMA calculation
        previous_ema: Previous EMA value (for recursive calculation)
        
    Returns:
        EMA value
    """
    if len(prices) < period:
        return Decimal("0")
    
    multiplier = Decimal("2") / Decimal(period + 1)
    
    if previous_ema is None:
        # Initialize with SMA
        sma = calculate_sma(prices, period)
        return sma
    
    # EMA = (Price - Previous EMA) * Multiplier + Previous EMA
    current_price = prices[-1]
    ema = (current_price - previous_ema) * multiplier + previous_ema
    return ema


class MovingAverageCrossStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.
    
    Entry Rules:
    - BUY when fast MA crosses above slow MA
    - SELL when fast MA crosses below slow MA
    
    Exit Rules:
    - Close position on opposite crossover
    - Stop loss and take profit if configured
    """
    
    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 30,
        ma_type: str = "SMA",  # "SMA" or "EMA"
        **kwargs
    ):
        """
        Initialize Moving Average Cross Strategy.
        
        Args:
            fast_period: Fast moving average period
            slow_period: Slow moving average period
            ma_type: Type of moving average ("SMA" or "EMA")
            **kwargs: Additional parameters passed to BaseStrategy
        """
        super().__init__(
            name="MovingAverageCross",
            **kwargs
        )
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.ma_type = ma_type.upper()
        
        if self.ma_type not in ["SMA", "EMA"]:
            raise ValueError("ma_type must be 'SMA' or 'EMA'")
        
        # Track previous MA values for crossover detection
        self.previous_fast_ma: Optional[Decimal] = None
        self.previous_slow_ma: Optional[Decimal] = None
        self.previous_ema_fast: Optional[Decimal] = None
        self.previous_ema_slow: Optional[Decimal] = None
    
    def calculate_indicators(self, market_data: List[MarketData]) -> Dict[str, IndicatorResult]:
        """
        Calculate moving averages.
        
        Args:
            market_data: Historical market data
            
        Returns:
            Dictionary with 'fast_ma' and 'slow_ma' indicators
        """
        if len(market_data) < self.slow_period:
            return {
                "fast_ma": IndicatorResult(
                    value=Decimal("0"),
                    timestamp=market_data[-1].timestamp if market_data else datetime.now()
                ),
                "slow_ma": IndicatorResult(
                    value=Decimal("0"),
                    timestamp=market_data[-1].timestamp if market_data else datetime.now()
                ),
            }
        
        closes = [md.close for md in market_data]
        timestamp = market_data[-1].timestamp
        
        if self.ma_type == "SMA":
            fast_ma = calculate_sma(closes, self.fast_period)
            slow_ma = calculate_sma(closes, self.slow_period)
        else:  # EMA
            # For EMA, we need to calculate recursively
            # In a real implementation, you'd maintain state better
            fast_ma = calculate_ema(closes, self.fast_period, self.previous_ema_fast)
            slow_ma = calculate_ema(closes, self.slow_period, self.previous_ema_slow)
            
            # Update previous values
            self.previous_ema_fast = fast_ma
            self.previous_ema_slow = slow_ma
        
        return {
            "fast_ma": IndicatorResult(
                value=fast_ma,
                timestamp=timestamp,
                metadata={"period": self.fast_period, "type": self.ma_type}
            ),
            "slow_ma": IndicatorResult(
                value=slow_ma,
                timestamp=timestamp,
                metadata={"period": self.slow_period, "type": self.ma_type}
            ),
        }
    
    def generate_signal(
        self,
        market_data: List[MarketData],
        indicators: Dict[str, IndicatorResult],
        current_position: Optional[Position]
    ) -> Signal:
        """
        Generate trading signal based on MA crossover.
        
        Args:
            market_data: Historical market data
            indicators: Calculated indicators
            current_position: Current position (if any)
            
        Returns:
            Trading signal
        """
        if not market_data:
            return Signal(
                signal_type=SignalType.HOLD,
                timestamp=datetime.now(),
                symbol="",
                price=Decimal("0"),
                confidence=Decimal("0"),
                reason="No market data"
            )
        
        current_price = market_data[-1].close
        symbol = market_data[-1].symbol
        timestamp = market_data[-1].timestamp
        
        fast_ma = indicators.get("fast_ma")
        slow_ma = indicators.get("slow_ma")
        
        if not fast_ma or not slow_ma or fast_ma.value == 0 or slow_ma.value == 0:
            return Signal(
                signal_type=SignalType.HOLD,
                timestamp=timestamp,
                symbol=symbol,
                price=current_price,
                confidence=Decimal("0"),
                reason="Insufficient data for indicators"
            )
        
        # Detect crossover
        current_fast = fast_ma.value
        current_slow = slow_ma.value
        
        # If we have a position, check for exit
        if current_position:
            if current_position.is_long:
                # Exit long on bearish crossover
                if current_fast < current_slow and self.previous_fast_ma and self.previous_slow_ma:
                    if self.previous_fast_ma >= self.previous_slow_ma:  # Was above, now below
                        return Signal(
                            signal_type=SignalType.CLOSE,
                            timestamp=timestamp,
                            symbol=symbol,
                            price=current_price,
                            confidence=Decimal("0.8"),
                            reason=f"Bearish MA crossover: Fast MA ({current_fast}) crossed below Slow MA ({current_slow})"
                        )
            else:  # short position
                # Exit short on bullish crossover
                if current_fast > current_slow and self.previous_fast_ma and self.previous_slow_ma:
                    if self.previous_fast_ma <= self.previous_slow_ma:  # Was below, now above
                        return Signal(
                            signal_type=SignalType.CLOSE,
                            timestamp=timestamp,
                            symbol=symbol,
                            price=current_price,
                            confidence=Decimal("0.8"),
                            reason=f"Bullish MA crossover: Fast MA ({current_fast}) crossed above Slow MA ({current_slow})"
                        )
        
        # Entry signals (only if no position)
        if not current_position:
            # Bullish crossover: fast crosses above slow
            if current_fast > current_slow and self.previous_fast_ma and self.previous_slow_ma:
                if self.previous_fast_ma <= self.previous_slow_ma:  # Was below, now above
                    # Calculate confidence based on how far apart the MAs are
                    ma_spread = (current_fast - current_slow) / current_slow
                    confidence = min(Decimal("0.9"), Decimal("0.5") + ma_spread * Decimal("10"))
                    
                    return Signal(
                        signal_type=SignalType.BUY,
                        timestamp=timestamp,
                        symbol=symbol,
                        price=current_price,
                        confidence=confidence,
                        reason=f"Bullish MA crossover: Fast MA ({current_fast}) crossed above Slow MA ({current_slow})"
                    )
            
            # Bearish crossover: fast crosses below slow
            if current_fast < current_slow and self.previous_fast_ma and self.previous_slow_ma:
                if self.previous_fast_ma >= self.previous_slow_ma:  # Was above, now below
                    # Calculate confidence
                    ma_spread = (current_slow - current_fast) / current_slow
                    confidence = min(Decimal("0.9"), Decimal("0.5") + ma_spread * Decimal("10"))
                    
                    return Signal(
                        signal_type=SignalType.SELL,
                        timestamp=timestamp,
                        symbol=symbol,
                        price=current_price,
                        confidence=confidence,
                        reason=f"Bearish MA crossover: Fast MA ({current_fast}) crossed below Slow MA ({current_slow})"
                    )
        
        # Update previous values
        self.previous_fast_ma = current_fast
        self.previous_slow_ma = current_slow
        
        return Signal(
            signal_type=SignalType.HOLD,
            timestamp=timestamp,
            symbol=symbol,
            price=current_price,
            confidence=Decimal("0"),
            reason="No crossover detected"
        )


