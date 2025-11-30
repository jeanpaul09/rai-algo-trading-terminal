"""
Kraken API Integration
Multi-asset trading with fiat pairs
"""

import requests
import hmac
import hashlib
import base64
import urllib.parse
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from rai_algo.data_types import MarketData, Order
from rai_algo.exchanges.base import BaseExchange
import logging

logger = logging.getLogger(__name__)

KRAKEN_API_URL = "https://api.kraken.com"


class KrakenExchange(BaseExchange):
    """Kraken API integration."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Kraken exchange.
        
        Args:
            config: Dictionary with 'api_key' and 'api_secret'
        """
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.base_url = KRAKEN_API_URL
        
    def _sign_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Sign request for Kraken API."""
        nonce = str(int(time.time() * 1000))
        data["nonce"] = nonce
        
        post_data = urllib.parse.urlencode(data)
        message = endpoint.encode() + hashlib.sha256(nonce.encode() + post_data.encode()).digest()
        
        signature = base64.b64encode(
            hmac.new(
                base64.b64decode(self.api_secret),
                message,
                hashlib.sha512
            ).digest()
        ).decode()
        
        return {
            "API-Key": self.api_key,
            "API-Sign": signature,
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, signed: bool = False) -> Dict:
        """Make HTTP request to Kraken API."""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if signed:
            if not self.api_key or not self.api_secret:
                raise ValueError("Kraken API credentials required")
            headers.update(self._sign_request(endpoint, params or {}))
        
        try:
            if signed:
                response = requests.post(url, data=params, headers=headers, timeout=10)
            else:
                response = requests.get(url, params=params, headers=headers, timeout=10)
            
            response.raise_for_status()
            result = response.json()
            
            # Kraken wraps results in 'result' key
            if "result" in result:
                return result["result"]
            if "error" in result and result["error"]:
                raise Exception(f"Kraken API error: {result['error']}")
            return result
        except Exception as e:
            logger.error(f"Kraken API error: {e}")
            raise
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Fetch current market data."""
        try:
            # Convert symbol format (BTC/USDT -> XBTUSDT for Kraken)
            # Kraken uses different symbol naming (XBT instead of BTC)
            kraken_symbol = self._normalize_symbol(symbol)
            
            ticker_data = self._make_request("/0/public/Ticker", params={"pair": kraken_symbol}, signed=False)
            
            # Kraken returns nested dict with symbol as key
            ticker_key = list(ticker_data.keys())[0] if ticker_data else None
            if not ticker_key:
                raise ValueError(f"Symbol {symbol} not found on Kraken")
            
            ticker = ticker_data[ticker_key]
            price = float(ticker["c"][0])  # Last price
            
            return MarketData(
                timestamp=datetime.now(),
                open=float(ticker["o"]),  # 24h open
                high=float(ticker["h"][1]),  # 24h high
                low=float(ticker["l"][1]),  # 24h low
                close=price,
                volume=float(ticker["v"][1]),  # 24h volume
                metadata={
                    "symbol": symbol,
                    "bid": float(ticker["b"][0]),
                    "ask": float(ticker["a"][0]),
                    "exchange": "kraken"
                },
            )
        except Exception as e:
            logger.error(f"Error fetching Kraken market data: {e}")
            raise
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Convert symbol to Kraken format."""
        # Kraken uses XBT instead of BTC, XETH instead of ETH
        symbol_map = {
            "BTC/USDT": "XBTUSDT",
            "BTC/USD": "XBTUSD",
            "ETH/USDT": "ETHUSDT",
            "ETH/USD": "ETHUSD",
        }
        
        normalized = symbol_map.get(symbol.upper(), symbol.replace("/", "").upper())
        return normalized
    
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Order:
        """Place order on Kraken."""
        if not self.api_key or not self.api_secret:
            raise ValueError("Kraken API credentials required for trading")
        
        kraken_symbol = self._normalize_symbol(symbol)
        order_type_kraken = order_type.lower()  # market or limit
        
        params = {
            "pair": kraken_symbol,
            "type": side.lower(),  # buy or sell
            "ordertype": order_type_kraken,
            "volume": str(quantity),
        }
        
        if order_type_kraken == "limit":
            if not price:
                raise ValueError("Price required for limit orders")
            params["price"] = str(price)
        
        response = self._make_request("/0/private/AddOrder", params=params, signed=True)
        
        order_ids = response.get("txid", [])
        order_id = order_ids[0] if order_ids else ""
        
        return Order(
            id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price or 0,
            status="pending",
            timestamp=datetime.now(),
        )

