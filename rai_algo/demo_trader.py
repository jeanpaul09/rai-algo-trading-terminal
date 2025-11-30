"""
Demo/Paper Trading Engine for RAI-ALGO Framework
Simulates trades without using real funds - tracks virtual positions, PnL, and trade history
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

from rai_algo.base import BaseStrategy
from rai_algo.exchange import BaseExchange, Order
from rai_algo.risk import RiskManager, RiskLimits
from rai_algo.data_types import MarketData, Signal, Position, SignalType

logger = logging.getLogger(__name__)


class TradeType(Enum):
    """Trade type for demo trading."""
    ENTRY = "entry"
    EXIT = "exit"
    TP = "tp"  # Take profit
    SL = "sl"  # Stop loss


@dataclass
class DemoTrade:
    """Represents a demo/paper trade."""
    id: str
    timestamp: datetime
    type: TradeType
    symbol: str
    strategy: str
    side: str  # "long" or "short"
    price: float
    size: float
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # For exit trades
    entry_price: Optional[float] = None
    entry_time: Optional[datetime] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None


@dataclass
class DemoPosition:
    """Virtual position for demo trading."""
    symbol: str
    side: str  # "long" or "short"
    entry_price: float
    entry_time: datetime
    size: float
    strategy: str
    
    # Stop loss / Take profit
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Current metrics
    current_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    
    def update_pnl(self, current_price: float):
        """Update unrealized PnL based on current price."""
        self.current_price = current_price
        if self.side == "long":
            self.unrealized_pnl = (current_price - self.entry_price) * self.size
        else:  # short
            self.unrealized_pnl = (self.entry_price - current_price) * self.size
        self.unrealized_pnl_pct = (self.unrealized_pnl / (self.entry_price * self.size)) * 100


@dataclass
class DemoTraderConfig:
    """Configuration for demo trader."""
    symbol: str
    strategy: BaseStrategy
    exchange: BaseExchange  # Used for market data only
    initial_capital: float = 10000.0
    risk_limits: Optional[RiskLimits] = None
    data_interval: float = 1.0
    heartbeat_interval: float = 30.0
    max_history_length: int = 1000
    enable_auto_trading: bool = True
    
    # Commission and slippage for realistic simulation
    commission_rate: float = 0.001  # 0.1%
    slippage_rate: float = 0.0005  # 0.05%


class DemoTrader:
    """
    Demo/Paper Trading Engine
    
    Simulates trading with virtual positions and capital.
    Tracks all trades, positions, and PnL for display in terminal.
    """
    
    def __init__(self, config: DemoTraderConfig):
        """Initialize demo trader."""
        self.config = config
        self.strategy = config.strategy
        self.exchange = config.exchange
        self.symbol = config.symbol
        
        # Virtual capital and positions
        self.virtual_capital = config.initial_capital
        self.virtual_cash = config.initial_capital
        self.positions: Dict[str, DemoPosition] = {}
        
        # Trade history
        self.trades: List[DemoTrade] = []
        self.equity_curve: List[Dict[str, Any]] = []
        
        # Market data history
        self.market_data_history: List[MarketData] = []
        
        # Risk manager (uses virtual capital)
        self.risk_manager = RiskManager(
            initial_balance=config.initial_capital,
            risk_limits=config.risk_limits or RiskLimits(),
        )
        
        # State
        self.is_running = False
        self.is_paused = False
        self.start_time: Optional[datetime] = None
        self.last_heartbeat: Optional[datetime] = None
        
        # Threading
        self._main_loop_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Callbacks for brain feed and annotations
        self.on_trade_callback: Optional[callable] = None
        self.on_brain_feed_callback: Optional[callable] = None
        
        logger.info(f"Demo trader initialized: {self.symbol}, initial capital: ${self.virtual_capital:,.2f}")
    
    def start(self):
        """Start the demo trading engine."""
        if self.is_running:
            logger.warning("Demo trader is already running")
            return
        
        logger.info(f"🚀 Starting demo trader for {self.symbol} with strategy: {self.strategy.name}")
        
        self.is_running = True
        self.start_time = datetime.now()
        self.last_heartbeat = datetime.now()
        self._stop_event.clear()
        
        # Start main loop
        self._main_loop_thread = threading.Thread(target=self._main_loop, daemon=True)
        self._main_loop_thread.start()
        
        # Start heartbeat monitor
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        
        logger.info("✅ Demo trader started successfully")
    
    def stop(self):
        """Stop the demo trading engine."""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping demo trader...")
        self.is_running = False
        self._stop_event.set()
        
        # Close all positions
        for symbol, position in list(self.positions.items()):
            self._close_position(symbol, "stopped", {})
        
        # Wait for threads
        if self._main_loop_thread:
            self._main_loop_thread.join(timeout=5.0)
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5.0)
        
        logger.info("✅ Demo trader stopped")
    
    def _main_loop(self):
        """Main trading loop."""
        logger.info("Demo trader main loop started")
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # Fetch market data
                market_data = self.exchange.get_market_data(self.symbol)
                if not market_data.metadata:
                    market_data.metadata = {}
                market_data.metadata["symbol"] = self.symbol
                
                self._add_market_data(market_data)
                
                # Update positions PnL
                self._update_positions_pnl(market_data.price)
                
                # Check stop loss / take profit
                self._check_exit_conditions(market_data)
                
                # Generate signal if trading is enabled
                if not self.is_paused and self.config.enable_auto_trading:
                    current_position = self.positions.get(self.symbol)
                    
                    signal = self.strategy.generate_signal(
                        market_data=market_data,
                        history=self.market_data_history,
                        current_position=current_position,
                    )
                    
                    # Process signal
                    if signal.signal_type != SignalType.HOLD:
                        self._process_signal(signal, market_data)
                
                # Update equity curve
                self._update_equity_curve(market_data.timestamp)
                
                # Sleep
                time.sleep(self.config.data_interval)
                
            except Exception as e:
                logger.error(f"Error in demo trader main loop: {e}", exc_info=True)
                time.sleep(self.config.data_interval)
    
    def _heartbeat_loop(self):
        """Heartbeat monitoring loop."""
        while self.is_running and not self._stop_event.is_set():
            try:
                self.last_heartbeat = datetime.now()
                time.sleep(self.config.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}", exc_info=True)
                time.sleep(self.config.heartbeat_interval)
    
    def _add_market_data(self, market_data: MarketData):
        """Add market data to history."""
        self.market_data_history.append(market_data)
        if len(self.market_data_history) > self.config.max_history_length:
            self.market_data_history.pop(0)
    
    def _update_positions_pnl(self, current_price: float):
        """Update unrealized PnL for all positions."""
        for position in self.positions.values():
            position.update_pnl(current_price)
    
    def _check_exit_conditions(self, market_data: MarketData):
        """Check stop loss and take profit conditions."""
        if self.symbol not in self.positions:
            return
        
        position = self.positions[self.symbol]
        current_price = market_data.price
        
        # Check stop loss
        if position.stop_loss:
            if position.side == "long" and current_price <= position.stop_loss:
                self._close_position(self.symbol, "stop_loss", {
                    "stop_loss": position.stop_loss,
                    "exit_price": current_price,
                })
                return
            elif position.side == "short" and current_price >= position.stop_loss:
                self._close_position(self.symbol, "stop_loss", {
                    "stop_loss": position.stop_loss,
                    "exit_price": current_price,
                })
                return
        
        # Check take profit
        if position.take_profit:
            if position.side == "long" and current_price >= position.take_profit:
                self._close_position(self.symbol, "take_profit", {
                    "take_profit": position.take_profit,
                    "exit_price": current_price,
                })
                return
            elif position.side == "short" and current_price <= position.take_profit:
                self._close_position(self.symbol, "take_profit", {
                    "take_profit": position.take_profit,
                    "exit_price": current_price,
                })
                return
    
    def _process_signal(self, signal: Signal, market_data: MarketData):
        """Process trading signal."""
        current_position = self.positions.get(self.symbol)
        
        # Entry signal
        if signal.signal_type == SignalType.LONG or signal.signal_type == SignalType.SHORT:
            if current_position:
                # Already in position, ignore entry signal
                return
            
            # Calculate position size
            risk_amount = self.virtual_capital * self.config.risk_limits.max_position_size
            position_size = risk_amount / market_data.price
            
            # Check if we have enough capital
            required_capital = position_size * market_data.price * (1 + self.config.commission_rate)
            if required_capital > self.virtual_cash:
                self._log_brain_feed("warning", f"Insufficient capital for entry: required ${required_capital:,.2f}, available ${self.virtual_cash:,.2f}")
                return
            
            # Open position
            self._open_position(signal, market_data, position_size)
        
        # Exit signal
        elif signal.signal_type == SignalType.EXIT:
            if current_position:
                self._close_position(self.symbol, "signal_exit", {
                    "signal": signal.signal_type.value,
                    "reason": signal.metadata.get("reason", "Strategy exit signal") if signal.metadata else "Strategy exit signal",
                })
    
    def _open_position(self, signal: Signal, market_data: MarketData, size: float):
        """Open a new position."""
        side = "long" if signal.signal_type == SignalType.LONG else "short"
        
        # Apply slippage
        entry_price = market_data.price * (1 + self.config.slippage_rate) if side == "long" else market_data.price * (1 - self.config.slippage_rate)
        
        # Calculate commission
        commission = size * entry_price * self.config.commission_rate
        
        # Update cash
        if side == "long":
            self.virtual_cash -= (size * entry_price + commission)
        else:  # short (for perps, we still need margin)
            self.virtual_cash -= (size * entry_price * 0.1 + commission)  # 10% margin
        
        # Get stop loss and take profit from signal metadata
        stop_loss = signal.metadata.get("stop_loss") if signal.metadata else None
        take_profit = signal.metadata.get("take_profit") if signal.metadata else None
        
        # Create position
        position = DemoPosition(
            symbol=self.symbol,
            side=side,
            entry_price=entry_price,
            entry_time=market_data.timestamp,
            size=size,
            strategy=self.strategy.name,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        
        self.positions[self.symbol] = position
        
        # Record trade
        trade = DemoTrade(
            id=f"demo_{len(self.trades)}_{int(datetime.now().timestamp())}",
            timestamp=market_data.timestamp,
            type=TradeType.ENTRY,
            symbol=self.symbol,
            strategy=self.strategy.name,
            side=side,
            price=entry_price,
            size=size,
            reason=signal.metadata.get("reason", f"{side.capitalize()} signal") if signal.metadata else f"{side.capitalize()} signal",
            metadata={
                "commission": commission,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
            },
        )
        
        self.trades.append(trade)
        
        # Log to brain feed
        reason_text = f"Opened {side} position: {size:.6f} @ ${entry_price:,.2f}"
        if stop_loss:
            reason_text += f" | SL: ${stop_loss:,.2f}"
        if take_profit:
            reason_text += f" | TP: ${take_profit:,.2f}"
        
        self._log_brain_feed("trade", reason_text, {
            "type": "entry",
            "side": side,
            "price": entry_price,
            "size": size,
        })
        
        # Callback
        if self.on_trade_callback:
            self.on_trade_callback(trade, "entry")
        
        logger.info(f"📈 Demo entry: {side} {size:.6f} {self.symbol} @ ${entry_price:,.2f}")
    
    def _close_position(self, symbol: str, reason: str, metadata: Dict[str, Any]):
        """Close an existing position."""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        market_data = self.market_data_history[-1] if self.market_data_history else None
        if not market_data:
            return
        
        # Apply slippage
        exit_price = market_data.price * (1 - self.config.slippage_rate) if position.side == "long" else market_data.price * (1 + self.config.slippage_rate)
        
        # Calculate commission
        commission = position.size * exit_price * self.config.commission_rate
        
        # Calculate PnL
        if position.side == "long":
            gross_pnl = (exit_price - position.entry_price) * position.size
        else:  # short
            gross_pnl = (position.entry_price - exit_price) * position.size
        
        net_pnl = gross_pnl - commission
        pnl_pct = (net_pnl / (position.entry_price * position.size)) * 100
        
        # Update cash
        if position.side == "long":
            self.virtual_cash += (position.size * exit_price - commission)
        else:  # short
            self.virtual_cash += (position.size * position.entry_price * 0.1 + net_pnl)
        
        # Update capital
        self.virtual_capital = self.virtual_cash + sum(p.size * (p.current_price or 0) for p in self.positions.values() if p != position)
        
        # Record trade
        trade_type = TradeType.SL if reason == "stop_loss" else TradeType.TP if reason == "take_profit" else TradeType.EXIT
        
        trade = DemoTrade(
            id=f"demo_{len(self.trades)}_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(),
            type=trade_type,
            symbol=symbol,
            strategy=position.strategy,
            side=position.side,
            price=exit_price,
            size=position.size,
            reason=reason,
            entry_price=position.entry_price,
            entry_time=position.entry_time,
            pnl=net_pnl,
            pnl_pct=pnl_pct,
            metadata={
                "commission": commission,
                "gross_pnl": gross_pnl,
                **metadata,
            },
        )
        
        self.trades.append(trade)
        
        # Log to brain feed
        pnl_sign = "+" if net_pnl >= 0 else ""
        reason_text = f"Closed {position.side} position: {position.size:.6f} @ ${exit_price:,.2f} | PnL: {pnl_sign}${net_pnl:,.2f} ({pnl_sign}{pnl_pct:.2f}%) | Reason: {reason}"
        
        self._log_brain_feed("trade", reason_text, {
            "type": "exit",
            "side": position.side,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "pnl": net_pnl,
            "pnl_pct": pnl_pct,
            "reason": reason,
        })
        
        # Callback
        if self.on_trade_callback:
            self.on_trade_callback(trade, "exit")
        
        # Remove position
        del self.positions[symbol]
        
        logger.info(f"📉 Demo exit: {position.side} {position.size:.6f} {symbol} @ ${exit_price:,.2f} | PnL: ${net_pnl:,.2f} ({pnl_pct:.2f}%)")
    
    def _update_equity_curve(self, timestamp: datetime):
        """Update equity curve."""
        total_equity = self.virtual_cash
        for position in self.positions.values():
            if position.current_price:
                if position.side == "long":
                    total_equity += position.size * position.current_price
                else:
                    total_equity += position.size * position.entry_price + position.unrealized_pnl
        
        self.equity_curve.append({
            "timestamp": timestamp.isoformat(),
            "equity": total_equity,
            "cash": self.virtual_cash,
            "positions_value": total_equity - self.virtual_cash,
        })
    
    def _log_brain_feed(self, entry_type: str, content: str, data: Optional[Dict[str, Any]] = None):
        """Log entry to brain feed."""
        if self.on_brain_feed_callback:
            self.on_brain_feed_callback({
                "type": entry_type,
                "content": content,
                "strategy": self.strategy.name,
                "timestamp": datetime.now().isoformat(),
                "data": data or {},
            })
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        total_equity = self.virtual_cash
        unrealized_pnl = 0.0
        
        for position in self.positions.values():
            if position.current_price:
                if position.side == "long":
                    total_equity += position.size * position.current_price
                else:
                    total_equity += position.size * position.entry_price + position.unrealized_pnl
                unrealized_pnl += position.unrealized_pnl
        
        realized_pnl = sum(t.pnl for t in self.trades if t.type in [TradeType.EXIT, TradeType.TP, TradeType.SL] and t.pnl)
        total_pnl = realized_pnl + unrealized_pnl
        
        return {
            "mode": "DEMO",
            "symbol": self.symbol,
            "strategy": self.strategy.name,
            "is_running": self.is_running,
            "virtual_capital": self.virtual_capital,
            "virtual_cash": self.virtual_cash,
            "total_equity": total_equity,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl": total_pnl,
            "open_positions": len(self.positions),
            "total_trades": len([t for t in self.trades if t.type == TradeType.EXIT or t.type == TradeType.TP or t.type == TradeType.SL]),
            "winning_trades": len([t for t in self.trades if t.pnl and t.pnl > 0]),
            "losing_trades": len([t for t in self.trades if t.pnl and t.pnl < 0]),
            "start_time": self.start_time.isoformat() if self.start_time else None,
        }
    
    def get_trades(self, limit: Optional[int] = None) -> List[DemoTrade]:
        """Get trade history."""
        trades = self.trades
        if limit:
            trades = trades[-limit:]
        return trades
    
    def get_chart_annotations(self) -> List[Dict[str, Any]]:
        """Get chart annotations from trades."""
        annotations = []
        
        for trade in self.trades:
            if trade.type == TradeType.ENTRY:
                annotations.append({
                    "id": trade.id,
                    "timestamp": int(trade.timestamp.timestamp()),
                    "type": "entry",
                    "price": trade.price,
                    "strategy": trade.strategy,
                    "label": f"{trade.side.upper()} @ ${trade.price:,.2f}",
                    "reason": trade.reason,
                    "color": "#10b981",  # Green for entry
                })
            elif trade.type in [TradeType.EXIT, TradeType.TP, TradeType.SL]:
                annotations.append({
                    "id": trade.id,
                    "timestamp": int(trade.timestamp.timestamp()),
                    "type": trade.type.value,
                    "price": trade.price,
                    "strategy": trade.strategy,
                    "label": f"EXIT @ ${trade.price:,.2f} (PnL: ${trade.pnl:,.2f})",
                    "reason": trade.reason,
                    "color": "#ef4444" if (trade.pnl and trade.pnl < 0) else "#10b981",
                    "pnl": trade.pnl,
                })
            
            # Add stop loss and take profit lines from metadata
            if trade.type == TradeType.ENTRY and trade.metadata:
                if trade.metadata.get("stop_loss"):
                    annotations.append({
                        "id": f"{trade.id}_sl",
                        "timestamp": int(trade.timestamp.timestamp()),
                        "type": "sl",
                        "price": trade.metadata["stop_loss"],
                        "strategy": trade.strategy,
                        "label": f"SL: ${trade.metadata['stop_loss']:,.2f}",
                        "color": "#f59e0b",  # Amber
                    })
                if trade.metadata.get("take_profit"):
                    annotations.append({
                        "id": f"{trade.id}_tp",
                        "timestamp": int(trade.timestamp.timestamp()),
                        "type": "tp",
                        "price": trade.metadata["take_profit"],
                        "strategy": trade.strategy,
                        "label": f"TP: ${trade.metadata['take_profit']:,.2f}",
                        "color": "#3b82f6",  # Blue
                    })
        
        return annotations

