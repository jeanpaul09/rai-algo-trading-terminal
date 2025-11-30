"""
Terminal API endpoints for live trading terminal.
Handles agent commands, real-time updates via WebSocket, and trading control.
"""
import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import agent and trading modules
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  Anthropic not installed. Agent features will be limited.")

from rai_algo.exchanges.hyperliquid import HyperliquidExchange
from rai_algo.live_trader import LiveTrader, TraderConfig
from rai_algo.strategies.example_strategy import ExampleStrategy

app = FastAPI(title="RAI-ALGO Terminal API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
_active_traders: Dict[str, LiveTrader] = {}
_websocket_connections: List[WebSocket] = []
_agent_status = {
    "mode": "OFF",
    "isActive": False,
    "environment": os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true" and "testnet" or "mainnet",
    "connected": True,
    "lastUpdate": datetime.now().isoformat(),
}

# Initialize Anthropic client if available
anthropic_client = None
if ANTHROPIC_AVAILABLE:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        anthropic_client = Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")
    else:
        print("⚠️  ANTHROPIC_API_KEY not set. Agent features disabled.")


async def broadcast_to_clients(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients."""
    disconnected = []
    for connection in _websocket_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)
    for conn in disconnected:
        if conn in _websocket_connections:
            _websocket_connections.remove(conn)


@app.websocket("/ws/terminal")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time terminal updates."""
    await websocket.accept()
    _websocket_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle incoming messages
            msg_type = data.get("type")
            
            if msg_type == "set_agent_mode":
                mode = data.get("mode", "OFF")
                _agent_status["mode"] = mode
                _agent_status["isActive"] = mode != "OFF"
                _agent_status["lastUpdate"] = datetime.now().isoformat()
                
                await broadcast_to_clients({
                    "type": "agent_status",
                    "status": _agent_status
                })
                
            elif msg_type == "toggle_agent":
                _agent_status["isActive"] = not _agent_status["isActive"]
                if not _agent_status["isActive"]:
                    _agent_status["mode"] = "OFF"
                elif _agent_status["mode"] == "OFF":
                    _agent_status["mode"] = "DEMO"
                _agent_status["lastUpdate"] = datetime.now().isoformat()
                
                await broadcast_to_clients({
                    "type": "agent_status",
                    "status": _agent_status
                })
                
            elif msg_type == "emergency_stop":
                # Stop all traders
                for trader_id, trader in list(_active_traders.items()):
                    trader.stop()
                    del _active_traders[trader_id]
                
                _agent_status["mode"] = "OFF"
                _agent_status["isActive"] = False
                _agent_status["lastUpdate"] = datetime.now().isoformat()
                
                await broadcast_to_clients({
                    "type": "brain_feed",
                    "entry": {
                        "id": f"bf-{datetime.now().timestamp()}",
                        "timestamp": datetime.now().isoformat(),
                        "type": "risk_alert",
                        "summary": "EMERGENCY STOP activated. All strategies halted.",
                        "sentiment": "negative"
                    }
                })
                
            elif msg_type == "agent_command":
                command = data.get("command", "")
                command_id = data.get("commandId", "")
                
                # Process command with Anthropic
                response_text = "Command received but agent not configured."
                if anthropic_client:
                    try:
                        message = anthropic_client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1024,
                            messages=[{
                                "role": "user",
                                "content": f"""You are an AI trading agent controlling a crypto trading system.
Current status: {_agent_status['mode']} mode, Active: {_agent_status['isActive']}
User command: {command}

Respond professionally and helpfully. If the command involves trading actions, acknowledge and explain what you'll do."""
                            }]
                        )
                        response_text = message.content[0].text if message.content else "No response"
                    except Exception as e:
                        response_text = f"Error processing command: {str(e)}"
                
                await broadcast_to_clients({
                    "type": "command_response",
                    "commandId": command_id,
                    "command": {
                        "id": command_id,
                        "status": "completed",
                        "response": response_text
                    }
                })
                
            elif msg_type == "set_strategy_mode":
                strategy_name = data.get("strategyName")
                mode = data.get("mode", "OFF")
                # Handle strategy mode change
                await broadcast_to_clients({
                    "type": "strategy_update",
                    "strategy": {
                        "name": strategy_name,
                        "mode": mode
                    }
                })
                
    except WebSocketDisconnect:
        if websocket in _websocket_connections:
            _websocket_connections.remove(websocket)


@app.get("/api/terminal/status")
async def get_agent_status():
    """Get current agent status."""
    return _agent_status


@app.get("/api/terminal/wallet")
async def get_wallet_info():
    """Get wallet information from Hyperliquid."""
    try:
        exchange = HyperliquidExchange()
        
        # Get balance
        balance = exchange.get_balance("USDC")  # Hyperliquid uses USDC
        
        # Get positions
        positions = {}
        try:
            # This would fetch actual positions
            # For now, return basic info
            pass
        except:
            pass
        
        return {
            "address": os.getenv("HYPERLIQUID_ADDRESS", "Not set"),
            "balance": balance.total if balance else 0,
            "marginUsed": 0,  # Calculate from positions
            "marginAvailable": balance.available if balance else 0,
            "realizedPnL": 0,
            "unrealizedPnL": 0,
            "environment": _agent_status["environment"]
        }
    except Exception as e:
        return {
            "address": os.getenv("HYPERLIQUID_ADDRESS", "Not set"),
            "balance": 0,
            "marginUsed": 0,
            "marginAvailable": 0,
            "realizedPnL": 0,
            "unrealizedPnL": 0,
            "environment": _agent_status["environment"],
            "error": str(e)
        }


@app.post("/api/terminal/strategies/{strategy_name}/start")
async def start_strategy(strategy_name: str, mode: str = "DEMO"):
    """Start a trading strategy."""
    try:
        # Determine if dry_run based on mode
        dry_run = mode != "LIVE"
        
        # Get Hyperliquid exchange
        exchange = HyperliquidExchange()
        
        # Create strategy
        strategy = ExampleStrategy(parameters={})
        
        # Create trader config
        config = TraderConfig(
            symbol="BTC",
            strategy=strategy,
            exchange=exchange,
            dry_run=dry_run,
        )
        
        # Create and start trader
        trader = LiveTrader(config)
        trader.start()
        
        trader_id = f"{strategy_name}_{datetime.now().timestamp()}"
        _active_traders[trader_id] = trader
        
        await broadcast_to_clients({
            "type": "strategy_update",
            "strategy": {
                "name": strategy_name,
                "mode": mode,
                "status": "scanning"
            }
        })
        
        return {"success": True, "trader_id": trader_id, "status": "running"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/terminal/strategies/{strategy_name}/stop")
async def stop_strategy(strategy_name: str):
    """Stop a trading strategy."""
    traders_to_stop = [
        (tid, t) for tid, t in _active_traders.items()
        if tid.startswith(strategy_name)
    ]
    
    for trader_id, trader in traders_to_stop:
        trader.stop()
        del _active_traders[trader_id]
    
    await broadcast_to_clients({
        "type": "strategy_update",
        "strategy": {
            "name": strategy_name,
            "mode": "OFF",
            "status": "idle"
        }
    })
    
    return {"success": True}


@app.post("/api/terminal/agent/command")
async def send_agent_command(command: Dict[str, Any]):
    """Send a command to the AI agent."""
    cmd_text = command.get("command", "")
    
    if not anthropic_client:
        return {
            "id": f"cmd-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "command": cmd_text,
            "status": "failed",
            "response": "Anthropic API not configured. Set ANTHROPIC_API_KEY."
        }
    
    try:
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""You are an AI trading agent for a crypto perpetual trading system on Hyperliquid.
Current status: {_agent_status['mode']} mode, Active: {_agent_status['isActive']}

User command: {cmd_text}

Respond helpfully. If the command involves trading actions, explain what you'll do and confirm."""
            }]
        )
        
        response_text = message.content[0].text if message.content else "No response"
        
        # Broadcast to WebSocket clients
        await broadcast_to_clients({
            "type": "brain_feed",
            "entry": {
                "id": f"bf-{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat(),
                "type": "agent_message",
                "summary": f"Agent response: {response_text[:100]}..."
            }
        })
        
        return {
            "id": f"cmd-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "command": cmd_text,
            "status": "completed",
            "response": response_text
        }
    except Exception as e:
        return {
            "id": f"cmd-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "command": cmd_text,
            "status": "failed",
            "response": f"Error: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Terminal API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

