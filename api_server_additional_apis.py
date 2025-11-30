"""
Additional API Integrations for Professional Trading
Coinbase, Kraken, Polymarket WebSocket support
"""

from fastapi import APIRouter, WebSocket
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests
import json
import asyncio
import websockets
from pydantic import BaseModel

router = APIRouter()

# API Base URLs
COINBASE_API = "https://api.coinbase.com/api/v3/brokerage"
KRAKEN_API = "https://api.kraken.com/0/public"
POLYMARKET_WS = "wss://clob.polymarket.com"


def fetch_coinbase_market_data(symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Fetch REAL market data from Coinbase Advanced Trade API."""
    try:
        # Convert symbol format (BTC/USDT -> BTC-USDT)
        cb_symbol = symbol.replace("/", "-")
        
        # Coinbase candles endpoint
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        
        url = f"{COINBASE_API}/products/{cb_symbol}/candles"
        params = {
            "start": start_ts,
            "end": end_ts,
            "granularity": "3600",  # 1 hour candles
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        candles = []
        for candle in data.get("candles", []):
            candles.append({
                "timestamp": datetime.fromtimestamp(int(candle[0])).isoformat(),
                "open": float(candle[3]),
                "high": float(candle[2]),
                "low": float(candle[1]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
            })
        
        return candles
    except Exception as e:
        print(f"Error fetching Coinbase data: {e}")
        return []


def fetch_kraken_market_data(symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Fetch REAL market data from Kraken API."""
    try:
        # Normalize symbol for Kraken (BTC/USDT -> XBTUSDT)
        symbol_map = {
            "BTC/USDT": "XBTUSDT",
            "BTC/USD": "XBTUSD",
            "ETH/USDT": "ETHUSDT",
            "ETH/USD": "ETHUSD",
        }
        kraken_symbol = symbol_map.get(symbol.upper(), symbol.replace("/", "").upper())
        
        # Kraken OHLC data
        url = f"{KRAKEN_API}/OHLC"
        params = {
            "pair": kraken_symbol,
            "interval": 60,  # 1 hour
            "since": int(datetime.fromisoformat(start_date.replace("Z", "+00:00")).timestamp()),
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data and data["error"]:
            raise Exception(f"Kraken API error: {data['error']}")
        
        result_key = list(data.get("result", {}).keys())[0]
        ohlc_data = data.get("result", {}).get(result_key, [])
        
        candles = []
        for candle in ohlc_data:
            candles.append({
                "timestamp": datetime.fromtimestamp(int(candle[0])).isoformat(),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[6]),
            })
        
        return candles
    except Exception as e:
        print(f"Error fetching Kraken data: {e}")
        return []


@router.get("/api/market/data/coinbase")
async def get_coinbase_market_data(symbol: str = "BTC-USDT", days: int = 30):
    """Get REAL market data from Coinbase."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = fetch_coinbase_market_data(
        symbol,
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    return {
        "symbol": symbol,
        "exchange": "coinbase",
        "data_points": len(data),
        "data": data[-100:],  # Last 100 points
        "data_source": "real",
    }


@router.get("/api/market/data/kraken")
async def get_kraken_market_data(symbol: str = "BTC/USDT", days: int = 30):
    """Get REAL market data from Kraken."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = fetch_kraken_market_data(
        symbol,
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    return {
        "symbol": symbol,
        "exchange": "kraken",
        "data_points": len(data),
        "data": data[-100:],  # Last 100 points
        "data_source": "real",
    }


@router.websocket("/ws/polymarket")
async def polymarket_websocket(websocket: WebSocket):
    """WebSocket endpoint for Polymarket real-time data."""
    await websocket.accept()
    
    try:
        # Connect to Polymarket WebSocket
        async with websockets.connect(POLYMARKET_WS) as ws:
            # Subscribe to market updates
            await ws.send(json.dumps({
                "type": "subscribe",
                "channel": "markets",
            }))
            
            async for message in ws:
                try:
                    data = json.loads(message)
                    await websocket.send_json({
                        "type": "polymarket_update",
                        "data": data,
                        "timestamp": datetime.now().isoformat(),
                    })
                except Exception as e:
                    print(f"Error processing Polymarket message: {e}")
    except Exception as e:
        print(f"Polymarket WebSocket error: {e}")
        await websocket.close()

