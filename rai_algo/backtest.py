"""
Backtesting engine for RAI-ALGO framework.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from rai_algo.base import BaseStrategy
from rai_algo.data_types import (
    MarketData,
    Signal,
    SignalType,
    Position,
    BacktestResult,
)


class BacktestEngine:
    """
    Backtesting engine that simulates strategy execution on historical data.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,  # 0.1% commission
        slippage: float = 0.0005,  # 0.05% slippage
        position_size_pct: float = 1.0,  # 100% of capital per trade
    ):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate per trade (e.g., 0.001 = 0.1%)
            slippage: Slippage rate (e.g., 0.0005 = 0.05%)
            position_size_pct: Position size as percentage of capital (1.0 = 100%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.position_size_pct = position_size_pct
    
    def run(
        self,
        strategy: BaseStrategy,
        market_data: List[MarketData],
        verbose: bool = False,
    ) -> BacktestResult:
        """
        Run backtest on historical data.
        
        Args:
            strategy: Strategy instance to test
            market_data: Historical market data (must be sorted by timestamp)
            verbose: Print progress if True
            
        Returns:
            BacktestResult with performance metrics
        """
        if not market_data:
            raise ValueError("Market data cannot be empty")
        
        # Sort by timestamp
        market_data = sorted(market_data, key=lambda x: x.timestamp)
        
        # Reset strategy state
        strategy.reset()
        
        # Initialize tracking variables
        capital = self.initial_capital
        positions: List[Position] = []
        current_position: Optional[Position] = None
        equity_curve = [capital]
        drawdown_curve = [0.0]
        peak_equity = capital
        
        # Get required history length
        lookback = strategy.get_required_history_length()
        
        for i in range(len(market_data)):
            current_data = market_data[i]
            history = market_data[max(0, i - lookback):i]
            
            # Check if we should exit current position
            if current_position and current_position.is_open:
                exit_signal = self._check_exit_conditions(
                    current_position, current_data, strategy.parameters
                )
                
                if exit_signal:
                    # Close position
                    exit_price = self._apply_slippage(
                        current_data.price,
                        current_position.signal_type,
                        is_entry=False,
                    )
                    
                    # Calculate PnL after commission
                    commission_cost = current_position.size * exit_price * self.commission
                    pnl = self._calculate_pnl(current_position, exit_price)
                    pnl_after_commission = pnl - commission_cost
                    
                    current_position.update_exit(current_data.timestamp, exit_price)
                    capital += pnl_after_commission
                    positions.append(current_position)
                    current_position = None
                    
                    equity_curve.append(capital)
                    if capital > peak_equity:
                        peak_equity = capital
                    drawdown_curve.append((peak_equity - capital) / peak_equity * 100)
                    
                    if verbose:
                        print(f"Closed position: PnL={pnl_after_commission:.2f}, Capital={capital:.2f}")
            
            # Generate new signal
            signal = strategy.generate_signal(current_data, history, current_position)
            
            # Process signal
            if signal.signal_type in [SignalType.BUY, SignalType.SELL] and current_position is None:
                # Open new position
                entry_price = self._apply_slippage(
                    current_data.price,
                    signal.signal_type,
                    is_entry=True,
                )
                
                # Calculate position size
                position_size = self._calculate_position_size(capital, entry_price)
                
                # Deduct commission
                commission_cost = position_size * entry_price * self.commission
                capital -= commission_cost
                
                # Create position
                current_position = Position(
                    entry_time=current_data.timestamp,
                    entry_price=entry_price,
                    size=position_size,
                    signal_type=SignalType.BUY if signal.signal_type == SignalType.BUY else SignalType.SELL,
                )
                
                # Set stop loss and take profit if provided
                if 'stop_loss_pct' in strategy.parameters:
                    sl_pct = strategy.parameters['stop_loss_pct']
                    if signal.signal_type == SignalType.BUY:
                        current_position.stop_loss = entry_price * (1 - sl_pct)
                    else:
                        current_position.stop_loss = entry_price * (1 + sl_pct)
                
                if 'take_profit_pct' in strategy.parameters:
                    tp_pct = strategy.parameters['take_profit_pct']
                    if signal.signal_type == SignalType.BUY:
                        current_position.take_profit = entry_price * (1 + tp_pct)
                    else:
                        current_position.take_profit = entry_price * (1 - tp_pct)
                
                equity_curve.append(capital)
                drawdown_curve.append((peak_equity - capital) / peak_equity * 100)
                
                if verbose:
                    print(f"Opened {signal.signal_type} position: Price={entry_price:.2f}, Size={position_size:.4f}")
            
            elif signal.signal_type == SignalType.CLOSE and current_position:
                # Manual close signal
                exit_price = self._apply_slippage(
                    current_data.price,
                    current_position.signal_type,
                    is_entry=False,
                )
                
                commission_cost = current_position.size * exit_price * self.commission
                pnl = self._calculate_pnl(current_position, exit_price)
                pnl_after_commission = pnl - commission_cost
                
                current_position.update_exit(current_data.timestamp, exit_price)
                capital += pnl_after_commission
                positions.append(current_position)
                current_position = None
                
                equity_curve.append(capital)
                if capital > peak_equity:
                    peak_equity = capital
                drawdown_curve.append((peak_equity - capital) / peak_equity * 100)
            
            # Update strategy state
            strategy.update_state(current_data, signal)
        
        # Close any remaining open position at final price
        if current_position and current_position.is_open:
            final_data = market_data[-1]
            exit_price = self._apply_slippage(
                final_data.price,
                current_position.signal_type,
                is_entry=False,
            )
            
            commission_cost = current_position.size * exit_price * self.commission
            pnl = self._calculate_pnl(current_position, exit_price)
            pnl_after_commission = pnl - commission_cost
            
            current_position.update_exit(final_data.timestamp, exit_price)
            capital += pnl_after_commission
            positions.append(current_position)
            
            equity_curve.append(capital)
            if capital > peak_equity:
                peak_equity = capital
            drawdown_curve.append((peak_equity - capital) / peak_equity * 100)
        
        # Calculate metrics
        return self._calculate_metrics(positions, equity_curve, drawdown_curve, strategy.parameters)
    
    def _check_exit_conditions(
        self,
        position: Position,
        market_data: MarketData,
        parameters: Dict[str, Any],
    ) -> bool:
        """Check if position should be exited (stop loss or take profit)."""
        if position.signal_type == SignalType.BUY:
            # Long position
            if position.stop_loss and market_data.low <= position.stop_loss:
                return True
            if position.take_profit and market_data.high >= position.take_profit:
                return True
        else:
            # Short position
            if position.stop_loss and market_data.high >= position.stop_loss:
                return True
            if position.take_profit and market_data.low <= position.take_profit:
                return True
        
        return False
    
    def _apply_slippage(self, price: float, signal_type: SignalType, is_entry: bool) -> float:
        """Apply slippage to trade price."""
        if signal_type == SignalType.BUY:
            # Buy orders: pay more (slippage increases price)
            return price * (1 + self.slippage)
        else:
            # Sell orders: receive less (slippage decreases price)
            return price * (1 - self.slippage)
    
    def _calculate_position_size(self, capital: float, price: float) -> float:
        """Calculate position size based on available capital."""
        capital_to_use = capital * self.position_size_pct
        return capital_to_use / price
    
    def _calculate_pnl(self, position: Position, exit_price: float) -> float:
        """Calculate PnL for a position."""
        if position.signal_type == SignalType.BUY:
            return (exit_price - position.entry_price) * position.size
        else:
            return (position.entry_price - exit_price) * position.size
    
    def _calculate_metrics(
        self,
        positions: List[Position],
        equity_curve: List[float],
        drawdown_curve: List[float],
        parameters: Dict[str, Any],
    ) -> BacktestResult:
        """Calculate performance metrics from backtest results."""
        if not positions:
            # No trades executed
            return BacktestResult(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_return=0.0,
                total_return_pct=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
                avg_trade_duration=0.0,
                trades=positions,
                equity_curve=equity_curve,
                drawdown_curve=drawdown_curve,
                parameters=parameters,
            )
        
        # Calculate returns
        final_capital = equity_curve[-1]
        total_return = final_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Separate winning and losing trades
        winning_trades = [p for p in positions if p.pnl and p.pnl > 0]
        losing_trades = [p for p in positions if p.pnl and p.pnl <= 0]
        
        total_trades = len(positions)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0
        
        # Average win/loss
        avg_win = np.mean([p.pnl for p in winning_trades]) if winning_trades else 0.0
        avg_loss = abs(np.mean([p.pnl for p in losing_trades])) if losing_trades else 0.0
        
        # Profit factor
        total_profit = sum(p.pnl for p in winning_trades) if winning_trades else 0.0
        total_loss = abs(sum(p.pnl for p in losing_trades)) if losing_trades else 0.0
        profit_factor = total_profit / total_loss if total_loss > 0 else (float('inf') if total_profit > 0 else 0.0)
        
        # Sharpe ratio (simplified - using returns instead of excess returns)
        if len(equity_curve) > 1:
            returns = np.diff(equity_curve) / equity_curve[:-1]
            if len(returns) > 0 and np.std(returns) > 0:
                sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252)  # Annualized
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown
        max_drawdown = max(drawdown_curve) if drawdown_curve else 0.0
        max_drawdown_pct = max_drawdown
        
        # Average trade duration
        durations = []
        for p in positions:
            if p.exit_time:
                duration = (p.exit_time - p.entry_time).total_seconds() / 3600  # hours
                durations.append(duration)
        
        avg_trade_duration = np.mean(durations) if durations else 0.0
        
        return BacktestResult(
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            total_return=total_return,
            total_return_pct=total_return_pct,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown * self.initial_capital / 100,  # Convert % to absolute
            max_drawdown_pct=max_drawdown,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            avg_trade_duration=avg_trade_duration,
            trades=positions,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            parameters=parameters,
        )

