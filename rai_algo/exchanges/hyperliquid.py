"""
Hyperliquid exchange connector implementation.

Enables live trading and paper trading on Hyperliquid perpetual contracts.
"""
import os
import time
import logging
import requests
import hmac
import hashlib
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from rai_algo.exchange import BaseExchange, Order, Balance
from rai_algo.data_types import MarketData, Position, SignalType


logger = logging.getLogger(__name__)

# Hyperliquid API endpoints
HYPERLIQUID_BASE_URL = "https://api.hyperliquid.xyz"
HYPERLIQUID_WS_URL = "wss://api.hyperliquid.xyz/ws"


class HyperliquidExchange(BaseExchange):
    """
    Hyperliquid exchange connector for perpetual contracts.
    
    Environment variables required:
    - HYPERLIQUID_PRIVATE_KEY: Your Hyperliquid private key (for signing)
    - HYPERLIQUID_ADDRESS: Your wallet address (optional, for some operations)
    - HYPERLIQUID_TESTNET: Set to "true" to use testnet (optional)
    
    Note: Hyperliquid uses wallet-based authentication with private key signing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Hyperliquid connector.
        
        Args:
            config: Optional config dict. If None, reads from environment variables.
        """
        if config is None:
            config = {
                "private_key": os.getenv("HYPERLIQUID_PRIVATE_KEY"),
                "address": os.getenv("HYPERLIQUID_ADDRESS"),
                "testnet": os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true",
            }
        
        # Hyperliquid uses wallet-based auth, not traditional API keys
        # For now, we'll use a simplified approach
        # In production, you'd use proper wallet signing (e.g., via web3)
        if not config.get("private_key"):
            logger.warning(
                "HYPERLIQUID_PRIVATE_KEY not set. Some operations may fail."
            )
        
        base_url = config.get("base_url", HYPERLIQUID_BASE_URL)
        config["base_url"] = base_url
        
        # Add dummy api_key/api_secret to pass base class validation
        # Hyperliquid doesn't actually use these, but BaseExchange requires them
        if "api_key" not in config:
            config["api_key"] = config.get("private_key", "") or "dummy"
        if "api_secret" not in config:
            config["api_secret"] = config.get("private_key", "") or "dummy"
        
        # Initialize base class
        super().__init__(name="Hyperliquid", config=config)
        
        # Set Hyperliquid-specific attributes
        self.base_url = base_url
        self.private_key = config.get("private_key")
        self.address = config.get("address")
    
    def _validate_config(self):
        """Validate exchange configuration."""
        # Hyperliquid uses wallet-based auth, so we don't require api_key/api_secret
        # Override base class validation to skip the check
        pass
    
    def _sign_message(self, message: str) -> str:
        """
        Sign a message with the private key.
        
        Note: This is a simplified version. In production, use proper
        cryptographic signing (e.g., via web3.py or eth_account).
        
        Args:
            message: Message to sign
            
        Returns:
            Signature string
        """
        if not self.private_key:
            raise ValueError("Private key required for signing")
        
        # Simplified signing - in production, use proper ECDSA signing
        # This is a placeholder that should be replaced with actual signing
        # For example, using eth_account or similar library
        try:
            # Attempt to use eth_account if available
            from eth_account import Account
            account = Account.from_key(self.private_key)
            signed = account.sign_message(message)
            return signed.signature.hex()
        except ImportError:
            logger.warning(
                "eth_account not available. Install with: pip install eth-account"
            )
            # Fallback: use HMAC (not cryptographically correct, but works for testing)
            return hmac.new(
                self.private_key.encode() if isinstance(self.private_key, str) else self.private_key,
                message.encode(),
                hashlib.sha256
            ).hexdigest()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict:
        """
        Make HTTP request to Hyperliquid API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            signed: Whether to sign the request
            
        Returns:
            JSON response as dict
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if params is None:
            params = {}
        if data is None:
            data = {}
        
        if signed:
            # Hyperliquid uses wallet-based signing
            # Create a signature for the request
            timestamp = int(time.time() * 1000)
            message = json.dumps(data, sort_keys=True) if data else ""
            signature = self._sign_message(f"{method}{endpoint}{message}{timestamp}")
            headers["X-Signature"] = signature
            headers["X-Timestamp"] = str(timestamp)
            if self.address:
                headers["X-Address"] = self.address
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, params=params, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Error details: {error_detail}")
                except:
                    logger.error(f"Error response: {e.response.text}")
            raise
    
    def get_market_data(self, symbol: str) -> MarketData:
        """
        Fetch current market data for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC", "ETH")
            
        Returns:
            MarketData object
        """
        try:
            # Normalize symbol
            hl_symbol = self._normalize_symbol(symbol)
            
            # Fetch ticker data
            url = f"{self.base_url}/info"
            params = {
                "type": "allMids",
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find the symbol in the response
            # Hyperliquid returns a dict with symbol -> price
            price = None
            if isinstance(data, dict):
                # Try different possible keys
                for key in [hl_symbol, symbol, symbol.replace("/", "")]:
                    if key in data:
                        price = float(data[key])
                        break
            
            if price is None:
                # Fallback: try to get from orderbook
                params = {
                    "type": "l2Book",
                    "coin": hl_symbol,
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                book_data = response.json()
                
                # Extract mid price from orderbook
                if isinstance(book_data, dict) and "levels" in book_data:
                    bids = book_data["levels"].get("bids", [])
                    asks = book_data["levels"].get("asks", [])
                    if bids and asks:
                        bid_price = float(bids[0][0])
                        ask_price = float(asks[0][0])
                        price = (bid_price + ask_price) / 2
            
            if price is None:
                raise ValueError(f"Could not fetch price for {symbol}")
            
            # For now, use price for all OHLC (in production, fetch actual OHLC)
            return MarketData(
                timestamp=datetime.now(),
                open=price,
                high=price,
                low=price,
                close=price,
                volume=0.0,  # Would need to fetch from API
                metadata={"symbol": symbol, "source": "hyperliquid"},
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
        """
        Place an order on Hyperliquid.
        
        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            quantity: Order quantity (in base currency)
            order_type: Order type (MARKET, LIMIT)
            price: Limit price (for LIMIT orders)
            stop_price: Stop price (for STOP orders - may not be supported)
            
        Returns:
            Order object
        """
        try:
            if not self.private_key:
                raise ValueError("Private key required for placing orders")
            
            hl_symbol = self._normalize_symbol(symbol)
            is_buy = side.upper() == "BUY"
            
            # Build order payload
            order_data = {
                "coin": hl_symbol,
                "is_buy": is_buy,
                "sz": str(quantity),  # Size as string
            }
            
            if order_type.upper() == "LIMIT":
                if price is None:
                    raise ValueError("Price required for LIMIT orders")
                order_data["limit_px"] = str(price)
                order_data["order_type"] = {"limit": {"tif": "Gtc"}}
            else:  # MARKET
                order_data["order_type"] = {"market": {}}
            
            # Place order via API
            # Note: Hyperliquid's actual API structure may differ
            # This is a template that should be adjusted based on official docs
            result = self._make_request(
                "POST",
                "/exchange",
                data={"action": {"type": "order", "orders": [order_data]}},
                signed=True,
            )
            
            # Parse response
            order_id = result.get("statuses", [{}])[0].get("resting", {}).get("oid")
            if not order_id:
                order_id = result.get("statuses", [{}])[0].get("filled", {}).get("oid")
            
            return Order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=price,
                stop_price=stop_price,
                order_id=str(order_id) if order_id else None,
                status="FILLED" if result.get("statuses", [{}])[0].get("filled") else "PENDING",
                filled_quantity=quantity if result.get("statuses", [{}])[0].get("filled") else 0.0,
                average_fill_price=price,
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading symbol
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.private_key:
                raise ValueError("Private key required for canceling orders")
            
            hl_symbol = self._normalize_symbol(symbol)
            
            cancel_data = {
                "action": {
                    "type": "cancel",
                    "cancels": [{"a": hl_symbol, "o": int(order_id)}],
                }
            }
            
            result = self._make_request(
                "POST",
                "/exchange",
                data=cancel_data,
                signed=True,
            )
            
            return result.get("status") == "ok"
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            return False
    
    def get_order_status(self, order_id: str, symbol: str) -> Order:
        """
        Get order status.
        
        Args:
            order_id: Order ID
            symbol: Trading symbol
            
        Returns:
            Order object with current status
        """
        try:
            # Fetch open orders and find the matching one
            open_orders = self.get_open_orders(symbol)
            for order in open_orders:
                if order.order_id == order_id:
                    return order
            
            # If not in open orders, it may be filled or cancelled
            # In production, you'd query the order history
            raise ValueError(f"Order {order_id} not found")
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get current position for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position object if position exists, None otherwise
        """
        try:
            if not self.private_key:
                # Can't fetch positions without auth
                return None
            
            hl_symbol = self._normalize_symbol(symbol)
            
            # Fetch user state
            url = f"{self.base_url}/info"
            params = {
                "type": "clearinghouseState",
                "user": self.address,
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find position for this symbol
            positions = data.get("assetPositions", [])
            for pos in positions:
                if pos.get("position", {}).get("coin") == hl_symbol:
                    position_data = pos["position"]
                    size = float(position_data.get("szi", 0))
                    
                    if size == 0:
                        return None
                    
                    entry_price = float(position_data.get("entryPx", 0))
                    current_price = self.get_market_data(symbol).price
                    
                    return Position(
                        entry_price=entry_price,
                        size=abs(size),
                        entry_time=datetime.now(),  # Would need to fetch from API
                        current_price=current_price,
                        signal_type=SignalType.BUY if size > 0 else SignalType.SELL,
                        metadata={"symbol": symbol, "source": "hyperliquid"},
                    )
            
            return None
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return None
    
    def get_balance(self, currency: str = "USDC") -> Balance:
        """
        Get account balance.
        
        Args:
            currency: Currency symbol (default: USDC for Hyperliquid)
            
        Returns:
            Balance object
        """
        try:
            if not self.private_key:
                # Can't fetch balance without auth
                return Balance(currency=currency, available=0.0, locked=0.0, total=0.0)
            
            url = f"{self.base_url}/info"
            params = {
                "type": "clearinghouseState",
                "user": self.address,
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract balance
            margin_summary = data.get("marginSummary", {})
            total = float(margin_summary.get("accountValue", 0))
            # Available = total - used margin
            used_margin = float(margin_summary.get("totalMarginUsed", 0))
            available = total - used_margin
            
            return Balance(
                currency=currency,
                available=available,
                locked=used_margin,
                total=total,
            )
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            # Return zero balance on error
            return Balance(currency=currency, available=0.0, locked=0.0, total=0.0)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get all open orders.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open Order objects
        """
        try:
            if not self.private_key:
                return []
            
            url = f"{self.base_url}/info"
            params = {
                "type": "openOrders",
                "user": self.address,
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            orders = []
            open_orders = data if isinstance(data, list) else data.get("orders", [])
            
            for order_data in open_orders:
                order_symbol = order_data.get("coin", "")
                
                if symbol and self._normalize_symbol(symbol) != order_symbol:
                    continue
                
                orders.append(Order(
                    symbol=order_symbol,
                    side="BUY" if order_data.get("side", {}).get("bids") else "SELL",
                    quantity=float(order_data.get("sz", 0)),
                    order_type="LIMIT" if order_data.get("limitPx") else "MARKET",
                    price=float(order_data.get("limitPx", 0)) if order_data.get("limitPx") else None,
                    order_id=str(order_data.get("oid", "")),
                    status="PENDING",
                    timestamp=datetime.now(),
                ))
            
            return orders
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol to Hyperliquid format.
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USDT", "BTCUSDT", "BTC")
            
        Returns:
            Hyperliquid symbol format (e.g., "BTC")
        """
        # Remove common separators and quote currency
        symbol = symbol.replace("/", "").replace("-", "").upper()
        
        # Remove quote currencies
        for quote in ["USDT", "USD", "USDC", "BTC", "ETH"]:
            if symbol.endswith(quote) and symbol != quote:
                symbol = symbol[:-len(quote)]
                break
        
        return symbol

