# AI Trading Terminal - User Guide

## Overview

The AI Trading Terminal is a comprehensive, institutional-grade control center for managing and monitoring AI trading agents. It provides real-time visualization of agent decisions, strategy controls, and performance analytics.

## Features

### 1. Global Control Bar
- **Agent Status**: Toggle the AI agent ON/OFF
- **Mode Selection**: Switch between OFF, DEMO, and LIVE modes
- **Environment Indicator**: Shows testnet vs mainnet status
- **Connection Status**: Real-time WebSocket connection indicator
- **Wallet Information**: Balance, margin usage, and PnL at a glance
- **Emergency Stop**: Immediate shutdown button (visible in LIVE mode)

### 2. Annotated Price Chart
- **Professional Trading Charts**: Built with TradingView's lightweight-charts
- **Agent Annotations**: Visual markers for:
  - Entry points
  - Exit points
  - Take Profit (TP) levels
  - Stop Loss (SL) levels
  - Target prices
  - Price regions/zones
- **Strategy Filtering**: View annotations filtered by specific strategy
- **Toggle Annotations**: Show/hide agent markers for chart clarity

### 3. Brain Feed Panel
Real-time stream of agent reasoning and decisions:
- **Analysis**: Market context and analysis
- **Signals**: Trading signals detected
- **Decisions**: Trade entry/exit decisions with reasoning
- **Trades**: Actual trade executions
- **Adjustments**: Parameter or position adjustments
- **Warnings**: Risk warnings and system alerts

### 4. Strategy Control Panel
Complete strategy management:
- **Strategy List**: All configured strategies with status
- **Mode Control**: Per-strategy OFF/DEMO/LIVE switching
- **Status Indicators**: Real-time status (idle, scanning, in-position, cooling-down)
- **Exposure Tracking**: Current position exposure per strategy
- **Performance Metrics**: Recent PnL for each strategy
- **Quick Actions**: Edit parameters, trigger backtests

### 5. Agent Interaction Panel
Chat-style interface for communicating with the AI agent:
- **Command Input**: Send instructions and questions
- **Response History**: Full conversation log with timestamps
- **Status Indicators**: Shows when agent is processing commands
- **Structured Responses**: Agent explanations and confirmations

### 6. Performance Comparison
Side-by-side comparison across trading modes:
- **BACKTEST**: Historical performance from backtests
- **DEMO**: Paper trading performance on live prices
- **LIVE**: Real trading performance
- **Metrics Comparison**: Sharpe ratio, drawdown, CAGR, win rate
- **Equity Curves**: Visual comparison of equity evolution

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Global Control Bar (Agent Status, Wallet, Emergency Stop) │
├──────────┬─────────────────────────────────────┬────────────┤
│          │                                     │            │
│Strategy  │      Annotated Price Chart          │  Agent     │
│Control   │      (with TP/SL/Entry markers)     │Interaction │
│Panel     │                                     │            │
│          │                                     ├────────────┤
│          │      Brain Feed (Agent Reasoning)   │Performance │
│          │                                     │Comparison  │
│          │                                     │            │
└──────────┴─────────────────────────────────────┴────────────┘
```

## Usage Guide

### Starting the Terminal

1. Navigate to `/terminal` in the dashboard
2. The terminal loads with mock data by default
3. Connect to backend API by setting `NEXT_PUBLIC_API_URL` environment variable

### Enabling Real-Time Updates

The terminal uses WebSockets for real-time updates:
- **WebSocket URL**: Automatically connects to `ws://localhost:8000/ws/terminal` (or configured API URL)
- **Connection Status**: Shown in the global control bar
- **Auto-Reconnect**: Automatically reconnects if connection is lost

### Controlling the Agent

1. **Toggle Agent**: Click the ON/OFF button in the control bar
2. **Select Mode**: Use the mode dropdown to switch between OFF, DEMO, and LIVE
3. **Warning**: LIVE mode uses real funds - use with caution!

### Managing Strategies

1. **View Strategies**: All strategies listed in the left panel
2. **Change Mode**: Select mode from dropdown for each strategy
3. **Edit Parameters**: Click settings icon to modify strategy parameters
4. **Run Backtest**: Click "Backtest" button to trigger historical backtest

### Interpreting Chart Annotations

- **Green Up Arrow**: Entry point
- **Red Down Arrow**: Exit point
- **Blue Circle**: Take Profit level
- **Orange Square**: Stop Loss level
- **Purple Circle**: Target price
- **Colored Lines**: Price regions/zones of interest

### Using Agent Interaction

1. Type a command or question in the input field
2. Examples:
   - "Explain your current position in BTC"
   - "Run a backtest for MA Cross strategy"
   - "Adjust stop loss for ETH position to 2%"
   - "What signals are you seeing right now?"
3. Agent responds with detailed explanations and confirms actions

## API Integration

### Backend Endpoints Expected

The terminal expects the following backend API endpoints:

```
GET  /api/terminal/agent/status          - Get agent status
POST /api/terminal/agent/mode            - Update agent mode
GET  /api/terminal/wallet                - Get wallet information
GET  /api/terminal/chart/data            - Get OHLCV data
GET  /api/terminal/chart/annotations     - Get chart annotations
GET  /api/terminal/brain-feed            - Get brain feed entries
GET  /api/terminal/strategies            - Get strategy controls
POST /api/terminal/strategies/:name/mode - Update strategy mode
POST /api/terminal/agent/command         - Send command to agent
GET  /api/terminal/performance           - Get performance comparison

WebSocket: ws://api/ws/terminal          - Real-time updates
```

### WebSocket Message Format

The terminal expects WebSocket messages in the following format:

```json
{
  "type": "brain_feed" | "annotation" | "chart_update" | "agent_status" | 
          "wallet_update" | "strategy_update" | "command_response",
  "entry": { ... },           // For brain_feed
  "annotation": { ... },      // For annotation
  "candle": { ... },          // For chart_update
  "status": { ... },          // For agent_status
  "wallet": { ... },          // For wallet_update
  "strategy": { ... },        // For strategy_update
  "command": { ... }          // For command_response
}
```

## Safety Features

1. **Mode Indication**: Clear visual indicators for OFF/DEMO/LIVE modes
2. **Environment Badge**: Testnet vs mainnet clearly displayed
3. **Emergency Stop**: One-click emergency shutdown (LIVE mode only)
4. **Confirmation Dialogs**: Mode changes to LIVE require confirmation
5. **Audit Logging**: All mode changes and commands are logged

## Customization

### Styling

The terminal uses the dark theme by default. All components use shadcn/ui and can be customized via:
- Tailwind CSS classes
- Component props
- Theme configuration

### Chart Customization

The annotated chart component accepts:
- Custom symbol names
- Annotation filtering
- Height adjustment
- Show/hide annotations toggle

### Performance Views

The performance comparison can be filtered by:
- Strategy name
- Time range
- Trading mode (BACKTEST/DEMO/LIVE)

## Development Notes

- All components are in `components/terminal/`
- Types are defined in `lib/types.ts`
- API client functions in `lib/api-terminal.ts`
- WebSocket hook in `hooks/use-websocket.ts`
- Main terminal page at `app/terminal/page.tsx`

## Future Enhancements

- Multi-symbol chart support
- Advanced annotation editing
- Strategy parameter optimization UI
- Risk management dashboard
- Order flow visualization
- Sentiment analysis overlay

