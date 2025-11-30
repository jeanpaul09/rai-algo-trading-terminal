# Bloomberg-Style Trading Dashboard

## ✅ What's Built

A professional Bloomberg Terminal-style dashboard with:

### 6 Main Tabs

1. **Overview** - High-level KPIs and performance summary
2. **Performance** - Detailed performance metrics and charts
3. **Market Positions** - See all traders' longs and shorts
4. **Advanced Charts** - Professional charts with multiple metrics
5. **Strategy Analytics** - Strategy rankings and comparisons
6. **Market Intelligence** - Liquidation analysis and market sentiment

## Features

### Bloomberg-Style Header
- Real-time BTC price display
- Data source indicator (REAL/MOCK)
- Active strategies count
- UTC timestamp

### Market Positions Tab
- **Total Long/Short Value** - See market-wide exposure
- **Long/Short Ratio** - Market sentiment indicator
- **Active Traders** - Number of active positions
- **Positions Table** - All open positions with:
  - Symbol, Side (LONG/SHORT)
  - Size, Entry Price, Current Price
  - Leverage, PnL, PnL %
- **Total Market PnL** - Aggregate PnL across all traders

### Advanced Charts Tab
- **Equity Curve** - Area chart with real data
- **Returns Distribution** - Bar chart of returns
- **Rolling Volatility** - 20-period volatility chart
- **Drawdown Analysis** - Drawdown visualization
- **Performance Metrics**:
  - Sharpe Ratio
  - Total Return
  - Max Drawdown
  - Annual Volatility

### Strategy Analytics Tab
- **Strategy Rankings** - Top 10 strategies by Sharpe
- **Performance Metrics** - Avg Sharpe, Win Rate
- **Risk Analysis** - Worst drawdown, best CAGR
- **Strategy Comparison Table** with:
  - Rank, Strategy Name
  - Sharpe, Sortino, Max DD, CAGR
  - Win Rate, Total Trades

### Market Intelligence Tab
- **Liquidation Metrics**:
  - Total liquidations (24h)
  - Long vs Short liquidations
  - Largest liquidation
- **Market Sentiment**:
  - Liquidation trend analysis
  - Long/Short ratio
  - Liquidation intensity
- **Recent Liquidations Table** - Real-time liquidation events

## Design Philosophy

- **Information Density** - Bloomberg-style high information density
- **Professional Aesthetics** - Dark theme, clean, minimal
- **Real-Time Updates** - Auto-refresh every 5-30 seconds
- **Color Coding**:
  - Green: Positive, Longs, Gains
  - Red: Negative, Shorts, Losses
  - Yellow: Warnings, Alerts

## Data Sources

- **Real Data**: CoinGecko API (BTC prices, market data)
- **Positions**: API endpoint `/api/positions`
- **Liquidations**: Binance Futures API
- **Auto-refresh**: Every 5-30 seconds depending on tab

## Usage

1. Start API server: `python3 api_server_simple.py`
2. Start dashboard: `cd ui/web && npm run dev`
3. Open: `http://localhost:3001`
4. Navigate tabs to see different views

## Next Level Features

- **Market Depth Visualization** - Order book analysis
- **Correlation Heatmaps** - Strategy correlations
- **Risk Decomposition** - Factor analysis
- **Portfolio Optimization** - Efficient frontier
- **Real-time Alerts** - Custom alert system
- **Backtesting Comparison** - Side-by-side strategy comparison

This is a professional-grade trading dashboard! 🚀


