#!/bin/bash

# Start Everything - API Server + Dashboard with Real Data

echo "🚀 Starting RAI-ALGO with REAL Data..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Install Python deps if needed
python3 -c "import requests, fastapi, uvicorn" 2>/dev/null || {
    echo "📦 Installing Python dependencies..."
    pip3 install requests fastapi uvicorn
}

# Kill existing processes on ports
echo "🧹 Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
sleep 1

# Start API server
echo "🐍 Starting API server (port 8000)..."
cd "$(dirname "$0")"
python3 api_server.py &
API_PID=$!
sleep 3

# Verify API is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ API server is running"
else
    echo "❌ API server failed to start"
    exit 1
fi

# Start dashboard
echo "⚛️  Starting dashboard (port 3001)..."
cd ui/web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev &
DASHBOARD_PID=$!

cd ../..

echo ""
echo "✅ Everything started!"
echo ""
echo "📊 Dashboard: http://localhost:3001"
echo "🔌 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "✨ Real Data Sources:"
echo "   - Market Data: Binance Public API"
echo "   - Liquidations: Binance Futures API"
echo "   - All data is REAL (no mocks)"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $API_PID $DASHBOARD_PID 2>/dev/null; exit" INT TERM
wait


