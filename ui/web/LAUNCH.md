# Launch Guide - RAI-ALGO Quant Lab Dashboard

## Quick Start (Mock Data Mode)

The dashboard works immediately with mock data - no backend required!

```bash
cd ui/web
npm install
npm run dev
```

Open http://localhost:3001 in your browser.

## Full Launch (With Python Backend)

### Step 1: Start Python API Server

The Python backend should expose REST API endpoints. See `../api_server.py` for a FastAPI stub.

```bash
# From project root
python api_server.py
# Server runs on http://localhost:8000
```

### Step 2: Start Dashboard

```bash
cd ui/web
npm install
npm run dev
```

### Step 3: Configure API URL (Optional)

If your Python API runs on a different port, set the environment variable:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Or create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production Build

```bash
cd ui/web
npm run build
npm start
```

## Troubleshooting

### Port Already in Use

If port 3001 is taken, modify `package.json`:

```json
"dev": "next dev -p 3002"
```

### API Connection Issues

- Check Python server is running: `curl http://localhost:8000/api/overview`
- Verify CORS is enabled on Python backend
- Check browser console for errors

### Missing Dependencies

```bash
cd ui/web
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. ✅ Dashboard launches with mock data
2. 🔄 Connect to Python backend (update `lib/api.ts`)
3. 🚀 Deploy to production


