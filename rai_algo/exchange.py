"""
Exchange connector interface for RAI-ALGO framework.
Exchange-agnostic abstraction for order execution and market data.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from rai_algo.data_types import MarketData, Position


@dataclass
class Order:
    """Order representation."""
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    order_type: str  # "MARKET", "LIMIT", "STOP", "STOP_LIMIT"
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"  # GTC, IOC, FOK
    order_id: Optional[str] = None
    status: str = "PENDING"  # PENDING, FILLED, PARTIALLY_FILLED, CANCELLED, REJECTED
    filled_quantity: float = 0.0
    average_fill_price: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class Balance:
    """Account balance."""
    currency: str
    available: float
    locked: float
    total: float


class BaseExchange(ABC):
    """
    Base class for exchange connectors.
    
    Subclasses should implement:
    - get_market_data(): Fetch current market data
    - place_order(): Execute orders
    - get_position(): Get current position for a symbol
    - get_balance(): Get account balance
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize exchange connector.
        
        Args:
            name: Exchange name
            config: Exchange configuration (API keys, endpoints, etc.)
        """
        self.name = name
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """Validate exchange configuration."""
        required_keys = ["api_key", "api_secret"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
    
    @abstractmethod
    def get_market_data(self, symbol: str) -> MarketData:
        """
        Fetch current market data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            
        Returns:
            MarketData object
        """
        pass
    
    @abstractmethod
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
        Place an order on the exchange.
        
        Args:
            symbol: Trading pair symbol
            side: "BUY" or "SELL"
            quantity: Order quantity
            order_type: Order type (MARKET, LIMIT, STOP, STOP_LIMIT)
            price: Limit price (for LIMIT orders)
            stop_price: Stop price (for STOP orders)
            
        Returns:
            Order object
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str, symbol: str) -> Order:
        """
        Get order status.
        
        Args:
            order_id: Order ID
            symbol: Trading pair symbol
            
        Returns:
            Order object with current status
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get current position for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Position object if position exists, None otherwise
        """
        pass
    
    @abstractmethod
    def get_balance(self, currency: str = "USDT") -> Balance:
        """
        Get account balance.
        
        Args:
            currency: Currency symbol (default: USDT)
            
        Returns:
            Balance object
        """
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get all open orders.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open Order objects
        """
        pass
    
    def health_check(self) -> bool:
        """
        Check exchange connectivity.
        
        Returns:
            True if exchange is reachable, False otherwise
        """
        try:
            # Try to fetch balance as a connectivity test
            self.get_balance()
            return True
        except Exception:
            return False

