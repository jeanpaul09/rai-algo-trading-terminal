"""
Example usage of Hyperliquid integration for RAI-ALGO.

This demonstrates:
1. Fetching historical OHLCV data for backtesting
2. Fetching funding rates
3. Instantiating HyperliquidExchange for live trading (paper mode)
"""
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rai_algo.data.sources.crypto.hyperliquid import fetch_ohlcv, fetch_funding_rates
from rai_algo.exchanges.hyperliquid import HyperliquidExchange


def example_fetch_historical_data():
    """Example: Fetch historical OHLCV data from Hyperliquid."""
    print("=" * 60)
    print("Example 1: Fetching Historical OHLCV Data")
    print("=" * 60)
    
    try:
        # Fetch BTC OHLCV data for the last 7 days, 1-hour timeframe
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"\nFetching BTC/USDT OHLCV data...")
        print(f"Timeframe: 1h")
        print(f"Date range: {start_date} to {end_date}")
        
        df = fetch_ohlcv(
            symbol="BTC",
            timeframe="1h",
            start=start_date,
            end=end_date,
            use_cache=True,
            use_polars=False,
        )
        
        print(f"\n✅ Successfully fetched {len(df)} bars")
        print("\nFirst few rows:")
        print(df.head())
        print("\nLast few rows:")
        print(df.tail())
        print(f"\nData shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"\n❌ Error fetching historical data: {e}")
        print("\nNote: This may fail if Hyperliquid API structure differs.")
        print("Adjust the API endpoints in hyperliquid.py based on official docs.")
        return None


def example_fetch_funding_rates():
    """Example: Fetch funding rate data from Hyperliquid."""
    print("\n" + "=" * 60)
    print("Example 2: Fetching Funding Rates")
    print("=" * 60)
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"\nFetching BTC funding rates...")
        print(f"Date range: {start_date} to {end_date}")
        
        df = fetch_funding_rates(
            symbol="BTC",
            start=start_date,
            end=end_date,
            use_cache=True,
            use_polars=False,
        )
        
        print(f"\n✅ Successfully fetched {len(df)} funding rate records")
        if len(df) > 0:
            print("\nFirst few rows:")
            print(df.head())
        else:
            print("\n⚠️  No funding rate data returned")
        
        return df
        
    except Exception as e:
        print(f"\n❌ Error fetching funding rates: {e}")
        print("\nNote: This may fail if Hyperliquid API structure differs.")
        return None


def example_live_trading_setup():
    """Example: Setup HyperliquidExchange for live trading."""
    print("\n" + "=" * 60)
    print("Example 3: Setting Up HyperliquidExchange")
    print("=" * 60)
    
    # Check if credentials are set
    private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    address = os.getenv("HYPERLIQUID_ADDRESS")
    
    if not private_key:
        print("\n⚠️  HYPERLIQUID_PRIVATE_KEY not set in environment")
        print("   Set it with: export HYPERLIQUID_PRIVATE_KEY='your_key'")
        print("\n   For testing, you can still instantiate the exchange,")
        print("   but trading operations will fail without credentials.")
        print("\n   Creating exchange instance in read-only mode...")
    else:
        print("\n✅ HYPERLIQUID_PRIVATE_KEY found")
    
    try:
        # Create exchange instance
        # If no private key, it will work for read-only operations
        exchange = HyperliquidExchange(config={
            "private_key": private_key,
            "address": address,
            "testnet": os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true",
        })
        
        print(f"\n✅ Exchange instance created: {exchange.name}")
        print(f"   Base URL: {exchange.base_url}")
        
        # Try to fetch market data (doesn't require auth)
        print("\nFetching market data for BTC...")
        try:
            market_data = exchange.get_market_data("BTC")
            print(f"✅ Market data fetched:")
            print(f"   Symbol: BTC")
            print(f"   Price: ${market_data.close:.2f}")
            print(f"   Timestamp: {market_data.timestamp}")
        except Exception as e:
            print(f"⚠️  Could not fetch market data: {e}")
            print("   This may be due to API endpoint differences.")
        
        # Try to fetch balance (requires auth)
        if private_key:
            print("\nFetching account balance...")
            try:
                balance = exchange.get_balance()
                print(f"✅ Balance fetched:")
                print(f"   Currency: {balance.currency}")
                print(f"   Available: {balance.available:.2f}")
                print(f"   Locked: {balance.locked:.2f}")
                print(f"   Total: {balance.total:.2f}")
            except Exception as e:
                print(f"⚠️  Could not fetch balance: {e}")
                print("   This may be due to authentication issues.")
        else:
            print("\n⚠️  Skipping balance fetch (no private key)")
        
        # Try to fetch positions (requires auth)
        if private_key:
            print("\nFetching positions...")
            try:
                position = exchange.get_position("BTC")
                if position:
                    print(f"✅ Position found:")
                    print(f"   Symbol: BTC")
                    print(f"   Size: {position.size:.6f}")
                    print(f"   Entry Price: ${position.entry_price:.2f}")
                    print(f"   Current Price: ${position.current_price:.2f}")
                else:
                    print("   No open position for BTC")
            except Exception as e:
                print(f"⚠️  Could not fetch positions: {e}")
        else:
            print("\n⚠️  Skipping position fetch (no private key)")
        
        print("\n" + "=" * 60)
        print("Example: Placing a Test Order (commented out for safety)")
        print("=" * 60)
        print("""
# To place a test order, uncomment the following:
# 
# order = exchange.place_order(
#     symbol="BTC",
#     side="BUY",
#     quantity=0.001,
#     order_type="MARKET",
# )
# print(f"Order placed: {order.order_id}")
# print(f"Status: {order.status}")
        """)
        
        return exchange
        
    except Exception as e:
        print(f"\n❌ Error setting up exchange: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Hyperliquid Integration Examples for RAI-ALGO")
    print("=" * 60)
    print("\nThis script demonstrates:")
    print("1. Fetching historical OHLCV data")
    print("2. Fetching funding rates")
    print("3. Setting up HyperliquidExchange for live trading")
    print("\nNote: Some operations may fail if the Hyperliquid API")
    print("      structure differs from the implementation.")
    print("      Adjust endpoints in hyperliquid.py as needed.")
    
    # Example 1: Historical data
    df_ohlcv = example_fetch_historical_data()
    
    # Example 2: Funding rates
    df_funding = example_fetch_funding_rates()
    
    # Example 3: Live trading setup
    exchange = example_live_trading_setup()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✅ Historical data fetch: {'Success' if df_ohlcv is not None else 'Failed'}")
    print(f"✅ Funding rates fetch: {'Success' if df_funding is not None else 'Failed'}")
    print(f"✅ Exchange setup: {'Success' if exchange is not None else 'Failed'}")
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Review the Hyperliquid API documentation")
    print("2. Adjust API endpoints in rai_algo/data/sources/crypto/hyperliquid.py")
    print("3. Adjust API endpoints in rai_algo/exchanges/hyperliquid.py")
    print("4. Set HYPERLIQUID_PRIVATE_KEY for live trading")
    print("5. Test with small amounts on testnet first")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()


