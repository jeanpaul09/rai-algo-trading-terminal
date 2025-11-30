"""
Generic bar-based backtesting engine.
"""
import logging
from typing import Callable, Optional, Dict, Any, Union, List
from datetime import datetime
from abc import ABC, abstractmethod

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

logger = logging.getLogger(__name__)


class FeeModel(ABC):
    """Abstract base class for fee models."""
    
    @abstractmethod
    def calculate_fee(self, price: float, size: float, is_entry: bool) -> float:
        """
        Calculate trading fee.
        
        Args:
            price: Trade price
            size: Position size
            is_entry: True for entry, False for exit
            
        Returns:
            Fee amount
        """
        pass


class FixedFeeModel(FeeModel):
    """Fixed percentage fee model."""
    
    def __init__(self, fee_rate: float = 0.001):
        """
        Initialize fixed fee model.
        
        Args:
            fee_rate: Fee rate (e.g., 0.001 = 0.1%)
        """
        self.fee_rate = fee_rate
    
    def calculate_fee(self, price: float, size: float, is_entry: bool) -> float:
        """Calculate fee as percentage of trade value."""
        return price * size * self.fee_rate


class SlippageModel(ABC):
    """Abstract base class for slippage models."""
    
    @abstractmethod
    def apply_slippage(self, price: float, size: float, is_buy: bool) -> float:
        """
        Apply slippage to trade price.
        
        Args:
            price: Original price
            size: Trade size
            is_buy: True for buy orders, False for sell orders
            
        Returns:
            Price with slippage applied
        """
        pass


class FixedSlippageModel(SlippageModel):
    """Fixed percentage slippage model."""
    
    def __init__(self, slippage_rate: float = 0.0005):
        """
        Initialize fixed slippage model.
        
        Args:
            slippage_rate: Slippage rate (e.g., 0.0005 = 0.05%)
        """
        self.slippage_rate = slippage_rate
    
    def apply_slippage(self, price: float, size: float, is_buy: bool) -> float:
        """
        Apply slippage: buy orders pay more, sell orders receive less.
        """
        if is_buy:
            return price * (1 + self.slippage_rate)
        else:
            return price * (1 - self.slippage_rate)


class Trade:
    """Represents a single trade."""
    
    def __init__(
        self,
        entry_time: datetime,
        exit_time: datetime,
        entry_price: float,
        exit_price: float,
        size: float,
        is_long: bool,
        fee_entry: float,
        fee_exit: float,
    ):
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.size = size
        self.is_long = is_long
        self.fee_entry = fee_entry
        self.fee_exit = fee_exit
    
    @property
    def pnl(self) -> float:
        """Calculate profit/loss."""
        if self.is_long:
            gross_pnl = (self.exit_price - self.entry_price) * self.size
        else:
            gross_pnl = (self.entry_price - self.exit_price) * self.size
        return gross_pnl - self.fee_entry - self.fee_exit
    
    @property
    def pnl_pct(self) -> float:
        """Calculate profit/loss percentage."""
        if self.is_long:
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100
    
    @property
    def duration(self) -> float:
        """Trade duration in hours."""
        delta = self.exit_time - self.entry_time
        return delta.total_seconds() / 3600.0


class BacktestEngine:
    """
    Generic bar-based backtesting engine.
    
    Works with Pandas or Polars DataFrames and accepts strategy callbacks.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        fee_model: Optional[FeeModel] = None,
        slippage_model: Optional[SlippageModel] = None,
    ):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital
            fee_model: Fee model (defaults to FixedFeeModel with 0.1% fee)
            slippage_model: Slippage model (defaults to FixedSlippageModel with 0.05% slippage)
        """
        self.initial_capital = initial_capital
        self.fee_model = fee_model or FixedFeeModel(0.001)
        self.slippage_model = slippage_model or FixedSlippageModel(0.0005)
    
    def run(
        self,
        price_data: Union[pd.DataFrame, pl.DataFrame],
        strategy: Callable,
        initial_capital: Optional[float] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data.
        
        Args:
            price_data: DataFrame with timestamp, open, high, low, close, volume
                       Must have timestamp as column or index
            strategy: Strategy function that takes (data_slice, current_index, state) 
                     and returns position signal:
                     - 1.0 for long (100% of capital)
                     - -1.0 for short (100% of capital)
                     - 0.0 for no position
                     - Or target position size as fraction of capital
            initial_capital: Override initial capital (uses self.initial_capital if None)
            verbose: Print progress if True
            
        Returns:
            Dictionary with:
            - trades: List of Trade objects
            - equity_curve: List of portfolio values over time
            - timestamps: List of timestamps
            - cash: Final cash balance
            - positions: Final position size
        """
        if initial_capital is None:
            initial_capital = self.initial_capital
        
        # Normalize DataFrame
        is_polars = isinstance(price_data, pl.DataFrame) if POLARS_AVAILABLE else False
        
        if is_polars:
            # Convert to Pandas for easier manipulation (can optimize later)
            price_data = price_data.to_pandas()
            is_polars = False
        
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is required for backtesting")
        
        # Ensure timestamp is a column
        if isinstance(price_data.index, pd.DatetimeIndex):
            price_data = price_data.reset_index()
            if 'date' in price_data.columns:
                price_data = price_data.rename(columns={'date': 'timestamp'})
            elif price_data.columns[0] == 'index':
                price_data = price_data.rename(columns={'index': 'timestamp'})
        
        if 'timestamp' not in price_data.columns:
            raise ValueError("DataFrame must have 'timestamp' column or datetime index")
        
        # Sort by timestamp
        price_data = price_data.sort_values('timestamp').reset_index(drop=True)
        
        # Initialize state
        cash = initial_capital
        position_size = 0.0  # Current position size (positive = long, negative = short)
        position_entry_price = 0.0
        position_entry_time = None
        position_is_long = True
        
        trades: List[Trade] = []
        equity_curve = [initial_capital]
        timestamps = [price_data['timestamp'].iloc[0]]
        
        strategy_state: Dict[str, Any] = {}
        
        # Iterate through bars
        for i in range(len(price_data)):
            row = price_data.iloc[i]
            timestamp = row['timestamp']
            current_price = row['close']
            high = row['high']
            low = row['low']
            
            # Get data slice up to current bar (for strategy to use)
            data_slice = price_data.iloc[:i+1]
            
            # Get strategy signal
            try:
                target_position = strategy(data_slice, i, strategy_state)
            except Exception as e:
                logger.error(f"Strategy error at bar {i}: {e}")
                target_position = 0.0
            
            # Normalize target position to -1.0 to 1.0 range
            if target_position > 1.0:
                target_position = 1.0
            elif target_position < -1.0:
                target_position = -1.0
            
            # Calculate current portfolio value
            if position_size != 0.0:
                if position_is_long:
                    position_value = position_size * current_price
                else:
                    position_value = -position_size * current_price
            else:
                position_value = 0.0
            
            current_equity = cash + position_value
            
            # Check if we need to adjust position
            current_position_signal = 1.0 if position_size > 0 else (-1.0 if position_size < 0 else 0.0)
            
            if abs(target_position - current_position_signal) > 0.01:  # Threshold to avoid tiny trades
                # Close existing position if any
                if position_size != 0.0:
                    exit_price = self.slippage_model.apply_slippage(
                        current_price,
                        abs(position_size),
                        is_buy=(not position_is_long),  # Exit long = sell, exit short = buy
                    )
                    
                    fee_exit = self.fee_model.calculate_fee(
                        exit_price,
                        abs(position_size),
                        is_entry=False,
                    )
                    
                    # Calculate PnL
                    if position_is_long:
                        gross_pnl = (exit_price - position_entry_price) * position_size
                    else:
                        gross_pnl = (position_entry_price - exit_price) * abs(position_size)
                    
                    net_pnl = gross_pnl - fee_exit
                    cash += net_pnl
                    
                    # Record trade
                    trade = Trade(
                        entry_time=position_entry_time,
                        exit_time=timestamp,
                        entry_price=position_entry_price,
                        exit_price=exit_price,
                        size=abs(position_size),
                        is_long=position_is_long,
                        fee_entry=0.0,  # Will be calculated when we track entry fees
                        fee_exit=fee_exit,
                    )
                    trades.append(trade)
                    
                    if verbose:
                        logger.info(
                            f"Closed {'long' if position_is_long else 'short'} position: "
                            f"PnL={net_pnl:.2f}, Cash={cash:.2f}"
                        )
                    
                    position_size = 0.0
                    position_entry_price = 0.0
                    position_entry_time = None
                
                # Open new position if target is not zero
                if abs(target_position) > 0.01:
                    # Calculate position size based on available capital
                    available_capital = cash
                    target_capital = available_capital * abs(target_position)
                    
                    entry_price = self.slippage_model.apply_slippage(
                        current_price,
                        target_capital / current_price,
                        is_buy=(target_position > 0),
                    )
                    
                    position_size_units = target_capital / entry_price
                    
                    fee_entry = self.fee_model.calculate_fee(
                        entry_price,
                        position_size_units,
                        is_entry=True,
                    )
                    
                    # Deduct fee from cash
                    cash -= fee_entry
                    
                    position_size = position_size_units if target_position > 0 else -position_size_units
                    position_entry_price = entry_price
                    position_entry_time = timestamp
                    position_is_long = (target_position > 0)
                    
                    if verbose:
                        logger.info(
                            f"Opened {'long' if position_is_long else 'short'} position: "
                            f"Price={entry_price:.2f}, Size={abs(position_size):.4f}, Cash={cash:.2f}"
                        )
            
            # Update equity curve
            if position_size != 0.0:
                if position_is_long:
                    position_value = position_size * current_price
                else:
                    position_value = -position_size * current_price
            else:
                position_value = 0.0
            
            current_equity = cash + position_value
            equity_curve.append(current_equity)
            timestamps.append(timestamp)
        
        # Close any remaining position at final bar
        if position_size != 0.0:
            final_row = price_data.iloc[-1]
            final_price = final_row['close']
            exit_price = self.slippage_model.apply_slippage(
                final_price,
                abs(position_size),
                is_buy=(not position_is_long),
            )
            
            fee_exit = self.fee_model.calculate_fee(
                exit_price,
                abs(position_size),
                is_entry=False,
            )
            
            if position_is_long:
                gross_pnl = (exit_price - position_entry_price) * position_size
            else:
                gross_pnl = (position_entry_price - exit_price) * abs(position_size)
            
            net_pnl = gross_pnl - fee_exit
            cash += net_pnl
            
            trade = Trade(
                entry_time=position_entry_time,
                exit_time=final_row['timestamp'],
                entry_price=position_entry_price,
                exit_price=exit_price,
                size=abs(position_size),
                is_long=position_is_long,
                fee_entry=0.0,
                fee_exit=fee_exit,
            )
            trades.append(trade)
            
            equity_curve[-1] = cash
            position_size = 0.0
        
        return {
            'trades': trades,
            'equity_curve': equity_curve,
            'timestamps': timestamps,
            'cash': cash,
            'position': position_size,
            'initial_capital': initial_capital,
        }


