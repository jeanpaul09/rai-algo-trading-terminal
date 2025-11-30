#!/bin/bash

# Launch script for RAI-ALGO Quant Lab Dashboard
# This script starts both the Python API server and the Next.js dashboard

set -e

echo "🚀 Launching RAI-ALGO Quant Lab Dashboard..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm"
    exit 1
fi

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate 2>/dev/null || true
pip install -q fastapi uvicorn 2>/dev/null || pip install fastapi uvicorn

# Install Node.js dependencies if needed
if [ ! -d "ui/web/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd ui/web
    npm install
    cd ../..
fi

echo ""
echo "✅ Dependencies installed"
echo ""

# Start Python API server in background
echo "🐍 Starting Python API server on port 8000..."
python3 api_server.py &
API_PID=$!

# Wait a moment for API server to start
sleep 2

# Start Next.js dashboard
echo "⚛️  Starting Next.js dashboard on port 3001..."
cd ui/web
npm run dev &
DASHBOARD_PID=$!

cd ../..

echo ""
echo "✅ Dashboard launched!"
echo ""
echo "📊 Dashboard: http://localhost:3001"
echo "🔌 API Server: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $API_PID $DASHBOARD_PID 2>/dev/null; exit" INT TERM
wait


