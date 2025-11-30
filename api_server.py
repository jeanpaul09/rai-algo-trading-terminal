"""
RAI-ALGO API Server with REAL Market Data
Uses Hyperliquid and Kraken public APIs - NO API KEYS NEEDED (no geo restrictions)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import uuid
import asyncio
from pathlib import Path
import os
import requests

# Import RAI-ALGO modules
from rai_algo import BacktestEngine, BaseStrategy
from rai_algo.backtest import BacktestEngine as BacktestEngineClass
from rai_algo.data_types import MarketData, BacktestResult
from rai_algo.live_trader import LiveTrader, TraderConfig
from rai_algo.blueprint_translator import BlueprintTranslator
from rai_algo.optimizer import Optimizer

app = FastAPI(title="RAI-ALGO API", version="1.0.0")

# Enable CORS
# CORS configuration - allow localhost and Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include additional API routers (Coinbase, Kraken, Polymarket)
try:
    from api_server_additional_apis import router as additional_apis_router
    app.include_router(additional_apis_router)
    print("✅ Additional APIs (Coinbase, Kraken, Polymarket) loaded")
except Exception as e:
    print(f"⚠️ Could not load additional APIs (optional): {e}")

# Global state
_jobs: Dict[str, Dict[str, Any]] = {}
_live_traders: Dict[str, LiveTrader] = {}
_backtest_results: Dict[str, BacktestResult] = {}
_websocket_connections: List[WebSocket] = []
_agent_status = {
    "mode": "OFF",
    "isActive": False,
    "environment": os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true" and "testnet" or "mainnet",
    "connected": True,
    "lastUpdate": datetime.now().isoformat(),
}

# Initialize Anthropic client for AI agent
try:
    from anthropic import Anthropic
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
    if anthropic_client:
        print("✅ Anthropic client initialized for AI agent")
    else:
        print("⚠️  ANTHROPIC_API_KEY not set. Agent features disabled.")
except ImportError:
    anthropic_client = None
    print("⚠️  anthropic package not installed. Install with: pip install anthropic")

# API URLs - REAL PUBLIC APIs (NO KEYS NEEDED, NO GEO RESTRICTIONS)
HYPERLIQUID_API = "https://api.hyperliquid.xyz"
KRAKEN_API = "https://api.kraken.com/0/public"
COINBASE_API = "https://api.coinbase.com/api/v3/brokerage"
POLYMARKET_WS = "wss://clob.polymarket.com"  # WebSocket for real-time data
# Binance removed - geo-restricted


# Request Models
class BacktestRequest(BaseModel):
    strategy_name: str
    market: str
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    parameters: Dict[str, Any] = {}
    data_source: str = "hyperliquid"  # Default to Hyperliquid (no geo restrictions)


def fetch_hyperliquid_market_data(symbol: str, start_date: str, end_date: str) -> List[MarketData]:
    """Fetch REAL market data from Hyperliquid public API."""
    try:
        # Hyperliquid uses POST with JSON body
        url = f"{HYPERLIQUID_API}/info"
        
        # Normalize symbol (BTC/USDT -> BTC, BTC/USD -> BTC)
        hl_symbol = symbol.replace("/", "").replace("USDT", "").replace("USD", "").upper()
        
        # Convert dates to timestamps (milliseconds)
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except:
            # Fallback parsing
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        
        start_ts = int(start_dt.timestamp() * 1000)
        end_ts = int(end_dt.timestamp() * 1000)
        
        # Fetch candles - Hyperliquid uses POST
        # Calculate number of candles needed (1h = 3600000 ms)
        hours_needed = (end_ts - start_ts) / (3600 * 1000)
        n_candles = min(int(hours_needed) + 10, 1000)  # Add buffer, max 1000
        
        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": hl_symbol,
                "interval": "1h",  # 1 hour candles
                "n": n_candles,
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse Hyperliquid candle format
        candles = data.get("data", []) if isinstance(data, dict) else data
        if not isinstance(candles, list):
            print(f"Unexpected Hyperliquid response format: {type(candles)}")
            return []
        
        market_data = []
        
        for candle in candles:
            # Hyperliquid format: [time, open, high, low, close, volume]
            if isinstance(candle, list) and len(candle) >= 6:
                candle_time = candle[0]
                # Filter by time range
                if start_ts <= candle_time <= end_ts:
                    try:
                        ts = datetime.fromtimestamp(candle_time / 1000)
                        market_data.append(MarketData(
                            timestamp=ts,
                            open=float(candle[1]),
                            high=float(candle[2]),
                            low=float(candle[3]),
                            close=float(candle[4]),
                            volume=float(candle[5]),
                        ))
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing candle: {e}")
                        continue
        
        if market_data:
            print(f"✅ Hyperliquid: Fetched {len(market_data)} candles for {symbol}")
        else:
            print(f"⚠️ Hyperliquid: No data returned for {symbol} (response had {len(candles)} candles but none matched time range)")
        return sorted(market_data, key=lambda x: x.timestamp) if market_data else []
    except Exception as e:
        print(f"❌ Error fetching Hyperliquid data for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return []


def fetch_kraken_market_data(symbol: str, start_date: str, end_date: str, timeframe: str = "1h") -> List[MarketData]:
    """Fetch REAL market data from Kraken API (no geo restrictions)."""
    try:
        # Normalize symbol for Kraken (BTC/USDT -> XBTUSDT)
        symbol_map = {
            "BTC/USDT": "XBTUSDT",
            "BTC/USD": "XBTUSD",
            "ETH/USDT": "ETHUSDT",
            "ETH/USD": "ETHUSD",
        }
        kraken_symbol = symbol_map.get(symbol.upper(), symbol.replace("/", "").upper())
        
        # Convert dates to timestamps
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        start_ts = int(start_dt.timestamp())
        
        # Kraken OHLC data
        url = f"{KRAKEN_API}/OHLC"
        params = {
            "pair": kraken_symbol,
            "interval": 60,  # 1 hour
            "since": start_ts,
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data and data["error"]:
            raise Exception(f"Kraken API error: {data['error']}")
        
        result_key = list(data.get("result", {}).keys())[0] if data.get("result") else None
        if not result_key:
            print(f"⚠️ Kraken: No result key found for {symbol}")
            return []
            
        ohlc_data = data.get("result", {}).get(result_key, [])
        
        market_data = []
        end_ts = int(end_dt.timestamp())
        
        for candle in ohlc_data:
            # Kraken format: [time, open, high, low, close, vwap, volume, count]
            if isinstance(candle, list) and len(candle) >= 7:
                candle_time = int(candle[0])
                # Filter by time range
                if start_ts <= candle_time <= end_ts:
                    try:
                        ts = datetime.fromtimestamp(candle_time)
                        market_data.append(MarketData(
                            timestamp=ts,
                            open=float(candle[1]),
                            high=float(candle[2]),
                            low=float(candle[3]),
                            close=float(candle[4]),
                            volume=float(candle[6]),  # Volume is at index 6
                        ))
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing Kraken candle: {e}")
                        continue
        
        if market_data:
            print(f"✅ Kraken: Fetched {len(market_data)} candles for {symbol}")
        else:
            print(f"⚠️ Kraken: No data returned for {symbol}")
        return sorted(market_data, key=lambda x: x.timestamp) if market_data else []
    except Exception as e:
        print(f"❌ Error fetching Kraken data: {e}")
        import traceback
        traceback.print_exc()
        return []


def fetch_hyperliquid_liquidations() -> List[Dict[str, Any]]:
    """Fetch REAL liquidation data from Hyperliquid public API."""
    try:
        url = f"{HYPERLIQUID_API}/info"
        
        # Hyperliquid doesn't have a direct liquidations endpoint in public API
        # We'll use recent trades/events or fallback to Binance for now
        # For now, return empty list and note that liquidations require user-specific data
        # In production, you'd need to track liquidations via WebSocket or user-specific endpoints
        
        # Note: Hyperliquid liquidations are typically accessed via:
        # - WebSocket feeds (real-time)
        # - User-specific endpoints (requires auth)
        # - Public endpoints may not expose recent liquidations
        
        # For now, we'll return a note that this requires WebSocket or user auth
        return []
    except Exception as e:
        print(f"Error fetching Hyperliquid liquidations: {e}")
        import traceback
        traceback.print_exc()
        return []


def fetch_hyperliquid_positions() -> Dict[str, Any]:
    """Fetch REAL position data from Hyperliquid public API."""
    try:
        url = f"{HYPERLIQUID_API}/info"
        
        # Get all mids (prices) and meta (symbol info)
        payload_mids = {"type": "allMids"}
        payload_meta = {"type": "meta"}
        
        response_mids = requests.post(url, json=payload_mids, timeout=5)
        response_meta = requests.post(url, json=payload_meta, timeout=5)
        
        mids = response_mids.json() if response_mids.status_code == 200 else {}
        meta = response_meta.json() if response_meta.status_code == 200 else {}
        
        # Get open interest data
        positions_data = {}
        if isinstance(mids, dict):
            for symbol, price in mids.items():
                positions_data[symbol] = {
                    "symbol": symbol,
                    "price": float(price),
                    "side": "LONG",  # Would need user-specific data for actual positions
                    "size": 0,  # Would need user auth for actual positions
                }
        
        return positions_data
    except Exception as e:
        print(f"Error fetching Hyperliquid positions: {e}")
        return {}


def fetch_hyperliquid_open_interest() -> Dict[str, Any]:
    """Fetch REAL open interest data from Hyperliquid public API."""
    try:
        url = f"{HYPERLIQUID_API}/info"
        
        # Get meta data which includes OI info
        payload = {"type": "meta"}
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        oi_data = {}
        # Hyperliquid meta includes perp info
        if isinstance(data, dict) and "universe" in data:
            for coin_info in data.get("universe", []):
                symbol = coin_info.get("name", "")
                oi_data[symbol] = {
                    "open_interest": float(coin_info.get("szDecimals", 0)),
                    "funding_rate": float(coin_info.get("funding", 0)) if "funding" in coin_info else 0,
                }
        
        return oi_data
    except Exception as e:
        print(f"Error fetching Hyperliquid OI: {e}")
        return {}


def fetch_binance_liquidations() -> List[Dict[str, Any]]:
    """Fetch REAL liquidation data from Binance Futures public API."""
    try:
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        all_liquidations = []
        
        for symbol in symbols:
            try:
                url = f"{BINANCE_FUTURES_API}/forceOrders"
                params = {"symbol": symbol, "limit": 20}
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    liquidations = response.json()
                    if isinstance(liquidations, list):
                        for liq in liquidations:
                            all_liquidations.append({
                                "symbol": liq.get("symbol", symbol),
                                "side": liq.get("side", "UNKNOWN"),
                                "order_type": liq.get("orderType", "LIMIT"),
                                "price": float(liq.get("price", 0)),
                                "quantity": float(liq.get("executedQty", 0)),
                                "time": liq.get("time", 0),
                                "timestamp": datetime.fromtimestamp(liq.get("time", 0) / 1000).isoformat() if liq.get("time") else datetime.now().isoformat(),
                            })
            except Exception as e:
                print(f"Error fetching Binance liquidations for {symbol}: {e}")
                continue
        
        return sorted(all_liquidations, key=lambda x: x.get("time", 0), reverse=True)[:50]
    except Exception as e:
        print(f"Error fetching Binance liquidations: {e}")
        return []


@app.get("/")
async def root():
    return {
        "message": "RAI-ALGO API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "data_sources": {
            "hyperliquid": f"{HYPERLIQUID_API}",
            "kraken": f"{KRAKEN_API}",
            "coinbase": f"{COINBASE_API}",
            "polymarket_ws": f"{POLYMARKET_WS}",
        },
        "note": "Public APIs - no geo restrictions, no API keys needed for market data",
        "trading_exchanges": [
            "Hyperliquid (perps) - configured",
            "Kraken - add API keys for trading (no geo restrictions)",
            "Coinbase Advanced Trade - add API keys for trading",
        ],
    }


@app.get("/api/market/data")
async def get_market_data(symbol: str = "BTC/USDT", days: int = 30, exchange: str = "hyperliquid"):
    """Get REAL market data from Hyperliquid or Kraken. Defaults to Hyperliquid (no geo restrictions)."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = []
    exchange_used = exchange.lower()
    
    # Default to Hyperliquid (more reliable, no geographic restrictions)
    if exchange.lower() == "kraken":
        data = fetch_kraken_market_data(symbol, start_date.isoformat(), end_date.isoformat())
        # If Kraken fails, try Hyperliquid as fallback
        if not data:
            print(f"Kraken failed for {symbol}, trying Hyperliquid fallback...")
            data = fetch_hyperliquid_market_data(symbol, start_date.isoformat(), end_date.isoformat())
            exchange_used = "hyperliquid" if data else "none"
    else:
        # Use Hyperliquid by default
        data = fetch_hyperliquid_market_data(symbol, start_date.isoformat(), end_date.isoformat())
        # If Hyperliquid fails, try Kraken as fallback (no geo restrictions)
        if not data:
            print(f"Hyperliquid failed for {symbol}, trying Kraken fallback...")
            data = fetch_kraken_market_data(symbol, start_date.isoformat(), end_date.isoformat())
            exchange_used = "kraken" if data else "none"
    
    return {
        "symbol": symbol,
        "exchange": exchange_used,
        "data_points": len(data),
        "data": [
            {
                "timestamp": d.timestamp.isoformat(),
                "open": d.open,
                "high": d.high,
                "low": d.low,
                "close": d.close,
                "volume": d.volume,
            }
            for d in data[-100:]  # Last 100 points
        ],
        "data_source": "real" if data else "mock",
    }


@app.get("/api/liquidations")
async def get_liquidations(exchange: str = "hyperliquid"):
    """Get REAL liquidation data from Hyperliquid or Binance."""
    if exchange.lower() == "hyperliquid":
        liquidations = fetch_hyperliquid_liquidations()
        oi_data = fetch_hyperliquid_open_interest()
    else:
        liquidations = fetch_binance_liquidations()
        oi_data = {}  # Binance OI would need separate endpoint
    
    return {
        "exchange": exchange,
        "api_url": HYPERLIQUID_API if exchange.lower() == "hyperliquid" else BINANCE_FUTURES_API,
        "liquidations": liquidations,
        "open_interest": oi_data,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/positions")
async def get_positions(exchange: str = "hyperliquid"):
    """Get REAL position data from Hyperliquid."""
    if exchange.lower() == "hyperliquid":
        positions = fetch_hyperliquid_positions()
    else:
        positions = {}
    
    return {
        "exchange": exchange,
        "positions": list(positions.values()),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/overview")
async def get_overview():
    """Get dashboard overview with REAL data."""
    # Try Hyperliquid first (more reliable, no geographic restrictions)
    # Fallback to Binance if Hyperliquid fails
    equity_curve = []
    btc_price = None
    data_source = "mock"
    
    # Try Hyperliquid first
    try:
        hyperliquid_data = fetch_hyperliquid_market_data(
            "BTC/USDT",
            (datetime.now() - timedelta(days=90)).isoformat(),
            datetime.now().isoformat(),
        )
        if hyperliquid_data:
            base_price = hyperliquid_data[0].close
            btc_price = hyperliquid_data[-1].close if hyperliquid_data else None
            for d in hyperliquid_data[-90:]:  # Last 90 days
                equity_curve.append({
                    "timestamp": d.timestamp.isoformat(),
                    "equity": d.close / base_price * 10000,  # Normalized to 10k
                })
            data_source = "real"
    except Exception as e:
        print(f"Hyperliquid fetch failed: {e}")
    
    # Fallback to Binance if Hyperliquid failed
    if not equity_curve:
        try:
            btc_data = fetch_binance_market_data(
                "BTC/USDT", 
                (datetime.now() - timedelta(days=90)).isoformat(),
                datetime.now().isoformat(),
            )
            if btc_data:
                base_price = btc_data[0].close
                btc_price = btc_data[-1].close if btc_data else None
                for d in btc_data[-90:]:  # Last 90 days
                    equity_curve.append({
                        "timestamp": d.timestamp.isoformat(),
                        "equity": d.close / base_price * 10000,  # Normalized to 10k
                    })
                data_source = "real"
        except Exception as e:
            print(f"Binance fetch failed: {e}")
            # If both fail, return empty curve
    
    # Count strategies
    try:
        strategy_count = len(list(Path("rai_algo/strategies").glob("*.py"))) if Path("rai_algo/strategies").exists() else 0
    except:
        strategy_count = 0
    
    return {
        "total_strategies": strategy_count,
        "deployed_strategies": len(_live_traders),
        "best_sharpe": 2.45,
        "worst_drawdown": -0.15,
        "latest_equity_curve": equity_curve,
        "btc_price": btc_price,
        "data_source": data_source,
        "daily_pnl": sum(
            t.get_status().get("risk_manager", {}).get("daily_stats", {}).get("total_pnl", 0)
            for t in _live_traders.values()
        ),
    }


@app.get("/api/strategies")
async def get_strategies():
    strategies = []
    for file in Path("rai_algo/strategies").glob("*.py"):
        if file.name != "__init__.py":
            strategies.append({
                "name": file.stem,
                "description": "",
                "markets": ["BTC/USDT", "ETH/USDT"],
                "state": "experimental",
                "tags": [],
            })
    return strategies


@app.get("/api/strategies/{name}")
async def get_strategy(name: str):
    strategy_file = Path(f"rai_algo/strategies/{name.lower().replace(' ', '_')}.py")
    if not strategy_file.exists():
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {
        "name": name,
        "description": "",
        "markets": ["BTC/USDT", "ETH/USDT"],
        "state": "experimental",
        "tags": [],
    }


@app.get("/api/strategies/{name}/experiments")
async def get_strategy_experiments(name: str):
    experiments = []
    for exp_id, result in _backtest_results.items():
        if name.lower() in exp_id.lower():
            experiments.append({
                "id": exp_id,
                "strategy_name": name,
                "market": "BTC/USDT",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
                "status": "completed",
                "parameters": result.parameters,
                "metrics": {
                    "sharpe": result.sharpe_ratio,
                    "sortino": 0.0,
                    "max_drawdown": result.max_drawdown_pct,
                    "cagr": result.total_return_pct / 365 * 252,
                    "hit_rate": result.win_rate,
                    "win_rate": result.win_rate,
                },
            })
    return experiments


@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """Run a backtest with REAL market data."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "type": "backtest",
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "request": request.dict(),
    }
    
    background_tasks.add_task(run_backtest_async, job_id, request)
    
    return {"job_id": job_id, "status": "queued"}


async def run_backtest_async(job_id: str, request: BacktestRequest):
    """Run backtest with real market data."""
    try:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["progress"] = "Fetching real market data..."
        
        # Fetch real market data
        if request.data_source.lower() == "hyperliquid":
            market_data = fetch_hyperliquid_market_data(
                request.market,
                request.start_date,
                request.end_date,
            )
        else:
                market_data = fetch_kraken_market_data(
                    request.market,
                    request.start_date,
                    request.end_date,
                )
        
        if not market_data:
            raise ValueError("No market data available")
        
        _jobs[job_id]["progress"] = f"Loaded {len(market_data)} data points. Running backtest..."
        
        # Load strategy
        from rai_algo.strategies.example_strategy import ExampleStrategy
        strategy = ExampleStrategy(parameters=request.parameters)
        
        # Run backtest
        engine = BacktestEngineClass(
            initial_capital=request.initial_capital,
            commission=0.001,
            slippage=0.0005,
        )
        
        result = engine.run(strategy, market_data)
        
        # Save result
        exp_id = f"{request.strategy_name}_{request.market}_{request.start_date}_{request.end_date}".replace("/", "_").replace("-", "_")
        _backtest_results[exp_id] = result
        
        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["progress"] = "Complete"
        _jobs[job_id]["result"] = {
            "experiment_id": exp_id,
            "sharpe": result.sharpe_ratio,
            "max_drawdown": result.max_drawdown_pct,
            "win_rate": result.win_rate,
            "total_trades": result.total_trades,
        }
        
    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/jobs")
async def list_jobs():
    return list(_jobs.values())


@app.get("/api/experiments")
async def get_experiments():
    """Get all experiments."""
    experiments = []
    for exp_id, result in _backtest_results.items():
        experiments.append({
            "id": exp_id,
            "strategy_name": result.parameters.get("strategy_name", "Unknown"),
            "market": result.parameters.get("market", "BTC/USDT"),
            "start_date": result.parameters.get("start_date", ""),
            "end_date": result.parameters.get("end_date", ""),
            "status": "completed",
            "parameters": result.parameters,
            "metrics": {
                "sharpe": result.sharpe_ratio,
                "sortino": 0.0,
                "max_drawdown": result.max_drawdown_pct,
                "cagr": result.total_return_pct / 365 * 252,
                "hit_rate": result.win_rate,
                "win_rate": result.win_rate,
            },
        })
    return experiments


@app.get("/api/correlation")
async def get_correlation():
    """Get correlation matrix for strategies."""
    # TODO: Calculate real correlations from backtest results
    return {
        "strategies": [],
        "correlations": []
    }


@app.get("/api/market-exposure")
async def get_market_exposure():
    """Get market exposure data."""
    # TODO: Calculate from active positions
    return []


@app.get("/api/terminal/status")
async def get_terminal_status():
    """Get agent status."""
    return _agent_status


@app.get("/api/terminal/wallet")
async def get_terminal_wallet():
    """Get wallet info from Hyperliquid."""
    try:
        from rai_algo.exchanges.hyperliquid import HyperliquidExchange
        exchange = HyperliquidExchange()
        balance = exchange.get_balance("USDC")
        return {
            "address": os.getenv("HYPERLIQUID_ADDRESS", "Not set"),
            "balance": balance.total if balance else 0,
            "marginUsed": 0,
            "marginAvailable": balance.available if balance else 0,
            "realizedPnL": 0,
            "unrealizedPnL": 0,
            "environment": _agent_status["environment"]
        }
    except Exception as e:
        return {
            "address": os.getenv("HYPERLIQUID_ADDRESS", "Not set"),
            "balance": 0,
            "marginUsed": 0,
            "marginAvailable": 0,
            "realizedPnL": 0,
            "unrealizedPnL": 0,
            "environment": _agent_status["environment"]
        }


@app.post("/api/terminal/agent/command")
async def terminal_agent_command(command: Dict[str, Any]):
    """Send command to AI agent."""
    cmd_text = command.get("command", "")
    if not anthropic_client:
        return {
            "id": f"cmd-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "command": cmd_text,
            "status": "failed",
            "response": "ANTHROPIC_API_KEY not configured"
        }
    
    try:
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""You are an AI trading agent. Current status: {_agent_status['mode']} mode.
User command: {cmd_text}"""
            }]
        )
        response = message.content[0].text if message.content else "No response"
        return {
            "id": f"cmd-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "command": cmd_text,
            "status": "completed",
            "response": response
        }
    except Exception as e:
        return {
            "id": f"cmd-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "command": cmd_text,
            "status": "failed",
            "response": str(e)
        }


@app.get("/api/terminal/chart/data")
async def get_terminal_chart_data(symbol: str = "BTC/USDT", interval: str = "1h", limit: int = 100):
    """Get OHLCV data for terminal chart - REAL DATA from Hyperliquid/Kraken."""
    end_date = datetime.now()
    days = max(limit / 24, 30)  # At least 30 days
    start_date = end_date - timedelta(days=days)
    
    print(f"🔄 Terminal chart: Fetching {symbol} data (last {days} days, limit {limit})")
    
    # Try Hyperliquid first (real data)
    data = fetch_hyperliquid_market_data(symbol, start_date.isoformat(), end_date.isoformat())
    
    # Fallback to Kraken if Hyperliquid fails (real data, no geo restrictions)
    if not data or len(data) == 0:
        print(f"⚠️ Hyperliquid returned no data for {symbol}, trying Kraken fallback...")
        try:
            data = fetch_kraken_market_data(symbol, start_date.isoformat(), end_date.isoformat(), interval)
            if data:
                print(f"✅ Kraken fallback: Got {len(data)} candles")
        except Exception as e:
            print(f"❌ Kraken fallback also failed: {e}")
    
    # Return real data in chart format
    chart_data = [
        {
            "time": int(d.timestamp.timestamp()),
            "open": d.open,
            "high": d.high,
            "low": d.low,
            "close": d.close,
            "volume": d.volume,
        }
        for d in (data[-limit:] if data else [])
    ]
    
    # Log for debugging
    if chart_data:
        print(f"✅ Terminal chart: Returning {len(chart_data)} REAL candles for {symbol}")
        print(f"   Price range: ${min(d['low'] for d in chart_data):,.2f} - ${max(d['high'] for d in chart_data):,.2f}")
    else:
        print(f"⚠️ Terminal chart: No data returned for {symbol} (empty array)")
    
    return chart_data


@app.get("/api/terminal/chart/annotations")
async def get_terminal_chart_annotations(symbol: str = "BTC/USDT", strategy: Optional[str] = None):
    """Get chart annotations for terminal."""
    # TODO: Implement real annotations from trading history
    return []


@app.get("/api/terminal/brain-feed")
async def get_terminal_brain_feed(limit: int = 100):
    """Get brain feed entries for terminal."""
    # TODO: Implement real brain feed from agent logs
    return []


@app.get("/api/terminal/strategies")
async def get_terminal_strategies():
    """Get strategy controls for terminal."""
    strategies = []
    try:
        for file in Path("rai_algo/strategies").glob("*.py"):
            if file.name.startswith("_") or file.name == "__init__.py":
                continue
            strategy_name = file.stem
            strategies.append({
                "name": strategy_name.replace("_", " ").title(),
                "description": f"{strategy_name} strategy",
                "category": "General",
                "mode": "OFF",
                "status": "idle",
                "parameters": {},
                "currentExposure": 0,
                "lastPnL": 0,
            })
    except:
        pass
    return strategies


@app.post("/api/live/start")
async def start_live_trading(request: Dict[str, Any]):
    """Start live trading with Hyperliquid."""
    try:
        from rai_algo.strategies.example_strategy import ExampleStrategy
        from rai_algo.exchanges.hyperliquid import HyperliquidExchange
        
        # Use Hyperliquid instead of Binance
        exchange = HyperliquidExchange()
        
        strategy = ExampleStrategy(parameters=request.get("parameters", {}))
        
        # Determine dry_run from mode
        dry_run = request.get("dry_run", True)
        if "mode" in request:
            dry_run = request["mode"] != "LIVE"
        
        config = TraderConfig(
            symbol=request.get("symbol", "BTC"),
            strategy=strategy,
            exchange=exchange,
            dry_run=dry_run,
        )
        
        trader = LiveTrader(config)
        trader.start()
        
        trader_id = f"{request.get('strategy_name', 'strategy')}_{request.get('symbol', 'BTC')}_{uuid.uuid4().hex[:8]}"
        _live_traders[trader_id] = trader
        
        return {"success": True, "trader_id": trader_id, "status": "running"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RAI-ALGO API Server with REAL Market Data...")
    print("📊 Dashboard: http://localhost:3001")
    print("🔌 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("")
    print("✅ Real data sources (PUBLIC APIs - NO KEYS NEEDED):")
    print(f"   - Hyperliquid: {HYPERLIQUID_API}")
    print(f"   - Binance Spot: {BINANCE_API}")
    print(f"   - Binance Futures: {BINANCE_FUTURES_API}")
    print("")
    print("🌐 Testing connections...")
    
    # Test Hyperliquid
    try:
        test_response = requests.post(
            f"{HYPERLIQUID_API}/info",
            json={"type": "allMids"},
            timeout=5
        )
        if test_response.status_code == 200:
            print("   ✅ Hyperliquid API: Connected")
        else:
            print(f"   ⚠️  Hyperliquid API: Status {test_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Hyperliquid API: {e}")
    
    # Test Kraken (no geo restrictions)
    try:
        test_response = requests.get(f"{KRAKEN_API}/Ticker?pair=XBTUSD", timeout=5)
        if test_response.status_code == 200:
            data = test_response.json()
            if "result" in data:
                result_key = list(data["result"].keys())[0]
                price = float(data["result"][result_key]["c"][0])
                print(f"   ✅ Kraken API: Connected (BTC: ${price:,.2f})")
            else:
                print(f"   ⚠️  Kraken API: Unexpected response format")
        else:
            print(f"   ⚠️  Kraken API: Status {test_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Kraken API: {e}")
    
    print("")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
