#!/bin/bash

# Start Simple API Server - NO SETUP REQUIRED

echo "🚀 Starting Simple RAI-ALGO API Server..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Install requests if needed (silently)
python3 -c "import requests" 2>/dev/null || {
    echo "📦 Installing requests..."
    pip3 install requests fastapi uvicorn --quiet
}

# Kill existing server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1

# Start server
echo "🐍 Starting API server on port 8000..."
cd "$(dirname "$0")"
python3 api_server_simple.py


