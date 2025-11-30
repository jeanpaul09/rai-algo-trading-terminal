"""
Backtest Example for RAI-ALGO Strategies

This demonstrates how to run a backtest with a strategy.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import List

from rai_algo.base import MarketData, Signal, SignalType
from strategies.example_moving_average_cross import MovingAverageCrossStrategy


def generate_sample_data(
    symbol: str = "BTC/USD",
    days: int = 100,
    start_price: Decimal = Decimal("50000")
) -> List[MarketData]:
    """
    Generate sample market data for backtesting.
    
    Args:
        symbol: Trading symbol
        days: Number of days of data
        start_price: Starting price
        
    Returns:
        List of MarketData objects
    """
    import random
    
    data = []
    current_price = start_price
    base_time = datetime.now() - timedelta(days=days)
    
    for i in range(days * 24):  # Hourly data
        # Simple random walk with trend
        change_pct = Decimal(str(random.uniform(-0.02, 0.02)))
        current_price = current_price * (1 + change_pct)
        
        # Generate OHLC
        high = current_price * Decimal("1.01")
        low = current_price * Decimal("0.99")
        open_price = current_price * Decimal(str(random.uniform(0.995, 1.005)))
        close_price = current_price
        volume = Decimal(str(random.uniform(1000, 10000)))
        
        timestamp = base_time + timedelta(hours=i)
        
        data.append(MarketData(
            timestamp=timestamp,
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=volume,
            symbol=symbol
        ))
    
    return data


def run_backtest(
    strategy: MovingAverageCrossStrategy,
    market_data: List[MarketData]
) -> dict:
    """
    Run a backtest with the given strategy and market data.
    
    Args:
        strategy: Strategy instance
        market_data: Historical market data
        
    Returns:
        Backtest results dictionary
    """
    initial_capital = strategy.capital
    trades = []
    positions = {}
    
    for data_point in market_data:
        # Process market data and get signals
        signals = strategy.process_market_data(data_point)
        
        for signal in signals:
            if signal.signal_type == SignalType.BUY:
                # Calculate position size
                position_size = strategy.calculate_position_size(
                    signal,
                    strategy.capital
                )
                
                # Execute buy
                cost = position_size * signal.price
                if cost <= strategy.capital:
                    strategy.capital -= cost
                    positions[signal.symbol] = {
                        "size": position_size,
                        "entry_price": signal.price,
                        "entry_time": signal.timestamp,
                        "type": "long"
                    }
                    trades.append({
                        "type": "BUY",
                        "time": signal.timestamp,
                        "price": float(signal.price),
                        "size": float(position_size),
                        "reason": signal.reason
                    })
            
            elif signal.signal_type == SignalType.SELL:
                # For short selling (simplified)
                position_size = strategy.calculate_position_size(
                    signal,
                    strategy.capital
                )
                # In a real implementation, you'd handle margin/borrowing
                # For simplicity, we'll skip short selling in this example
                pass
            
            elif signal.signal_type == SignalType.CLOSE:
                # Close position
                if signal.symbol in positions:
                    pos = positions[signal.symbol]
                    if pos["type"] == "long":
                        proceeds = pos["size"] * signal.price
                        strategy.capital += proceeds
                        pnl = proceeds - (pos["size"] * pos["entry_price"])
                        
                        trades.append({
                            "type": "CLOSE",
                            "time": signal.timestamp,
                            "price": float(signal.price),
                            "size": float(pos["size"]),
                            "pnl": float(pnl),
                            "reason": signal.reason
                        })
                    
                    del positions[signal.symbol]
    
    # Close any remaining positions at final price
    final_price = market_data[-1].close
    for symbol, pos in positions.items():
        if pos["type"] == "long":
            proceeds = pos["size"] * final_price
            strategy.capital += proceeds
            pnl = proceeds - (pos["size"] * pos["entry_price"])
            trades.append({
                "type": "CLOSE",
                "time": market_data[-1].timestamp,
                "price": float(final_price),
                "size": float(pos["size"]),
                "pnl": float(pnl),
                "reason": "End of backtest"
            })
    
    # Calculate metrics
    total_pnl = strategy.capital - initial_capital
    total_return = (total_pnl / initial_capital) * 100
    
    winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
    losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
    
    win_rate = (len(winning_trades) / len([t for t in trades if "pnl" in t])) * 100 if trades else 0
    
    return {
        "initial_capital": float(initial_capital),
        "final_capital": float(strategy.capital),
        "total_pnl": float(total_pnl),
        "total_return_pct": float(total_return),
        "total_trades": len([t for t in trades if t["type"] in ["BUY", "SELL"]]),
        "win_rate": win_rate,
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "trades": trades,
        "strategy_state": strategy.get_strategy_state()
    }


def main():
    """Run example backtest."""
    print("=" * 60)
    print("RAI-ALGO Backtest Example")
    print("=" * 60)
    
    # Create strategy
    strategy = MovingAverageCrossStrategy(
        fast_period=10,
        slow_period=30,
        ma_type="SMA",
        initial_capital=Decimal("10000"),
        max_position_size=Decimal("0.2"),  # 20% max position
        stop_loss_pct=Decimal("0.02"),  # 2% stop loss
        take_profit_pct=Decimal("0.05")  # 5% take profit
    )
    
    # Generate sample data
    print("\nGenerating sample market data...")
    market_data = generate_sample_data("BTC/USD", days=30)
    print(f"Generated {len(market_data)} data points")
    
    # Run backtest
    print("\nRunning backtest...")
    results = run_backtest(strategy, market_data)
    
    # Print results
    print("\n" + "=" * 60)
    print("Backtest Results")
    print("=" * 60)
    print(f"Initial Capital: ${results['initial_capital']:,.2f}")
    print(f"Final Capital:   ${results['final_capital']:,.2f}")
    print(f"Total P&L:       ${results['total_pnl']:,.2f}")
    print(f"Total Return:    {results['total_return_pct']:.2f}%")
    print(f"Total Trades:    {results['total_trades']}")
    print(f"Win Rate:        {results['win_rate']:.2f}%")
    print(f"Winning Trades:  {results['winning_trades']}")
    print(f"Losing Trades:   {results['losing_trades']}")
    
    print("\n" + "=" * 60)
    print("Trade Log (first 10 trades)")
    print("=" * 60)
    for trade in results['trades'][:10]:
        pnl_str = f", P&L: ${trade.get('pnl', 0):,.2f}" if "pnl" in trade else ""
        print(f"{trade['time']} | {trade['type']:5s} | "
              f"Price: ${trade['price']:,.2f} | "
              f"Size: {trade['size']:.4f}{pnl_str}")
        print(f"  Reason: {trade['reason']}")


if __name__ == "__main__":
    main()


