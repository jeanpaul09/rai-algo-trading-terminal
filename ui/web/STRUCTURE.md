# RAI-ALGO Quant Lab Dashboard - File Structure

## Complete File & Route Structure

```
ui/web/
├── app/
│   ├── layout.tsx                    # Root layout with sidebar
│   ├── page.tsx                      # Main Lab Dashboard
│   ├── globals.css                   # Global styles (dark theme)
│   ├── strategies/
│   │   ├── page.tsx                  # Strategy Lab: list + filters
│   │   └── [name]/
│   │       └── page.tsx              # Strategy Detail Lab
│   ├── experiments/
│   │   ├── page.tsx                  # Backtest / experiment catalog
│   │   └── [id]/
│   │       └── page.tsx              # Experiment Detail & Comparison
│   └── live/
│       └── page.tsx                  # Live Trading Lab
│
├── components/
│   ├── layout/
│   │   ├── sidebar.tsx               # Left navigation sidebar
│   │   └── topbar.tsx                # Top bar with title and date
│   ├── cards/
│   │   ├── metric-card.tsx           # Metric display card
│   │   └── kpi-card.tsx              # KPI card with trend indicators
│   ├── charts/
│   │   ├── equity-curve.tsx          # Equity curve line chart
│   │   ├── drawdown-curve.tsx        # Drawdown area chart
│   │   ├── distribution-chart.tsx    # Return distribution histogram
│   │   └── correlation-matrix.tsx    # Strategy correlation heatmap
│   ├── tables/
│   │   ├── strategies-table.tsx       # Strategies data table
│   │   └── experiments-table.tsx     # Experiments data table
│   ├── lab/
│   │   ├── performance-panel.tsx     # Performance charts panel
│   │   ├── risk-panel.tsx            # Risk metrics and correlation
│   │   └── experiments-panel.tsx     # Recent experiments panel
│   └── ui/                           # shadcn/ui components
│       ├── card.tsx
│       ├── badge.tsx
│       ├── button.tsx
│       ├── tabs.tsx
│       ├── table.tsx
│       ├── select.tsx
│       └── input.tsx
│
└── lib/
    ├── api.ts                        # Typed API client helpers
    ├── types.ts                      # Shared TypeScript types
    └── utils.ts                      # Utility functions (cn)
```

## Routes

- `/` - Main Lab Dashboard
  - KPI cards (Total Strategies, Deployed, Best Sharpe, Worst DD, Daily PnL)
  - Equity curve and drawdown charts
  - Recent experiments table
  - Risk snapshot panel

- `/strategies` - Strategy Lab
  - Table of all strategies with filters
  - Filter by market, status, performance

- `/strategies/[name]` - Strategy Detail Lab
  - Overview with metrics
  - Performance tab (equity, drawdown, distribution charts)
  - Experiments tab (table of backtests)

- `/experiments` - Experiment Lab
  - Table of all experiments
  - Filter by strategy, date range, status

- `/experiments/[id]` - Experiment Detail
  - Summary metrics
  - Equity curve
  - Drawdown curve
  - Return distribution
  - Parameters

- `/live` - Live Trading Lab
  - Live PnL & Equity chart
  - Open positions table
  - Risk status indicators
  - Venue overview cards

## Key Components

### Charts (Recharts)
- **EquityCurve**: Line chart showing equity over time
- **DrawdownCurve**: Area chart showing drawdown periods
- **DistributionChart**: Histogram of return distribution
- **CorrelationMatrixChart**: Heatmap-style correlation matrix

### Cards
- **MetricCard**: Simple metric display with optional change indicator
- **KPICard**: KPI with trend icon (up/down/neutral)

### Tables
- **StrategiesTable**: Displays strategies with markets, state, metrics, tags
- **ExperimentsTable**: Displays experiments with strategy, market, period, metrics

### Lab Panels
- **PerformancePanel**: Combines equity and drawdown charts
- **RiskPanel**: Risk status, market exposure, correlation matrix
- **ExperimentsPanel**: Recent experiments table

## API Integration

All API calls are in `lib/api.ts` with typed interfaces in `lib/types.ts`.

Currently uses mock data for development. Replace mock implementations with actual API calls when backend is ready.

## Styling

- Dark theme by default
- Uses Tailwind CSS with custom color tokens
- Professional, minimal aesthetic
- High information density without clutter


