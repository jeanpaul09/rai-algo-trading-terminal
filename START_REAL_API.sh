#!/bin/bash

# Start API Server with Real Data
# This script ensures the API server is running and serving REAL data from Binance

echo "🚀 Starting RAI-ALGO API Server with REAL Market Data..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check if requests is installed
python3 -c "import requests" 2>/dev/null || {
    echo "📦 Installing Python dependencies..."
    pip3 install requests fastapi uvicorn
}

# Check if port 8000 is in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8000 is already in use"
    echo "   Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Start API server
echo "🐍 Starting API server on port 8000..."
cd "$(dirname "$0")"
python3 api_server.py


