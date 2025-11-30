#!/bin/bash

# Start RAI-ALGO Dashboard with Real Data

echo "🚀 Starting RAI-ALGO Dashboard with Real Market Data..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Install Python dependencies if needed
echo "📦 Checking Python dependencies..."
python3 -c "import requests, fastapi, uvicorn" 2>/dev/null || {
    echo "Installing Python dependencies..."
    pip3 install requests fastapi uvicorn
}

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Install Node dependencies if needed
if [ ! -d "ui/web/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd ui/web
    npm install
    cd ../..
fi

echo ""
echo "✅ Dependencies ready"
echo ""

# Start API server
echo "🐍 Starting Python API server (real market data)..."
cd "$(dirname "$0")"
python3 api_server.py &
API_PID=$!
sleep 2

# Start dashboard
echo "⚛️  Starting Next.js dashboard..."
cd ui/web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev &
DASHBOARD_PID=$!

cd ../..

echo ""
echo "✅ Both servers started!"
echo ""
echo "📊 Dashboard: http://localhost:3001"
echo "🔌 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "✨ Features:"
echo "   - Real market data from Binance"
echo "   - Liquidations viewer (see sidebar)"
echo "   - Run Backtest button on strategy pages"
echo "   - Real-time position tracking"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $API_PID $DASHBOARD_PID 2>/dev/null; exit" INT TERM
wait


