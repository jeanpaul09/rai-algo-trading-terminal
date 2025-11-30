# Vercel Environment Variables Setup

## Required Environment Variable

The frontend needs to know where the backend is running:

```
NEXT_PUBLIC_API_URL=https://web-production-e9cd4.up.railway.app
```

## How to Set in Vercel

1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://web-production-e9cd4.up.railway.app`
   - **Environment**: Production, Preview, Development (all)
5. Click **Save**
6. **Redeploy** the application

## Verify It's Set

After redeploy, check the browser console:
- Should see: "✅ Loaded REAL chart data from backend: X candles"
- Should NOT see: "⚠️ No backend URL - using mock data"

## Current Status

- ✅ Backend: Railway (https://web-production-e9cd4.up.railway.app)
- ✅ APIs: Hyperliquid + Kraken (no geo restrictions)
- ⏳ Frontend: Needs `NEXT_PUBLIC_API_URL` set in Vercel

