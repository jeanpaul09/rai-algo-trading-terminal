"""
Demo script for AGENT 4 — STRATEGY OPTIMIZER

This demonstrates how to use Agent4StrategyOptimizer to:
1. Backtest a strategy
2. Identify weaknesses
3. Optimize parameters
4. Get recommendations
"""
import json
from datetime import datetime, timedelta
import numpy as np

from rai_algo.agent4_optimizer import Agent4StrategyOptimizer
from rai_algo.strategies import MovingAverageCrossoverStrategy, TrendFollowingStrategy
from rai_algo.data_types import MarketData


def generate_sample_data(
    start_price: float = 100.0,
    days: int = 365,
    volatility: float = 0.02,
    trend: float = 0.0,
) -> list[MarketData]:
    """
    Generate sample market data for backtesting.
    
    Args:
        start_price: Starting price
        days: Number of days of data
        volatility: Daily volatility (std dev of returns)
        trend: Daily trend (drift)
    
    Returns:
        List of MarketData points
    """
    np.random.seed(42)  # For reproducibility
    
    data = []
    price = start_price
    start_date = datetime(2023, 1, 1)
    
    for i in range(days):
        # Generate OHLCV
        daily_return = np.random.normal(trend, volatility)
        open_price = price
        
        # Intraday high/low
        intraday_range = abs(np.random.normal(0, volatility * 0.5))
        high = open_price * (1 + abs(intraday_range))
        low = open_price * (1 - abs(intraday_range))
        
        close_price = open_price * (1 + daily_return)
        # Ensure close is within high/low
        close_price = max(low, min(high, close_price))
        
        volume = np.random.uniform(1000000, 5000000)
        
        timestamp = start_date + timedelta(days=i)
        
        data.append(MarketData(
            timestamp=timestamp,
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=volume,
        ))
        
        price = close_price
    
    return data


def main():
    """Run AGENT 4 optimization demo."""
    print("="*70)
    print("AGENT 4 — STRATEGY OPTIMIZER DEMO")
    print("="*70)
    
    # Generate sample market data
    print("\nGenerating sample market data...")
    market_data = generate_sample_data(
        start_price=100.0,
        days=365,
        volatility=0.02,
        trend=0.0001,  # Slight upward trend
    )
    print(f"Generated {len(market_data)} data points")
    print(f"Price range: ${min(d.close for d in market_data):.2f} - ${max(d.close for d in market_data):.2f}")
    
    # Initialize AGENT 4
    agent4 = Agent4StrategyOptimizer(
        initial_capital=10000.0,
        commission=0.001,  # 0.1%
        slippage=0.0005,  # 0.05%
    )
    
    # Test with Moving Average Crossover Strategy
    print("\n" + "="*70)
    print("TESTING: Moving Average Crossover Strategy")
    print("="*70)
    
    original_params = {
        'ma_fast': 10,
        'ma_slow': 30,
        'stop_loss_pct': 0.02,  # 2%
        'take_profit_pct': 0.05,  # 5%
    }
    
    # Run optimization
    result = agent4.optimize_strategy(
        strategy_class=MovingAverageCrossoverStrategy,
        market_data=market_data,
        original_parameters=original_params,
        strategy_name="MA_Crossover",
        verbose=True,
    )
    
    # Print formatted output
    print("\n" + "="*70)
    print("OPTIMIZATION RESULTS (JSON FORMAT)")
    print("="*70)
    print(json.dumps(result, indent=2, default=str))
    
    # Test with Trend Following Strategy
    print("\n" + "="*70)
    print("TESTING: Trend Following Strategy")
    print("="*70)
    
    original_params_tf = {
        'ma_period': 20,
        'volatility_period': 20,
        'volatility_threshold': 0.02,
        'trend_strength_threshold': 0.01,
        'stop_loss_pct': 0.03,
        'take_profit_pct': 0.06,
    }
    
    # Custom parameter grid for trend following
    parameter_grid = {
        'stop_loss_pct': [0.02, 0.03, 0.04, 0.05],
        'take_profit_pct': [0.04, 0.06, 0.08, 0.10],
        'volatility_threshold': [0.015, 0.02, 0.025],
        'trend_strength_threshold': [0.005, 0.01, 0.015],
    }
    
    result_tf = agent4.optimize_strategy(
        strategy_class=TrendFollowingStrategy,
        market_data=market_data,
        original_parameters=original_params_tf,
        strategy_name="TrendFollowing",
        parameter_grid=parameter_grid,
        verbose=True,
    )
    
    print("\n" + "="*70)
    print("TREND FOLLOWING OPTIMIZATION RESULTS")
    print("="*70)
    print(json.dumps(result_tf, indent=2, default=str))
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

