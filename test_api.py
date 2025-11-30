#!/usr/bin/env python3
"""
Quick test script to verify API server works with real data
"""

import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing RAI-ALGO API Server...")
    print()
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        r = requests.get(f"{API_URL}/", timeout=5)
        print(f"   ✅ {r.json()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: Market data
    print("\n2. Testing real market data...")
    try:
        r = requests.get(f"{API_URL}/api/market/data?symbol=BTC/USDT&days=7", timeout=10)
        data = r.json()
        print(f"   ✅ Got {data['data_points']} data points")
        if data['data']:
            print(f"   ✅ Latest price: ${data['data'][-1]['close']:,.2f}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Liquidations
    print("\n3. Testing liquidations data...")
    try:
        r = requests.get(f"{API_URL}/api/liquidations?exchange=binance", timeout=10)
        data = r.json()
        print(f"   ✅ Got {len(data.get('liquidations', []))} liquidations")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Overview
    print("\n4. Testing overview...")
    try:
        r = requests.get(f"{API_URL}/api/overview", timeout=10)
        data = r.json()
        print(f"   ✅ Strategies: {data.get('total_strategies', 0)}")
        print(f"   ✅ Equity curve points: {len(data.get('latest_equity_curve', []))}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n✅ API tests complete!")
    return True

if __name__ == "__main__":
    test_api()


