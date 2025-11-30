#!/usr/bin/env python3
"""
Example live trading bot using RAI-ALGO framework.

This bot demonstrates how to:
1. Initialize a strategy
2. Connect to an exchange
3. Configure risk management
4. Start live trading

Usage:
    python live/example_strategy_bot.py

Environment variables required:
    See DEPLOYMENT.md for full list
"""
import os
import sys
import signal
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rai_algo.live_trader import LiveTrader, TraderConfig
from rai_algo.risk import RiskLimits
from rai_algo.strategies.example_strategy import ExampleStrategy
from rai_algo.exchanges.binance import BinanceExchange


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the trading bot."""
    # Configuration
    SYMBOL = os.getenv("TRADING_SYMBOL", "BTC/USDT")
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
    ENABLE_AUTO_TRADING = os.getenv("ENABLE_AUTO_TRADING", "true").lower() == "true"
    
    # Strategy parameters
    strategy_params = {
        "fast_period": int(os.getenv("FAST_MA_PERIOD", "10")),
        "slow_period": int(os.getenv("SLOW_MA_PERIOD", "30")),
        "stop_loss": float(os.getenv("STOP_LOSS", "0.02")),
        "take_profit": float(os.getenv("TAKE_PROFIT", "0.05")),
    }
    
    # Risk limits
    risk_limits = RiskLimits(
        max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "0.05")),
        max_position_size=float(os.getenv("MAX_POSITION_SIZE", "0.10")),
        max_total_exposure=float(os.getenv("MAX_TOTAL_EXPOSURE", "0.50")),
        max_drawdown=float(os.getenv("MAX_DRAWDOWN", "0.15")),
        max_orders_per_day=int(os.getenv("MAX_ORDERS_PER_DAY", "100")),
        max_orders_per_hour=int(os.getenv("MAX_ORDERS_PER_HOUR", "20")),
    )
    
    # Initialize components
    logger.info("Initializing trading bot...")
    
    # Strategy
    strategy = ExampleStrategy(parameters=strategy_params)
    logger.info(f"Strategy: {strategy.name} with params: {strategy_params}")
    
    # Exchange
    exchange = BinanceExchange()
    logger.info(f"Exchange: {exchange.name}")
    
    # Trader config
    config = TraderConfig(
        symbol=SYMBOL,
        strategy=strategy,
        exchange=exchange,
        risk_limits=risk_limits,
        data_interval=float(os.getenv("DATA_INTERVAL", "1.0")),
        heartbeat_interval=float(os.getenv("HEARTBEAT_INTERVAL", "30.0")),
        enable_auto_trading=ENABLE_AUTO_TRADING,
        dry_run=DRY_RUN,
    )
    
    # Create trader
    trader = LiveTrader(config=config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received. Stopping trader...")
        trader.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start trading
    try:
        trader.start()
        
        # Keep running
        logger.info("Trading bot is running. Press Ctrl+C to stop.")
        while trader.is_running:
            import time
            time.sleep(1)
            
            # Print status every 5 minutes
            status = trader.get_status()
            if status.get("trades", 0) > 0:
                logger.info(f"Status: {status}")
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        trader.stop()
        logger.info("Trading bot stopped.")


if __name__ == "__main__":
    main()


