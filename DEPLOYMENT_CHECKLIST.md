# ✅ Deployment Checklist - Trading Terminal

## Backend Changes (Railway)
✅ **All changes made to `api_server.py`** (this is what Railway uses)

### Files Modified:
1. ✅ `api_server.py` - Main backend server
   - Added DemoTrader import and integration
   - Added demo trading endpoints
   - Added WebSocket support
   - Added performance tracking endpoints
   - Fixed async callback handling

2. ✅ `rai_algo/demo_trader.py` - NEW FILE
   - Complete demo trading engine
   - Must be deployed to Railway

3. ✅ `rai_algo/__init__.py` - Updated exports
   - Added DemoTrader and DemoTraderConfig exports

### Verification Steps:
1. ✅ Check `railway.json` - Uses `api_server.py` ✓
2. ✅ Check `Procfile` - Uses `api_server.py` ✓
3. ✅ All imports should work on Railway

## Frontend Changes (Vercel)
✅ **All changes made to `ui/web/app/terminal/page.tsx`**

### Files Modified:
1. ✅ `ui/web/app/terminal/page.tsx`
   - Fixed layout (h-screen)
   - Added performance data loading
   - Added real-time refresh

2. ✅ `ui/web/lib/api-terminal.ts`
   - Already has `fetchPerformanceComparison` function

### Verification Steps:
1. ✅ Terminal page should render correctly
2. ✅ Performance panel should load data
3. ✅ All API calls should work

## After Deployment

### Test Backend Endpoints:
```bash
# Test agent status
curl https://YOUR_RAILWAY_URL.railway.app/api/terminal/status

# Test strategies
curl https://YOUR_RAILWAY_URL.railway.app/api/terminal/strategies

# Test performance
curl https://YOUR_RAILWAY_URL.railway.app/api/terminal/performance

# Test annotations
curl https://YOUR_RAILWAY_URL.railway.app/api/terminal/chart/annotations

# Test brain feed
curl https://YOUR_RAILWAY_URL.railway.app/api/terminal/brain-feed
```

### Test Frontend:
1. Go to `/terminal` page
2. Check browser console for any errors
3. Verify:
   - Chart loads
   - Strategies list loads
   - Performance panel loads (may be empty initially)
   - Brain feed loads (may be empty initially)

### Start Demo Trading:
1. Set agent mode to "DEMO"
2. Change a strategy mode to "DEMO"
3. Watch:
   - Chart should show annotations when trades occur
   - Brain feed should show agent decisions
   - Performance should update in real-time

## Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'rai_algo.demo_trader'"
**Fix**: Make sure `rai_algo/demo_trader.py` is committed and pushed to git

### Issue: "ImportError: cannot import name 'DemoTrader'"
**Fix**: Check that `rai_algo/__init__.py` exports DemoTrader

### Issue: Terminal page not loading
**Fix**: Check browser console for errors, verify `NEXT_PUBLIC_API_URL` is set in Vercel

### Issue: No data showing
**Fix**: 
1. Check Railway logs for errors
2. Verify backend is running
3. Check CORS settings
4. Verify API URLs are correct

### Issue: WebSocket not connecting
**Fix**:
1. Check WebSocket URL in browser console
2. Verify Railway allows WebSocket connections
3. Check firewall/proxy settings

## Deployment Commands

### Railway (Automatic):
- Push to git → Railway auto-deploys
- Check Railway dashboard for deployment status
- Check logs for any errors

### Manual Test Locally:
```bash
# Backend
python api_server.py

# Frontend (in ui/web)
npm run dev
```

## Status

✅ All backend code changes complete
✅ All frontend code changes complete
✅ Ready for deployment

**Next**: Push to git → Railway/Vercel will auto-deploy

