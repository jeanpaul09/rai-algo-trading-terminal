# 🚀 Quick Start - RAI-ALGO Quant Lab Dashboard

## Launch the Dashboard (3 Steps)

### Option 1: Dashboard Only (Mock Data) - Fastest

```bash
cd ui/web
npm install
npm run dev
```

Open **http://localhost:3001** - Works immediately with mock data!

### Option 2: Full Stack (Dashboard + API)

**Terminal 1 - Start Python API:**
```bash
python api_server.py
# Runs on http://localhost:8000
```

**Terminal 2 - Start Dashboard:**
```bash
cd ui/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

### Option 3: One-Click Launch Script

```bash
./launch_dashboard.sh
```

This starts both the Python API server and the Next.js dashboard automatically.

## What You Get

✅ **Lab Dashboard** (`/`) - Overview with KPIs, equity curves, risk metrics  
✅ **Strategy Lab** (`/strategies`) - Browse and filter strategies  
✅ **Experiment Lab** (`/experiments`) - View backtest results  
✅ **Live Trading Lab** (`/live`) - Monitor live positions and risk  

## Next Steps

1. **Connect Real Data**: Update `api_server.py` to load actual RAI-ALGO data
2. **Customize**: Adjust colors, add features, modify layouts
3. **Deploy**: Build for production with `npm run build`

## Troubleshooting

- **Port 3001 in use?** Change port in `ui/web/package.json`
- **API not connecting?** Check Python server is running on port 8000
- **Missing dependencies?** Run `npm install` in `ui/web`

## Documentation

- Full guide: `ui/web/README.md`
- File structure: `ui/web/STRUCTURE.md`
- Launch details: `ui/web/LAUNCH.md`


