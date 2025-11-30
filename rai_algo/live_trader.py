"""
Live trading bot for RAI-ALGO framework.
Handles real-time data ingestion, signal evaluation, and trade execution.
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, field
import threading

from rai_algo.base import BaseStrategy
from rai_algo.exchange import BaseExchange, Order
from rai_algo.risk import RiskManager, RiskLimits
from rai_algo.data_types import MarketData, Signal, Position, SignalType


logger = logging.getLogger(__name__)


@dataclass
class TraderConfig:
    """Live trader configuration."""
    symbol: str
    strategy: BaseStrategy
    exchange: BaseExchange
    risk_limits: Optional[RiskLimits] = None
    data_interval: float = 1.0  # Seconds between data fetches
    heartbeat_interval: float = 30.0  # Seconds between heartbeat checks
    max_history_length: int = 1000
    enable_auto_trading: bool = True
    dry_run: bool = False  # If True, log orders but don't execute


class LiveTrader:
    """
    Live trading bot.
    
    Features:
    - Real-time market data ingestion
    - Signal evaluation loop
    - Trade execution
    - Position tracking
    - Risk management
    - Heartbeat monitoring
    - Comprehensive logging
    """
    
    def __init__(self, config: TraderConfig):
        """
        Initialize live trader.
        
        Args:
            config: Trader configuration
        """
        self.config = config
        self.strategy = config.strategy
        self.exchange = config.exchange
        self.symbol = config.symbol
        
        # Initialize risk manager
        initial_balance = self.exchange.get_balance().total
        self.risk_manager = RiskManager(
            initial_balance=initial_balance,
            risk_limits=config.risk_limits,
        )
        
        # State
        self.is_running = False
        self.is_paused = False
        self.positions: Dict[str, Position] = {}
        self.open_orders: Dict[str, Order] = {}
        self.market_data_history: List[MarketData] = []
        self.last_heartbeat: Optional[datetime] = None
        self.start_time: Optional[datetime] = None
        self.trade_count = 0
        
        # Threading
        self._main_loop_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Logging setup
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the trader."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f"trader_{self.strategy.name}_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(),
            ],
        )
    
    def start(self):
        """Start the live trading bot."""
        if self.is_running:
            logger.warning("Trader is already running")
            return
        
        logger.info(f"🚀 Starting live trader for {self.symbol} with strategy: {self.strategy.name}")
        logger.info(f"Exchange: {self.exchange.name}")
        logger.info(f"Dry run mode: {self.config.dry_run}")
        logger.info(f"Auto trading: {self.config.enable_auto_trading}")
        
        # Health check
        if not self.exchange.health_check():
            logger.error("❌ Exchange health check failed. Cannot start trader.")
            return
        
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
        
        logger.info("✅ Live trader started successfully")
    
    def stop(self):
        """Stop the live trading bot."""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping live trader...")
        self.is_running = False
        self._stop_event.set()
        
        # Wait for threads to finish
        if self._main_loop_thread:
            self._main_loop_thread.join(timeout=5.0)
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5.0)
        
        logger.info("✅ Live trader stopped")
    
    def pause(self):
        """Pause trading (stop executing new orders)."""
        self.is_paused = True
        logger.info("⏸️ Trading paused")
    
    def resume(self):
        """Resume trading."""
        self.is_paused = False
        logger.info("▶️ Trading resumed")
    
    def _main_loop(self):
        """Main trading loop."""
        logger.info("Main loop started")
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # Update positions
                self._update_positions()
                
                # Fetch market data
                market_data = self.exchange.get_market_data(self.symbol)
                # Store symbol in metadata if not present
                if not market_data.metadata:
                    market_data.metadata = {}
                market_data.metadata["symbol"] = self.symbol
                self._add_market_data(market_data)
                
                # Update risk manager balance
                balance = self.exchange.get_balance()
                self.risk_manager.update_balance(balance.total)
                
                # Check if trading is allowed
                if not self.is_paused and self.config.enable_auto_trading:
                    # Generate signal
                    current_position = self.positions.get(self.symbol)
                    signal = self.strategy.generate_signal(
                        market_data=market_data,
                        history=self.market_data_history,
                        current_position=current_position,
                    )
                    
                    # Validate and execute signal
                    if signal.signal_type != SignalType.HOLD:
                        self._process_signal(signal, market_data)
                
                # Update strategy state
                current_position = self.positions.get(self.symbol)
                if current_position:
                    signal = Signal(
                        signal_type=SignalType.HOLD,
                        symbol=self.symbol,
                        timestamp=datetime.now(),
                    )
                    self.strategy.update_state(market_data, signal)
                
                # Sleep
                time.sleep(self.config.data_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(self.config.data_interval)
    
    def _heartbeat_loop(self):
        """Heartbeat monitoring loop."""
        logger.info("Heartbeat monitor started")
        
        while self.is_running and not self._stop_event.is_set():
            try:
                now = datetime.now()
                time_since_heartbeat = (now - self.last_heartbeat).total_seconds() if self.last_heartbeat else 0
                
                # Check if heartbeat is stale (more than 2x interval)
                if time_since_heartbeat > self.config.heartbeat_interval * 2:
                    logger.warning(f"⚠️ Heartbeat stale: {time_since_heartbeat:.1f}s since last update")
                
                # Log status
                self._log_status()
                
                # Update heartbeat
                self.last_heartbeat = now
                
                time.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}", exc_info=True)
                time.sleep(self.config.heartbeat_interval)
    
    def _update_positions(self):
        """Update current positions from exchange."""
        try:
            position = self.exchange.get_position(self.symbol)
            if position:
                self.positions[self.symbol] = position
            elif self.symbol in self.positions:
                # Position was closed
                del self.positions[self.symbol]
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    def _add_market_data(self, market_data: MarketData):
        """Add market data to history."""
        self.market_data_history.append(market_data)
        
        # Trim history if too long
        if len(self.market_data_history) > self.config.max_history_length:
            self.market_data_history = self.market_data_history[-self.config.max_history_length:]
    
    def _process_signal(self, signal: Signal, market_data: MarketData):
        """Process a trading signal."""
        signal_type_str = signal.signal_type.value.upper()
        logger.info(f"📊 Signal received: {signal_type_str} for {self.symbol}")
        
        # Validate signal with risk manager
        is_valid, reason = self.risk_manager.validate_signal(signal, self.positions, self.symbol, market_data.price)
        
        if not is_valid:
            logger.warning(f"⚠️ Signal rejected: {reason}")
            return
        
        # Execute signal
        if signal.signal_type == SignalType.BUY:
            self._execute_buy(signal, market_data)
        elif signal.signal_type == SignalType.SELL:
            self._execute_sell(signal, market_data)
        elif signal.signal_type == SignalType.CLOSE:
            self._execute_close(signal, market_data)
    
    def _execute_buy(self, signal: Signal, market_data: MarketData):
        """Execute a buy order."""
        if self.symbol in self.positions:
            logger.warning(f"Position already exists for {self.symbol}. Skipping buy.")
            return
        
        try:
            # Determine quantity based on signal strength and risk limits
            balance = self.exchange.get_balance()
            price = signal.price
            max_position_value = balance.total * self.risk_manager.risk_limits.max_position_size
            # Use signal strength (0-1) to scale position size
            quantity = (max_position_value * signal.strength) / price if price > 0 else 0
            
            if quantity <= 0:
                logger.warning("Invalid quantity for buy order")
                return
            
            # Place order
            if self.config.dry_run:
                logger.info(f"🔵 [DRY RUN] BUY {quantity} {self.symbol} @ {signal.price or 'MARKET'}")
            else:
                order = self.exchange.place_order(
                    symbol=self.symbol,
                    side="BUY",
                    quantity=quantity,
                    order_type="MARKET" if signal.price is None else "LIMIT",
                    price=signal.price,
                )
                self.open_orders[order.order_id] = order
                self.risk_manager.record_order()
                logger.info(f"🔵 BUY order placed: {order.order_id} - {quantity} {self.symbol}")
                
        except Exception as e:
            logger.error(f"Error executing buy order: {e}", exc_info=True)
    
    def _execute_sell(self, signal: Signal, market_data: MarketData):
        """Execute a sell order."""
        if self.symbol not in self.positions:
            logger.warning(f"No position exists for {self.symbol}. Skipping sell.")
            return
        
        try:
            position = self.positions[self.symbol]
            # Use signal strength to determine partial close (1.0 = full close)
            quantity = position.size * signal.strength
            
            if quantity <= 0:
                logger.warning("Invalid quantity for sell order")
                return
            
            # Place order
            if self.config.dry_run:
                logger.info(f"🔴 [DRY RUN] SELL {quantity} {self.symbol} @ {signal.price or 'MARKET'}")
            else:
                order = self.exchange.place_order(
                    symbol=self.symbol,
                    side="SELL",
                    quantity=quantity,
                    order_type="MARKET" if signal.price is None else "LIMIT",
                    price=signal.price,
                )
                self.open_orders[order.order_id] = order
                self.risk_manager.record_order()
                logger.info(f"🔴 SELL order placed: {order.order_id} - {quantity} {self.symbol}")
                
        except Exception as e:
            logger.error(f"Error executing sell order: {e}", exc_info=True)
    
    def _execute_close(self, signal: Signal, market_data: MarketData):
        """Close an existing position."""
        if self.symbol not in self.positions:
            logger.warning(f"No position to close for {self.symbol}")
            return
        
        position = self.positions[self.symbol]
        close_side = "SELL" if position.signal_type == SignalType.BUY else "BUY"
        
        try:
            if self.config.dry_run:
                logger.info(f"🟡 [DRY RUN] CLOSE {position.size} {self.symbol} @ MARKET")
            else:
                order = self.exchange.place_order(
                    symbol=self.symbol,
                    side=close_side,
                    quantity=position.size,
                    order_type="MARKET",
                )
                self.open_orders[order.order_id] = order
                self.risk_manager.record_order()
                logger.info(f"🟡 CLOSE order placed: {order.order_id} - {position.size} {self.symbol}")
                
        except Exception as e:
            logger.error(f"Error closing position: {e}", exc_info=True)
    
    def _log_status(self):
        """Log current trader status."""
        balance = self.exchange.get_balance()
        risk_status = self.risk_manager.get_status()
        
        status = {
            "symbol": self.symbol,
            "balance": balance.total,
            "positions": len(self.positions),
            "open_orders": len(self.open_orders),
            "trades": self.trade_count,
            "uptime": str(datetime.now() - self.start_time) if self.start_time else "N/A",
            "risk_killed": risk_status["is_killed"],
            "daily_pnl": risk_status["daily_stats"]["total_pnl"] if risk_status["daily_stats"] else 0,
        }
        
        logger.info(f"💓 Heartbeat: {status}")
    
    def get_status(self) -> Dict:
        """Get current trader status."""
        balance = self.exchange.get_balance()
        risk_status = self.risk_manager.get_status()
        
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "symbol": self.symbol,
            "strategy": self.strategy.name,
            "exchange": self.exchange.name,
            "balance": balance.total,
            "positions": {sym: {
                "side": pos.signal_type.value,
                "size": pos.size,
                "entry_price": pos.entry_price,
                "current_price": pos.current_price if pos.current_price else pos.entry_price,
                "pnl": pos.pnl if not pos.is_open else None,
            } for sym, pos in self.positions.items()},
            "open_orders": len(self.open_orders),
            "trades": self.trade_count,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "risk_manager": risk_status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
        }

