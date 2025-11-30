# Force Vercel Rebuild

The terminal page is still showing cached errors. Here's how to force a fresh build:

## Option 1: Vercel Dashboard (Recommended)

1. Go to your Vercel dashboard
2. Find the deployment
3. Click "Redeploy" → "Redeploy with existing Build Cache: OFF"
4. This forces a completely fresh build

## Option 2: Clear Build Cache

Add this to `vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install"
}
```

## Option 3: Hard Refresh Browser

1. Open terminal page
2. Press `Cmd + Shift + R` (hard refresh on Mac Chrome)
3. Or clear cache: Chrome → Settings → Privacy → Clear browsing data → Cached images and files

## What's Fixed in Code

✅ Chart component now ONLY uses `addSeries('Candlestick', {...})` - the correct v5 API
✅ Removed all references to `addCandlestickSeries`
✅ Added error handling so page works even if chart fails
✅ Added debug logging to see what's happening

## After Rebuild

Check console for:
- `✅ Using addSeries (v5.0.9 API) - correct method` = Success!
- Any error messages = Tell me what you see

