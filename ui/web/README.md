# RAI-ALGO Quant Lab Dashboard

A modern quant lab / trading dashboard for the RAI-ALGO system built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui.

## Features

- **Lab Dashboard**: Central control center with KPIs, equity curves, and risk metrics
- **Strategy Lab**: Browse, filter, and inspect individual strategies
- **Experiment Lab**: View and compare backtest experiments
- **Live Trading Lab**: Monitor live positions, risk status, and venue overview

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Charts**: Recharts
- **Icons**: Lucide React

## Getting Started

### Quick Launch (Mock Data Mode)

The dashboard works immediately with mock data - no backend required!

```bash
cd ui/web
npm install
npm run dev
```

Open **http://localhost:3001** in your browser.

### Full Launch (With Python Backend)

1. **Start Python API Server** (from project root):
   ```bash
   python api_server.py
   # Server runs on http://localhost:8000
   ```

2. **Start Dashboard** (with API connection):
   ```bash
   cd ui/web
   npm install
   NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
   ```

3. **Or use the launch script** (from project root):
   ```bash
   ./launch_dashboard.sh
   ```

The dashboard automatically falls back to mock data if the API server is not available.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
ui/web/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout with sidebar
│   ├── page.tsx           # Main dashboard
│   ├── strategies/        # Strategy pages
│   ├── experiments/       # Experiment pages
│   └── live/              # Live trading page
├── components/
│   ├── cards/             # Metric and KPI cards
│   ├── charts/            # Chart components (equity, drawdown, etc.)
│   ├── lab/               # Lab panel components
│   ├── layout/            # Sidebar and topbar
│   ├── tables/            # Data tables
│   └── ui/                # shadcn/ui components
└── lib/
    ├── api.ts             # Typed API client
    ├── types.ts           # TypeScript types
    └── utils.ts           # Utility functions
```

## API Integration

The dashboard expects a Python backend API running on `http://localhost:8000` (configurable via `NEXT_PUBLIC_API_URL`).

### Expected Endpoints

- `GET /api/overview` - Dashboard overview data
- `GET /api/strategies` - List all strategies
- `GET /api/strategies/{name}` - Get strategy details
- `GET /api/strategies/{name}/experiments` - Get strategy experiments
- `GET /api/experiments` - List all experiments
- `GET /api/experiments/{id}` - Get experiment details
- `GET /api/live/status` - Live trading status

Currently, the API client includes mock data for development. Replace the mock implementations in `lib/api.ts` with actual API calls when the backend is ready.

## Design

- **Theme**: Dark mode by default
- **Aesthetics**: Clean, minimal, professional trading lab aesthetic
- **Information Density**: High without feeling cluttered
- **Color Palette**: Subtle grays with minimal accent colors

## Development Notes

- All components are typed with TypeScript
- Server components are used for data fetching where possible
- Client components are used for interactive charts and UI
- Mock data is provided for development and testing

## License

Private project - RAI-ALGO System

