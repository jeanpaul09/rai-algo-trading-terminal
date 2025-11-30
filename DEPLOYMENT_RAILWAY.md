# Railway Deployment Guide

## Quick Deploy (Web Interface)

Since Railway CLI requires admin access, use the web interface:

### Step 1: Go to Railway
1. Visit https://railway.app
2. Sign up/Login with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose repository: `jeanpaul09/rai-algo-trading-terminal`
4. Railway will detect it's a Python project

### Step 3: Configure Service
Railway should auto-detect, but verify:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python api_server.py`
- **Root Directory**: `/` (root)

### Step 4: Add Environment Variables
Go to "Variables" tab and add:

**Required:**
```
PORT=8000
```

**Optional (for live trading):**
```
HYPERLIQUID_PRIVATE_KEY=your_key_here
HYPERLIQUID_ADDRESS=your_address_here
CLAUDE_API_KEY=your_claude_api_key_here
```

### Step 5: Deploy
1. Railway will automatically start deploying
2. Wait for deployment (usually 2-5 minutes)
3. Click on the service → Settings → Generate Domain
4. Copy your Railway URL (e.g., `https://rai-algo-api.up.railway.app`)

### Step 6: Update Vercel
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add/Update:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-railway-url.up.railway.app`
5. Go to Deployments → Redeploy (or it will auto-redeploy)

## Using Railway CLI (Alternative)

If you have Railway CLI installed:

```bash
# Login
railway login

# Initialize
railway init

# Link to existing project or create new
railway link

# Set variables
railway variables set PORT=8000
railway variables set HYPERLIQUID_PRIVATE_KEY=your_key

# Deploy
railway up
```

## Verification

After deployment:

1. **Test Railway API:**
   ```bash
   curl https://your-railway-url.up.railway.app/api/overview
   ```

2. **Check Vercel terminal:**
   - Visit your Vercel URL: `/terminal`
   - Check browser console for API connection
   - Should connect to Railway backend

3. **Monitor Railway:**
   - Go to Railway dashboard
   - Check logs for any errors
   - Monitor resource usage

## Troubleshooting

**Build fails?**
- Check `requirements.txt` has all dependencies
- Verify Python version (3.11 recommended)

**API not connecting?**
- Check Railway URL is correct in Vercel env vars
- Verify CORS settings in `api_server.py`
- Check Railway logs for errors

**WebSocket not working?**
- Railway supports WebSockets on all plans
- Check Railway logs for WebSocket errors
- Verify WebSocket URL in frontend code

