"""
Coinbase Advanced Trade API Integration
Professional spot trading and market data
"""

import requests
import hmac
import hashlib
import base64
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from rai_algo.data_types import MarketData, Order
from rai_algo.exchanges.base import BaseExchange
import logging

logger = logging.getLogger(__name__)

COINBASE_API_URL = "https://api.coinbase.com/api/v3/brokerage"


class CoinbaseExchange(BaseExchange):
    """Coinbase Advanced Trade API integration."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Coinbase exchange.
        
        Args:
            config: Dictionary with 'api_key' and 'api_secret'
        """
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.base_url = COINBASE_API_URL
        
    def _sign_request(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Sign request for Coinbase Advanced Trade API."""
        timestamp = str(int(time.time()))
        message = timestamp + method + path + body
        
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, signed: bool = False) -> Dict:
        """Make HTTP request to Coinbase API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        body = ""
        if params:
            import json
            body = json.dumps(params)
        
        if signed and self.api_key and self.api_secret:
            headers.update(self._sign_request(method, endpoint, body))
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Coinbase API error: {e}")
            raise
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Fetch current market data."""
        try:
            # Convert symbol format (BTC/USDT -> BTC-USDT)
            cb_symbol = symbol.replace("/", "-")
            
            # Public endpoint - no auth needed
            ticker = self._make_request("GET", f"/products/{cb_symbol}/ticker", signed=False)
            
            price = float(ticker.get("price", 0))
            
            return MarketData(
                timestamp=datetime.now(),
                open=price,  # Coinbase doesn't provide 24h open in ticker
                high=float(ticker.get("high_24h", price)),
                low=float(ticker.get("low_24h", price)),
                close=price,
                volume=float(ticker.get("volume_24h", 0)),
                metadata={
                    "symbol": symbol,
                    "bid": float(ticker.get("bid", price)),
                    "ask": float(ticker.get("ask", price)),
                    "exchange": "coinbase"
                },
            )
        except Exception as e:
            logger.error(f"Error fetching Coinbase market data: {e}")
            raise
    
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Order:
        """Place order on Coinbase."""
        if not self.api_key or not self.api_secret:
            raise ValueError("Coinbase API credentials required for trading")
        
        cb_symbol = symbol.replace("/", "-")
        
        order_config = {
            "product_id": cb_symbol,
            "side": side.upper(),
            "order_configuration": {}
        }
        
        if order_type == "MARKET":
            order_config["order_configuration"] = {
                "market_market_ioc": {
                    "quote_size": str(quantity) if side.upper() == "BUY" else None,
                    "base_size": str(quantity) if side.upper() == "SELL" else None,
                }
            }
        elif order_type == "LIMIT":
            if not price:
                raise ValueError("Price required for limit orders")
            order_config["order_configuration"] = {
                "limit_limit_gtc": {
                    "base_size": str(quantity),
                    "limit_price": str(price),
                }
            }
        
        response = self._make_request("POST", "/orders", params=order_config, signed=True)
        
        return Order(
            id=response.get("order_id", ""),
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price or 0,
            status="pending",
            timestamp=datetime.now(),
        )

