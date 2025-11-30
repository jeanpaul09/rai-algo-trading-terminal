# 🚀 Deployment Steps - Railway Backend + Vercel Frontend

## ✅ Current Status

- **GitHub Repo**: ✅ https://github.com/jeanpaul09/rai-algo-trading-terminal
- **Vercel Frontend**: ✅ Deployed at https://web-qd6ycw6rq-jean-pauls-projects-7ca33fb2.vercel.app
- **Railway Backend**: ⏳ Ready to deploy

---

## 📋 Step-by-Step Deployment

### Part 1: Deploy Backend to Railway

#### Option A: Web Interface (Recommended)

1. **Go to Railway**
   - Visit https://railway.app
   - Click "Start a New Project"
   - Sign up/Login with GitHub

2. **Connect Repository**
   - Select "Deploy from GitHub repo"
   - Choose: `jeanpaul09/rai-algo-trading-terminal`
   - Railway will auto-detect Python

3. **Configure Service**
   - Railway should auto-detect settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python api_server.py`
   - If not, manually set:
     - Root Directory: `/` (leave empty)
     - Environment: `Python 3`

4. **Add Environment Variables**
   - Go to service → "Variables" tab
   - Add:
     ```
     PORT=8000
     ```
   - (Optional) Add secrets for live trading:
     ```
     HYPERLIQUID_PRIVATE_KEY=your_key
     HYPERLIQUID_ADDRESS=your_address
     CLAUDE_API_KEY=your_key
     ```

5. **Generate Domain**
   - Go to service → "Settings" → "Generate Domain"
   - Copy your Railway URL (e.g., `https://your-app.up.railway.app`)
   - **IMPORTANT**: Save this URL for Vercel configuration!

6. **Deploy**
   - Railway automatically deploys on push to GitHub
   - Watch logs for deployment status
   - Should complete in 2-5 minutes

7. **Verify Deployment**
   ```bash
   curl https://your-railway-url.up.railway.app/api/overview
   ```
   - Should return JSON response

---

### Part 2: Update Vercel Frontend

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Select your project: `web`

2. **Add Environment Variable**
   - Go to "Settings" → "Environment Variables"
   - Click "Add New"
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-railway-url.up.railway.app`
   - Select all environments (Production, Preview, Development)
   - Click "Save"

3. **Redeploy**
   - Go to "Deployments" tab
   - Click "..." on latest deployment
   - Click "Redeploy"
   - Or push a new commit (auto-redeploys)

4. **Verify Connection**
   - Visit: https://your-vercel-url.vercel.app/terminal
   - Open browser console (F12)
   - Should see API connection logs
   - Terminal should load with data

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] Railway service is running (green status)
- [ ] Railway API responds: `curl https://your-railway-url/api/overview`
- [ ] Vercel has `NEXT_PUBLIC_API_URL` environment variable set
- [ ] Vercel redeployed after adding env var
- [ ] Terminal page loads: `/terminal`
- [ ] Browser console shows API connection (no CORS errors)
- [ ] Chart displays (with mock data initially)
- [ ] Brain feed updates

---

## 🐛 Troubleshooting

### Railway Issues

**Build Fails:**
- Check Railway logs for error messages
- Verify `requirements.txt` includes all dependencies
- Check Python version (3.11 recommended)

**Service Won't Start:**
- Check logs: Railway dashboard → Service → Logs
- Verify `PORT` environment variable is set
- Check start command: `python api_server.py`

**API Not Responding:**
- Verify service is running (green status)
- Check Railway logs for errors
- Test with: `curl https://your-url/health` or `/api/overview`

### Vercel Issues

**Terminal Shows Error:**
- Check browser console (F12) for errors
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check Vercel deployment logs

**CORS Errors:**
- Verify Railway CORS settings in `api_server.py`
- Check Railway URL is correct in Vercel env vars
- Clear browser cache

**WebSocket Not Connecting:**
- Check WebSocket URL in browser console
- Verify Railway supports WebSocket (it does on all plans)
- Check Railway logs for WebSocket errors

---

## 📝 Quick Commands

### Test Railway API
```bash
# Health check
curl https://your-railway-url.up.railway.app/

# API overview
curl https://your-railway-url.up.railway.app/api/overview

# Test WebSocket (if implemented)
# Use browser DevTools → Network → WS tab
```

### Update Vercel Environment
```bash
cd ui/web
npx vercel env add NEXT_PUBLIC_API_URL
# Enter: https://your-railway-url.up.railway.app
```

### Redeploy Vercel
```bash
cd ui/web
npx vercel --prod
```

---

## 🎯 Next Steps After Deployment

1. **Test Full Stack**
   - Visit terminal: `/terminal`
   - Test agent interaction
   - Verify chart displays
   - Check brain feed

2. **Monitor Resources**
   - Railway dashboard: Check CPU/RAM usage
   - Vercel dashboard: Check deployment status
   - Both: Monitor logs for errors

3. **Add WebSocket Support** (if needed)
   - Railway supports WebSocket automatically
   - Update `api_server.py` to add WebSocket endpoint
   - Frontend already configured in `useWebSocket` hook

4. **Optimize**
   - Set up Railway auto-deploy from GitHub
   - Configure Vercel preview deployments
   - Add monitoring/alerting

---

## 📚 Documentation

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Full Guide: `DEPLOYMENT_RAILWAY.md`
- Specs Assessment: `RAILWAY_SPECS_ASSESSMENT.md`

