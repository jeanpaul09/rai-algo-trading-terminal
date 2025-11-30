"""
RAI-ALGO API Server - Implementation with Real Data
This shows how to connect the API server to actual RAI-ALGO modules
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
import importlib
import inspect
from pathlib import Path

# Import RAI-ALGO modules
from rai_algo import BaseStrategy, BacktestResult
from rai_algo.live_trader import LiveTrader
from rai_algo.data_types import BacktestResult as BacktestResultType

app = FastAPI(title="RAI-ALGO API", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use a proper state management solution)
_strategies_cache: List[Dict[str, Any]] = []
_backtest_results: Dict[str, BacktestResultType] = {}
_live_traders: Dict[str, LiveTrader] = {}


def discover_strategies() -> List[Dict[str, Any]]:
    """
    Discover all available strategies from:
    1. Python files in rai_algo/strategies/
    2. Blueprint JSON files in blueprints/
    """
    strategies = []
    
    # 1. Load from Python strategy files
    strategies_dir = Path("rai_algo/strategies")
    if strategies_dir.exists():
        for file in strategies_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue
            
            try:
                module_name = f"rai_algo.strategies.{file.stem}"
                module = importlib.import_module(module_name)
                
                # Find all BaseStrategy subclasses
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseStrategy) and 
                        obj != BaseStrategy):
                        
                        # Get default parameters
                        try:
                            instance = obj(parameters={})
                            params = instance.parameters
                        except:
                            params = {}
                        
                        strategies.append({
                            "name": obj.__name__,
                            "description": obj.__doc__ or "",
                            "module": module_name,
                            "class": name,
                            "parameters": params,
                            "source": "python",
                        })
            except Exception as e:
                print(f"Error loading strategy from {file}: {e}")
    
    # 2. Load from blueprint files
    blueprints_dir = Path("blueprints")
    if blueprints_dir.exists():
        for file in blueprints_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    blueprint = json.load(f)
                    
                    strategies.append({
                        "name": blueprint.get("name", file.stem),
                        "description": blueprint.get("description", ""),
                        "parameters": blueprint.get("parameters", {}),
                        "source": "blueprint",
                        "blueprint_file": str(file),
                    })
            except Exception as e:
                print(f"Error loading blueprint {file}: {e}")
    
    return strategies


def load_backtest_results() -> Dict[str, BacktestResultType]:
    """
    Load backtest results from storage.
    
    For now, this is a placeholder. You should implement:
    - Loading from JSON files in a results/ directory
    - Or loading from a database
    - Or keeping results in memory after running backtests
    """
    # TODO: Implement actual loading
    # Example: Load from results/ directory
    results_dir = Path("backtest_results")
    if not results_dir.exists():
        return {}
    
    results = {}
    for file in results_dir.glob("*.json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                # Reconstruct BacktestResult from JSON
                # (You'll need to implement serialization/deserialization)
                results[file.stem] = data
        except Exception as e:
            print(f"Error loading backtest result {file}: {e}")
    
    return results


def get_live_traders() -> Dict[str, LiveTrader]:
    """
    Get all active LiveTrader instances.
    
    In a real implementation, you might:
    - Track traders in a global registry
    - Load from a process manager
    - Query from a database
    """
    # TODO: Implement actual trader tracking
    return _live_traders


@app.on_event("startup")
async def startup_event():
    """Load data on startup."""
    global _strategies_cache, _backtest_results
    _strategies_cache = discover_strategies()
    _backtest_results = load_backtest_results()
    print(f"✅ Loaded {len(_strategies_cache)} strategies")
    print(f"✅ Loaded {len(_backtest_results)} backtest results")


@app.get("/")
async def root():
    return {
        "message": "RAI-ALGO API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "strategies_count": len(_strategies_cache),
        "backtests_count": len(_backtest_results),
    }


@app.get("/api/overview")
async def get_overview():
    """Get dashboard overview data."""
    strategies = _strategies_cache
    
    # Calculate aggregate metrics
    total_strategies = len(strategies)
    deployed_strategies = len([s for s in strategies if s.get("state") == "deployed"])
    
    # Get best/worst metrics from backtest results
    best_sharpe = 0.0
    worst_drawdown = 0.0
    latest_equity_curve = []
    
    if _backtest_results:
        sharpe_ratios = []
        drawdowns = []
        
        for result in _backtest_results.values():
            if isinstance(result, dict):
                sharpe = result.get("sharpe_ratio", 0)
                dd = result.get("max_drawdown_pct", 0)
                sharpe_ratios.append(sharpe)
                drawdowns.append(dd)
                
                # Get latest equity curve
                equity = result.get("equity_curve", [])
                if equity and len(equity) > len(latest_equity_curve):
                    latest_equity_curve = equity
        
        best_sharpe = max(sharpe_ratios) if sharpe_ratios else 0.0
        worst_drawdown = min(drawdowns) if drawdowns else 0.0
    
    # Get daily PnL from live traders
    daily_pnl = 0.0
    traders = get_live_traders()
    for trader in traders.values():
        status = trader.get_status()
        daily_pnl += status.get("risk_manager", {}).get("daily_stats", {}).get("total_pnl", 0.0)
    
    # Format equity curve for dashboard
    equity_points = []
    if latest_equity_curve:
        start_date = datetime.now() - timedelta(days=len(latest_equity_curve))
        for i, equity in enumerate(latest_equity_curve):
            equity_points.append({
                "timestamp": (start_date + timedelta(days=i)).isoformat(),
                "equity": equity,
            })
    
    return {
        "total_strategies": total_strategies,
        "deployed_strategies": deployed_strategies,
        "best_sharpe": best_sharpe,
        "worst_drawdown": worst_drawdown,
        "latest_equity_curve": equity_points,
        "daily_pnl": daily_pnl,
    }


@app.get("/api/strategies")
async def get_strategies():
    """List all strategies."""
    result = []
    
    for strategy in _strategies_cache:
        # Get best metrics from backtests for this strategy
        strategy_backtests = [
            r for r in _backtest_results.values()
            if isinstance(r, dict) and r.get("strategy_name") == strategy["name"]
        ]
        
        best_sharpe = 0.0
        worst_drawdown = 0.0
        
        if strategy_backtests:
            sharpe_ratios = [r.get("sharpe_ratio", 0) for r in strategy_backtests]
            drawdowns = [r.get("max_drawdown_pct", 0) for r in strategy_backtests]
            best_sharpe = max(sharpe_ratios) if sharpe_ratios else 0.0
            worst_drawdown = min(drawdowns) if drawdowns else 0.0
        
        result.append({
            "name": strategy["name"],
            "description": strategy.get("description", ""),
            "markets": strategy.get("markets", []),  # TODO: Extract from strategy
            "state": strategy.get("state", "experimental"),
            "tags": strategy.get("tags", []),  # TODO: Extract from strategy
            "best_sharpe": best_sharpe,
            "worst_drawdown": worst_drawdown,
        })
    
    return result


@app.get("/api/strategies/{name}")
async def get_strategy(name: str):
    """Get strategy details by name."""
    strategy = next((s for s in _strategies_cache if s["name"] == name), None)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Get latest metrics from backtests
    strategy_backtests = [
        r for r in _backtest_results.values()
        if isinstance(r, dict) and r.get("strategy_name") == name
    ]
    
    latest_metrics = None
    if strategy_backtests:
        latest = max(strategy_backtests, key=lambda x: x.get("timestamp", ""))
        latest_metrics = {
            "sharpe": latest.get("sharpe_ratio", 0),
            "sortino": latest.get("sortino_ratio", 0),  # TODO: Calculate if not present
            "max_drawdown": latest.get("max_drawdown_pct", 0),
            "cagr": latest.get("cagr", 0),  # TODO: Calculate if not present
            "hit_rate": latest.get("win_rate", 0),
            "win_rate": latest.get("win_rate", 0),
        }
    
    return {
        "name": strategy["name"],
        "description": strategy.get("description", ""),
        "markets": strategy.get("markets", []),
        "state": strategy.get("state", "experimental"),
        "tags": strategy.get("tags", []),
        "best_sharpe": latest_metrics["sharpe"] if latest_metrics else 0.0,
        "worst_drawdown": latest_metrics["max_drawdown"] if latest_metrics else 0.0,
        "latest_metrics": latest_metrics,
    }


@app.get("/api/strategies/{name}/experiments")
async def get_strategy_experiments(name: str):
    """Get experiments for a strategy."""
    experiments = []
    
    for exp_id, result in _backtest_results.items():
        if isinstance(result, dict) and result.get("strategy_name") == name:
            experiments.append({
                "id": exp_id,
                "strategy_name": name,
                "market": result.get("market", "Unknown"),
                "start_date": result.get("start_date", ""),
                "end_date": result.get("end_date", ""),
                "status": "completed",
                "parameters": result.get("parameters", {}),
                "metrics": {
                    "sharpe": result.get("sharpe_ratio", 0),
                    "sortino": result.get("sortino_ratio", 0),
                    "max_drawdown": result.get("max_drawdown_pct", 0),
                    "cagr": result.get("cagr", 0),
                    "hit_rate": result.get("win_rate", 0),
                    "win_rate": result.get("win_rate", 0),
                },
            })
    
    return experiments


@app.get("/api/experiments")
async def get_experiments():
    """List all experiments/backtests."""
    experiments = []
    
    for exp_id, result in _backtest_results.items():
        if isinstance(result, dict):
            experiments.append({
                "id": exp_id,
                "strategy_name": result.get("strategy_name", "Unknown"),
                "market": result.get("market", "Unknown"),
                "start_date": result.get("start_date", ""),
                "end_date": result.get("end_date", ""),
                "status": "completed",
                "parameters": result.get("parameters", {}),
                "metrics": {
                    "sharpe": result.get("sharpe_ratio", 0),
                    "sortino": result.get("sortino_ratio", 0),
                    "max_drawdown": result.get("max_drawdown_pct", 0),
                    "cagr": result.get("cagr", 0),
                    "hit_rate": result.get("win_rate", 0),
                    "win_rate": result.get("win_rate", 0),
                },
            })
    
    return experiments


@app.get("/api/experiments/{id}")
async def get_experiment(id: str):
    """Get experiment details by ID."""
    result = _backtest_results.get(id)
    
    if not result or not isinstance(result, dict):
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Format equity curve
    equity_curve = []
    if "equity_curve" in result:
        start_date = datetime.fromisoformat(result.get("start_date", datetime.now().isoformat()))
        for i, equity in enumerate(result["equity_curve"]):
            equity_curve.append({
                "timestamp": (start_date + timedelta(days=i)).isoformat(),
                "equity": equity,
            })
    
    # Format drawdown curve
    drawdown_curve = []
    if "drawdown_curve" in result:
        start_date = datetime.fromisoformat(result.get("start_date", datetime.now().isoformat()))
        for i, drawdown in enumerate(result["drawdown_curve"]):
            drawdown_curve.append({
                "timestamp": (start_date + timedelta(days=i)).isoformat(),
                "drawdown": drawdown,
            })
    
    return {
        "id": id,
        "strategy_name": result.get("strategy_name", "Unknown"),
        "market": result.get("market", "Unknown"),
        "start_date": result.get("start_date", ""),
        "end_date": result.get("end_date", ""),
        "status": "completed",
        "parameters": result.get("parameters", {}),
        "metrics": {
            "sharpe": result.get("sharpe_ratio", 0),
            "sortino": result.get("sortino_ratio", 0),
            "max_drawdown": result.get("max_drawdown_pct", 0),
            "cagr": result.get("cagr", 0),
            "hit_rate": result.get("win_rate", 0),
            "win_rate": result.get("win_rate", 0),
        },
        "equity_curve": equity_curve,
        "drawdown_curve": drawdown_curve,
        "return_distribution": result.get("return_distribution", []),
    }


@app.get("/api/live/status")
async def get_live_status():
    """Get live trading status."""
    traders = get_live_traders()
    
    if not traders:
        return {
            "equity": 0.0,
            "daily_pnl": 0.0,
            "total_exposure": 0.0,
            "max_exposure": 0.0,
            "current_drawdown": 0.0,
            "max_drawdown_allowed": -0.15,
            "risk_status": "OK",
            "positions": [],
            "venue_overview": [],
        }
    
    # Aggregate data from all traders
    total_equity = 0.0
    total_daily_pnl = 0.0
    total_exposure = 0.0
    all_positions = []
    venue_overview = {}
    
    for trader_name, trader in traders.items():
        status = trader.get_status()
        balance = status.get("balance", 0.0)
        total_equity += balance
        
        # Get daily PnL
        risk_mgr = status.get("risk_manager", {})
        daily_stats = risk_mgr.get("daily_stats", {})
        total_daily_pnl += daily_stats.get("total_pnl", 0.0)
        
        # Get positions
        positions = status.get("positions", {})
        for symbol, pos in positions.items():
            all_positions.append({
                "exchange": status.get("exchange", "Unknown"),
                "symbol": symbol,
                "side": pos.get("side", "long"),
                "size": pos.get("size", 0),
                "entry_price": pos.get("entry_price", 0),
                "mark_price": pos.get("current_price", pos.get("entry_price", 0)),
                "unrealized_pnl": pos.get("pnl", 0),
            })
            
            # Calculate exposure
            exposure = pos.get("size", 0) * pos.get("entry_price", 0)
            total_exposure += exposure
            
            # Venue overview
            exchange = status.get("exchange", "Unknown")
            if exchange not in venue_overview:
                venue_overview[exchange] = {
                    "venue": exchange,
                    "notional_exposure": 0.0,
                    "pnl": 0.0,
                }
            venue_overview[exchange]["notional_exposure"] += exposure
            venue_overview[exchange]["pnl"] += pos.get("pnl", 0.0)
    
    # Calculate drawdown (simplified)
    current_drawdown = 0.0
    risk_status = "OK"
    
    return {
        "equity": total_equity,
        "daily_pnl": total_daily_pnl,
        "total_exposure": total_exposure,
        "max_exposure": total_exposure * 2,  # TODO: Get from risk limits
        "current_drawdown": current_drawdown,
        "max_drawdown_allowed": -0.15,
        "risk_status": risk_status,
        "positions": all_positions,
        "venue_overview": list(venue_overview.values()),
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RAI-ALGO API Server (with real data)...")
    print("📊 Dashboard: http://localhost:3001")
    print("🔌 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)


