"""
Risk management module for live trading.
Implements position limits, daily loss limits, and auto-kill switch.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging

from rai_algo.data_types import Position, Signal
from rai_algo.exchange import Order


logger = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    """Risk limit configuration."""
    max_daily_loss: float = 0.05  # 5% of account
    max_position_size: float = 0.10  # 10% of account per position
    max_total_exposure: float = 0.50  # 50% of account total exposure
    max_drawdown: float = 0.15  # 15% max drawdown
    min_balance: float = 0.0  # Minimum account balance
    max_orders_per_day: int = 100
    max_orders_per_hour: int = 20


@dataclass
class DailyStats:
    """Daily trading statistics."""
    date: datetime
    starting_balance: float
    current_balance: float
    total_pnl: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    trades_count: int = 0
    orders_count: int = 0
    orders_by_hour: Dict[int, int] = field(default_factory=dict)
    max_drawdown: float = 0.0
    peak_balance: float = 0.0


class RiskManager:
    """
    Risk management system for live trading.
    
    Features:
    - Max daily loss monitoring
    - Position size limits
    - Auto-kill switch
    - Order rate limiting
    - Drawdown protection
    """
    
    def __init__(
        self,
        initial_balance: float,
        risk_limits: Optional[RiskLimits] = None,
    ):
        """
        Initialize risk manager.
        
        Args:
            initial_balance: Starting account balance
            risk_limits: Risk limit configuration
        """
        self.risk_limits = risk_limits or RiskLimits()
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.daily_stats: Optional[DailyStats] = None
        self.is_killed = False
        self.kill_reason: Optional[str] = None
        self._reset_daily_stats()
    
    def _reset_daily_stats(self):
        """Reset daily statistics for new trading day."""
        today = datetime.now().date()
        if self.daily_stats is None or self.daily_stats.date.date() != today:
            self.daily_stats = DailyStats(
                date=datetime.now(),
                starting_balance=self.current_balance,
                current_balance=self.current_balance,
                peak_balance=self.current_balance,
            )
            logger.info(f"Daily stats reset. Starting balance: ${self.current_balance:.2f}")
    
    def update_balance(self, new_balance: float):
        """Update current account balance."""
        self._reset_daily_stats()
        old_balance = self.current_balance
        self.current_balance = new_balance
        
        if self.daily_stats:
            self.daily_stats.current_balance = new_balance
            self.daily_stats.total_pnl = new_balance - self.daily_stats.starting_balance
            
            # Update peak balance and drawdown
            if new_balance > self.daily_stats.peak_balance:
                self.daily_stats.peak_balance = new_balance
            
            drawdown = (self.daily_stats.peak_balance - new_balance) / self.daily_stats.peak_balance
            if drawdown > self.daily_stats.max_drawdown:
                self.daily_stats.max_drawdown = drawdown
            
            # Check for daily loss limit breach
            daily_loss = self.daily_stats.starting_balance - new_balance
            daily_loss_pct = daily_loss / self.daily_stats.starting_balance if self.daily_stats.starting_balance > 0 else 0
            
            if daily_loss_pct >= self.risk_limits.max_daily_loss:
                self.kill(f"Daily loss limit exceeded: {daily_loss_pct:.2%} >= {self.risk_limits.max_daily_loss:.2%}")
            
            # Check for max drawdown breach
            if self.daily_stats.max_drawdown >= self.risk_limits.max_drawdown:
                self.kill(f"Max drawdown exceeded: {self.daily_stats.max_drawdown:.2%} >= {self.risk_limits.max_drawdown:.2%}")
            
            # Check for minimum balance
            if new_balance < self.risk_limits.min_balance:
                self.kill(f"Balance below minimum: ${new_balance:.2f} < ${self.risk_limits.min_balance:.2f}")
    
    def check_position_size(self, signal: Signal, current_balance: float, price: float) -> bool:
        """
        Check if position size is within limits.
        
        Args:
            signal: Trading signal
            current_balance: Current account balance
            price: Current market price
            
        Returns:
            True if position size is acceptable, False otherwise
        """
        # Calculate position size based on signal strength
        max_position_value = current_balance * self.risk_limits.max_position_size
        position_value = max_position_value * signal.strength
        position_pct = position_value / current_balance if current_balance > 0 else 0
        
        if position_pct > self.risk_limits.max_position_size:
            logger.warning(
                f"Position size exceeds limit: {position_pct:.2%} > {self.risk_limits.max_position_size:.2%}"
            )
            return False
        
        return True
    
    def check_total_exposure(self, positions: Dict[str, Position], current_balance: float) -> bool:
        """
        Check if total exposure is within limits.
        
        Args:
            positions: Dictionary of current positions
            current_balance: Current account balance
            
        Returns:
            True if total exposure is acceptable, False otherwise
        """
        total_exposure = sum(
            pos.size * (pos.current_price if pos.current_price else pos.entry_price)
            for pos in positions.values()
            if pos.is_open
        )
        exposure_pct = total_exposure / current_balance if current_balance > 0 else 0
        
        if exposure_pct > self.risk_limits.max_total_exposure:
            logger.warning(
                f"Total exposure exceeds limit: {exposure_pct:.2%} > {self.risk_limits.max_total_exposure:.2%}"
            )
            return False
        
        return True
    
    def check_order_rate(self) -> bool:
        """
        Check if order rate limits are respected.
        
        Returns:
            True if order rate is acceptable, False otherwise
        """
        if not self.daily_stats:
            return True
        
        # Check daily limit
        if self.daily_stats.orders_count >= self.risk_limits.max_orders_per_day:
            logger.warning(f"Daily order limit reached: {self.daily_stats.orders_count}")
            return False
        
        # Check hourly limit
        current_hour = datetime.now().hour
        hour_count = self.daily_stats.orders_by_hour.get(current_hour, 0)
        if hour_count >= self.risk_limits.max_orders_per_hour:
            logger.warning(f"Hourly order limit reached: {hour_count}")
            return False
        
        return True
    
    def record_order(self):
        """Record an order for rate limiting."""
        if self.daily_stats:
            self.daily_stats.orders_count += 1
            current_hour = datetime.now().hour
            self.daily_stats.orders_by_hour[current_hour] = (
                self.daily_stats.orders_by_hour.get(current_hour, 0) + 1
            )
    
    def record_trade(self, pnl: float):
        """Record a completed trade."""
        if self.daily_stats:
            self.daily_stats.trades_count += 1
            self.daily_stats.realized_pnl += pnl
    
    def validate_signal(
        self, 
        signal: Signal, 
        positions: Dict[str, Position], 
        symbol: str, 
        current_price: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a trading signal against all risk limits.
        
        Args:
            signal: Trading signal to validate
            positions: Current open positions
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        if self.is_killed:
            return False, f"Trading killed: {self.kill_reason}"
        
        # Check position size
        if not self.check_position_size(signal, self.current_balance, current_price):
            return False, "Position size exceeds limit"
        
        # Check total exposure (if opening new position)
        if signal.signal_type.value in ["buy", "sell"]:
            if not self.check_total_exposure(positions, self.current_balance):
                return False, "Total exposure exceeds limit"
        
        # Check order rate
        if not self.check_order_rate():
            return False, "Order rate limit exceeded"
        
        return True, None
    
    def kill(self, reason: str):
        """
        Activate auto-kill switch.
        
        Args:
            reason: Reason for killing trading
        """
        if not self.is_killed:
            self.is_killed = True
            self.kill_reason = reason
            logger.critical(f"🚨 TRADING KILLED: {reason}")
    
    def reset_kill_switch(self):
        """Reset kill switch (requires manual intervention)."""
        self.is_killed = False
        self.kill_reason = None
        logger.info("Kill switch reset. Trading resumed.")
    
    def get_status(self) -> Dict:
        """Get current risk manager status."""
        return {
            "is_killed": self.is_killed,
            "kill_reason": self.kill_reason,
            "current_balance": self.current_balance,
            "daily_stats": {
                "total_pnl": self.daily_stats.total_pnl if self.daily_stats else 0,
                "trades_count": self.daily_stats.trades_count if self.daily_stats else 0,
                "orders_count": self.daily_stats.orders_count if self.daily_stats else 0,
                "max_drawdown": self.daily_stats.max_drawdown if self.daily_stats else 0,
            } if self.daily_stats else None,
        }

