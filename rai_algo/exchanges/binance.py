"""
Binance exchange connector implementation.
Example implementation of BaseExchange for Binance.
"""
import os
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import hmac
import hashlib
import requests
import logging

from rai_algo.exchange import BaseExchange, Order, Balance
from rai_algo.data_types import MarketData, Position, SignalType


logger = logging.getLogger(__name__)


class BinanceExchange(BaseExchange):
    """
    Binance exchange connector.
    
    Environment variables required:
    - BINANCE_API_KEY: Your Binance API key
    - BINANCE_API_SECRET: Your Binance API secret
    - BINANCE_TESTNET: Set to "true" to use testnet (optional)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Binance connector.
        
        Args:
            config: Optional config dict. If None, reads from environment variables.
        """
        if config is None:
            config = {
                "api_key": os.getenv("BINANCE_API_KEY"),
                "api_secret": os.getenv("BINANCE_API_SECRET"),
                "testnet": os.getenv("BINANCE_TESTNET", "false").lower() == "true",
            }
        
        base_url = "https://testnet.binance.vision" if config.get("testnet") else "https://api.binance.com"
        config["base_url"] = base_url
        
        super().__init__(name="Binance", config=config)
        self.base_url = config["base_url"]
    
    def _sign_request(self, params: Dict[str, Any]) -> str:
        """Generate signature for authenticated requests."""
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.config["api_secret"].encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, signed: bool = False) -> Dict:
        """Make HTTP request to Binance API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.config["api_key"]}
        
        if params is None:
            params = {}
        
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._sign_request(params)
        
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, params=params, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, params=params, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Fetch current market data."""
        try:
            # Convert symbol format (BTC/USDT -> BTCUSDT)
            binance_symbol = symbol.replace("/", "")
            
            ticker = self._make_request("GET", "/api/v3/ticker/24hr", {"symbol": binance_symbol})
            price = float(ticker["lastPrice"])
            
            return MarketData(
                timestamp=datetime.now(),
                open=float(ticker.get("openPrice", price)),
                high=float(ticker.get("highPrice", price)),
                low=float(ticker.get("lowPrice", price)),
                close=price,
                volume=float(ticker["volume"]),
                metadata={"symbol": symbol, "bid": float(ticker.get("bidPrice", price)), "ask": float(ticker.get("askPrice", price))},
            )
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
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
        """Place an order."""
        try:
            binance_symbol = symbol.replace("/", "")
            binance_side = side.upper()
            binance_type = order_type.upper()
            
            params = {
                "symbol": binance_symbol,
                "side": binance_side,
                "type": binance_type,
                "quantity": quantity,
            }
            
            if binance_type == "LIMIT":
                if price is None:
                    raise ValueError("Price required for LIMIT orders")
                params["price"] = price
                params["timeInForce"] = "GTC"
            
            if stop_price:
                params["stopPrice"] = stop_price
            
            result = self._make_request("POST", "/api/v3/order", params, signed=True)
            
            return Order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=price,
                stop_price=stop_price,
                order_id=str(result["orderId"]),
                status="FILLED" if result.get("status") == "FILLED" else "PENDING",
                filled_quantity=float(result.get("executedQty", 0)),
                average_fill_price=float(result.get("price", 0)) if result.get("price") else None,
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order."""
        try:
            binance_symbol = symbol.replace("/", "")
            params = {
                "symbol": binance_symbol,
                "orderId": order_id,
            }
            self._make_request("DELETE", "/api/v3/order", params, signed=True)
            return True
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            return False
    
    def get_order_status(self, order_id: str, symbol: str) -> Order:
        """Get order status."""
        try:
            binance_symbol = symbol.replace("/", "")
            params = {
                "symbol": binance_symbol,
                "orderId": order_id,
            }
            result = self._make_request("GET", "/api/v3/order", params, signed=True)
            
            return Order(
                symbol=symbol,
                side=result["side"],
                quantity=float(result["origQty"]),
                order_type=result["type"],
                price=float(result.get("price", 0)) if result.get("price") else None,
                order_id=str(result["orderId"]),
                status=result["status"],
                filled_quantity=float(result.get("executedQty", 0)),
                average_fill_price=float(result.get("price", 0)) if result.get("price") else None,
                timestamp=datetime.fromtimestamp(result["time"] / 1000),
            )
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position."""
        try:
            # For spot trading, check account balance
            # For futures, use position endpoint
            binance_symbol = symbol.replace("/", "")
            base_asset = binance_symbol.replace("USDT", "").replace("USD", "")
            
            account = self._make_request("GET", "/api/v3/account", signed=True)
            
            for balance_info in account.get("balances", []):
                if balance_info["asset"] == base_asset:
                    free = float(balance_info["free"])
                    locked = float(balance_info["locked"])
                    total = free + locked
                    
                    if total > 0:
                        # Get current price
                        market_data = self.get_market_data(symbol)
                        
                        return Position(
                            entry_price=market_data.price,  # Approximate
                            size=total,
                            entry_time=datetime.now(),
                            current_price=market_data.price,
                            signal_type=SignalType.BUY,
                            metadata={"symbol": symbol},
                        )
            
            return None
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return None
    
    def get_balance(self, currency: str = "USDT") -> Balance:
        """Get account balance."""
        try:
            account = self._make_request("GET", "/api/v3/account", signed=True)
            
            for balance_info in account.get("balances", []):
                if balance_info["asset"] == currency:
                    free = float(balance_info["free"])
                    locked = float(balance_info["locked"])
                    total = free + locked
                    
                    return Balance(
                        currency=currency,
                        available=free,
                        locked=locked,
                        total=total,
                    )
            
            return Balance(currency=currency, available=0.0, locked=0.0, total=0.0)
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders."""
        try:
            params = {}
            if symbol:
                params["symbol"] = symbol.replace("/", "")
            
            results = self._make_request("GET", "/api/v3/openOrders", params, signed=True)
            
            orders = []
            for result in results:
                orders.append(Order(
                    symbol=result["symbol"].replace("USDT", "/USDT"),
                    side=result["side"],
                    quantity=float(result["origQty"]),
                    order_type=result["type"],
                    price=float(result.get("price", 0)) if result.get("price") else None,
                    order_id=str(result["orderId"]),
                    status=result["status"],
                    filled_quantity=float(result.get("executedQty", 0)),
                    timestamp=datetime.fromtimestamp(result["time"] / 1000),
                ))
            
            return orders
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []

