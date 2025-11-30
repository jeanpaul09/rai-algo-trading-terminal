"""
Example: How to save and load backtest results for the dashboard

This shows how to store BacktestResult objects so the API server can load them.
"""

import json
from datetime import datetime
from pathlib import Path
from rai_algo import BacktestResult
from rai_algo.backtest import BacktestEngine


def save_backtest_result(
    result: BacktestResult,
    strategy_name: str,
    market: str,
    start_date: str,
    end_date: str,
    output_dir: Path = Path("backtest_results"),
):
    """
    Save a backtest result to disk for the API server to load.
    
    Args:
        result: BacktestResult from backtest engine
        strategy_name: Name of the strategy
        market: Market symbol (e.g., "BTC/USD")
        start_date: Start date string
        end_date: End date string
        output_dir: Directory to save results
    """
    output_dir.mkdir(exist_ok=True)
    
    # Generate unique ID
    exp_id = f"{strategy_name}_{market}_{start_date}_{end_date}".replace("/", "_").replace("-", "_")
    output_file = output_dir / f"{exp_id}.json"
    
    # Convert to dictionary
    data = {
        "id": exp_id,
        "strategy_name": strategy_name,
        "market": market,
        "start_date": start_date,
        "end_date": end_date,
        "timestamp": datetime.now().isoformat(),
        "sharpe_ratio": result.sharpe_ratio,
        "sortino_ratio": 0.0,  # TODO: Calculate if available
        "max_drawdown": result.max_drawdown,
        "max_drawdown_pct": result.max_drawdown_pct,
        "cagr": result.total_return_pct / 365 * 252,  # Approximate CAGR
        "win_rate": result.win_rate,
        "total_trades": result.total_trades,
        "total_return": result.total_return,
        "total_return_pct": result.total_return_pct,
        "profit_factor": result.profit_factor,
        "parameters": result.parameters,
        "equity_curve": result.equity_curve,
        "drawdown_curve": result.drawdown_curve,
    }
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Saved backtest result: {output_file}")
    return exp_id


def run_and_save_backtest(
    strategy,
    market_data,
    strategy_name: str,
    market: str,
    start_date: str,
    end_date: str,
):
    """
    Run a backtest and save the result.
    
    Example usage:
        from rai_algo.strategies.example_strategy import ExampleStrategy
        from rai_algo.backtest import BacktestEngine
        
        strategy = ExampleStrategy(parameters={"fast_period": 10, "slow_period": 30})
        engine = BacktestEngine(initial_capital=10000)
        
        # Run backtest (you'll need to implement this based on your backtest engine)
        result = engine.run(strategy, market_data)
        
        # Save result
        exp_id = run_and_save_backtest(
            strategy,
            market_data,
            "ExampleMAStrategy",
            "BTC/USD",
            "2024-01-01",
            "2024-03-31",
        )
    """
    # This is a placeholder - implement based on your backtest engine
    # engine = BacktestEngine(initial_capital=10000)
    # result = engine.run(strategy, market_data)
    # return save_backtest_result(result, strategy_name, market, start_date, end_date)
    pass


if __name__ == "__main__":
    print("This is an example file showing how to save backtest results.")
    print("See CONNECTING_REAL_DATA.md for integration instructions.")


