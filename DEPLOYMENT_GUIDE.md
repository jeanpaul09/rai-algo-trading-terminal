# Deployment Guide - Trading Terminal

## Quick Setup Steps

### 1. GitHub Repository

Create and push to GitHub:
```bash
gh repo create rai-algo-trading-terminal --public --source=. --remote=origin --push
```

Or if you prefer a different name:
```bash
gh repo create YOUR_REPO_NAME --public --source=. --remote=origin --push
```

### 2. Vercel Deployment (Frontend)

**Option A: Using Vercel CLI**
```bash
npm install -g vercel
cd ui/web
vercel login
vercel --prod
```

**Option B: Using Vercel Dashboard**
1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `ui/web`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
5. Environment Variables:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com` (after Render deploy)
6. Click "Deploy"

### 3. Render Deployment (Backend)

**Using Render Dashboard:**
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `rai-algo-api` (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`
   - **Instance Type**: Free (or paid for better performance)
5. Environment Variables (Add as Secrets):
   ```
   HYPERLIQUID_PRIVATE_KEY=your_private_key_here
   HYPERLIQUID_ADDRESS=your_address_here
   CLAUDE_API_KEY=your_claude_api_key_here
   ```
6. Click "Create Web Service"

**Important**: After Render deploys, update Vercel's `NEXT_PUBLIC_API_URL` to point to your Render URL.

### 4. Environment Variables Summary

#### Vercel (Frontend)
- `NEXT_PUBLIC_API_URL` = `https://your-app.onrender.com`

#### Render (Backend)
- `HYPERLIQUID_PRIVATE_KEY` = (your key)
- `HYPERLIQUID_ADDRESS` = (your address)
- `CLAUDE_API_KEY` = (your key)

## Post-Deployment Checklist

- [ ] GitHub repo created and pushed
- [ ] Vercel frontend deployed
- [ ] Render backend deployed
- [ ] Environment variables set in both platforms
- [ ] Test terminal at Vercel URL: `https://your-app.vercel.app/terminal`
- [ ] Verify WebSocket connection works
- [ ] Test API endpoints work

## Troubleshooting

**Vercel build fails?**
- Check that root directory is set to `ui/web`
- Verify all dependencies are in `package.json`

**Render deploy fails?**
- Check that `requirements.txt` exists and has all dependencies
- Verify start command is correct

**WebSocket not connecting?**
- Ensure Render backend URL is set in Vercel's `NEXT_PUBLIC_API_URL`
- Check that Render service is running
- Verify WebSocket endpoint is accessible

## Quick Commands

```bash
# GitHub
gh repo create rai-algo-trading-terminal --public --source=. --remote=origin --push

# Vercel (after installing CLI)
cd ui/web && vercel --prod

# Check deployments
vercel ls  # Frontend
gh repo view --web  # GitHub repo
```

