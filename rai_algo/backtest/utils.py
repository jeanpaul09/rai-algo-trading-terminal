"""
Example usage and helper functions for backtesting.
"""
import logging
from typing import Callable, Dict, Any, Union, Optional
from datetime import datetime, timedelta

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from rai_algo.backtest.core import BacktestEngine, FixedFeeModel, FixedSlippageModel
from rai_algo.backtest.metrics import evaluate_performance, calculate_win_rate

logger = logging.getLogger(__name__)


def simple_sma_crossover_strategy(
    data_slice: pd.DataFrame,
    current_index: int,
    state: Dict[str, Any],
) -> float:
    """
    Simple moving average crossover strategy example.
    
    Strategy logic:
    - Calculate SMA(20) and SMA(50)
    - Go long when SMA(20) crosses above SMA(50)
    - Go short when SMA(20) crosses below SMA(50)
    - Otherwise hold current position
    
    Args:
        data_slice: DataFrame with historical data up to current bar
        current_index: Current bar index
        state: Strategy state dictionary (persists across bars)
        
    Returns:
        Position signal: 1.0 for long, -1.0 for short, 0.0 for no position
    """
    if len(data_slice) < 50:
        # Not enough data
        return 0.0
    
    # Calculate SMAs
    sma_20 = data_slice['close'].rolling(window=20).mean()
    sma_50 = data_slice['close'].rolling(window=50).mean()
    
    # Get current and previous values
    if current_index < 1:
        return 0.0
    
    current_sma20 = sma_20.iloc[current_index]
    current_sma50 = sma_50.iloc[current_index]
    prev_sma20 = sma_20.iloc[current_index - 1]
    prev_sma50 = sma_50.iloc[current_index - 1]
    
    # Check for crossover
    if pd.isna(current_sma20) or pd.isna(current_sma50):
        return 0.0
    
    # Bullish crossover: SMA20 crosses above SMA50
    if prev_sma20 <= prev_sma50 and current_sma20 > current_sma50:
        return 1.0  # Go long
    
    # Bearish crossover: SMA20 crosses below SMA50
    if prev_sma20 >= prev_sma50 and current_sma20 < current_sma50:
        return -1.0  # Go short
    
    # Hold current position (you could track this in state)
    if 'last_signal' in state:
        return state['last_signal']
    
    return 0.0


def run_example_backtest(
    data_source: str = "mock",
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    days: int = 30,
    initial_capital: float = 10000.0,
    strategy: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Run an example backtest with sample data.
    
    Args:
        data_source: Data source ('mock', 'crypto', 'stocks')
        symbol: Trading symbol
        timeframe: Timeframe
        days: Number of days of data
        initial_capital: Starting capital
        strategy: Strategy function (defaults to SMA crossover)
        
    Returns:
        Dictionary with backtest results and metrics
    """
    logger.info(f"Running example backtest: {symbol} on {data_source}")
    
    # Load or generate data
    if data_source == "mock":
        # Generate mock data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        dates = pd.date_range(start=start_date, end=end_date, freq=timeframe)
        n = len(dates)
        
        # Generate random walk price data
        import numpy as np
        np.random.seed(42)
        price = 100.0
        prices = [price]
        for _ in range(n - 1):
            price += np.random.randn() * 0.5
            prices.append(max(price, 1.0))  # Ensure positive prices
        
        # Create OHLCV data
        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.randn() * 0.01)) for p in prices],
            'low': [p * (1 - abs(np.random.randn() * 0.01)) for p in prices],
            'close': prices,
            'volume': [1000.0 + np.random.randn() * 100 for _ in range(n)],
        })
    else:
        # Load real data
        from rai_algo.data.loaders import load_data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = load_data(
            source=data_source,
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            use_cache=True,
        )
    
    # Use default strategy if none provided
    if strategy is None:
        strategy = simple_sma_crossover_strategy
    
    # Initialize backtest engine
    engine = BacktestEngine(
        initial_capital=initial_capital,
        fee_model=FixedFeeModel(0.001),  # 0.1% fee
        slippage_model=FixedSlippageModel(0.0005),  # 0.05% slippage
    )
    
    # Run backtest
    results = engine.run(
        price_data=data,
        strategy=strategy,
        initial_capital=initial_capital,
        verbose=False,
    )
    
    # Calculate metrics
    equity_curve = results['equity_curve']
    metrics = evaluate_performance(
        equity_curve,
        risk_free_rate=0.02,
        periods_per_year=252 if timeframe.endswith('d') else 365,
    )
    
    # Add trade statistics
    trade_stats = calculate_win_rate(results['trades'])
    metrics.update(trade_stats)
    
    # Print results
    print("\n" + "="*60)
    print("BACKTEST RESULTS")
    print("="*60)
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Period: {days} days")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Value: ${results['cash']:,.2f}")
    print(f"\nPerformance Metrics:")
    print(f"  Total Return: {metrics['total_return_pct']:.2f}%")
    print(f"  CAGR: {metrics['cagr_pct']:.2f}%")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
    print(f"  Sortino Ratio: {metrics['sortino_ratio']:.4f}")
    print(f"  Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
    print(f"\nTrade Statistics:")
    print(f"  Total Trades: {metrics['total_trades']}")
    print(f"  Winning Trades: {metrics['winning_trades']}")
    print(f"  Losing Trades: {metrics['losing_trades']}")
    print(f"  Win Rate: {metrics['win_rate_pct']:.2f}%")
    print(f"  Avg Win: ${metrics['avg_win']:.2f}")
    print(f"  Avg Loss: ${metrics['avg_loss']:.2f}")
    print(f"  Profit Factor: {metrics['profit_factor']:.4f}")
    print("="*60 + "\n")
    
    return {
        'results': results,
        'metrics': metrics,
        'data': data,
    }


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    run_example_backtest(
        data_source="mock",
        symbol="BTC/USDT",
        timeframe="1h",
        days=30,
        initial_capital=10000.0,
    )

