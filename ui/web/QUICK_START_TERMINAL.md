# 🚀 Quick Start - Trading Terminal

## See the Terminal Locally (Right Now!)

### Option 1: Terminal Only (Mock Data) - 30 seconds

```bash
cd ui/web
npm install
npm run dev
```

Then open: **http://localhost:3001/terminal**

The terminal works immediately with mock data - you'll see:
- ✅ Global control bar with agent status
- ✅ Annotated trading chart
- ✅ Brain feed with simulated agent reasoning
- ✅ Strategy control panel
- ✅ Agent interaction panel
- ✅ Performance comparison

### Option 2: Full Stack (Terminal + Backend API)

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

Then open: **http://localhost:3001/terminal**

### Option 3: One-Click Launch

```bash
./launch_dashboard.sh
```

Then open: **http://localhost:3001/terminal**

---

## What You'll See

The terminal has:
1. **Top Bar**: Agent controls, wallet info, emergency stop
2. **Left Panel**: Strategy management (turn strategies ON/OFF, switch modes)
3. **Center**: 
   - Annotated price chart (BTC/USD) with entry/exit markers
   - Brain feed showing agent reasoning
4. **Right Panel**:
   - Agent chat interface
   - Performance comparison (BACKTEST vs DEMO vs LIVE)

---

## Deployment Options

### For Full Functionality Testing

Yes, deployment can help with full functionality testing, especially for:
- WebSocket connections (real-time updates)
- Testing on different devices/networks
- Sharing with team members
- Production-like environment testing

### Deployment Setup

#### Frontend (Vercel) - Next.js Dashboard
- ✅ **Free tier available**
- ✅ Automatic deployments from GitHub
- ✅ Environment variables for API URL
- ✅ Fast global CDN

#### Backend (Render) - Python API + WebSocket
- ✅ **Free tier available** (with limitations)
- ✅ Easy deployment from GitHub
- ✅ Environment variables for secrets
- ✅ WebSocket support

#### Yes, You Need GitHub

Both Vercel and Render deploy from GitHub repositories:

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Trading terminal"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy to Vercel**:
   - Go to https://vercel.com
   - Import your GitHub repo
   - Set root directory to `ui/web`
   - Add environment variable: `NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com`
   - Deploy!

3. **Deploy to Render**:
   - Go to https://render.com
   - Create new Web Service
   - Connect GitHub repo
   - Build command: `pip install -r requirements.txt && python api_server.py`
   - Add environment variables (secrets):
     - `HYPERLIQUID_PRIVATE_KEY`
     - `HYPERLIQUID_ADDRESS`
     - `CLAUDE_API_KEY`
   - Deploy!

---

## Local Development vs Deployment

### Local Development (Recommended First)
✅ **Pros:**
- Instant feedback
- No deployment delays
- Easy debugging
- Works offline
- Free

❌ **Cons:**
- WebSocket only works on localhost
- Can't share easily
- Need to keep your computer running

### Deployment (For Testing/Production)
✅ **Pros:**
- Accessible from anywhere
- Real WebSocket connections
- Team collaboration
- Production-like environment
- Can use real API keys (securely)

❌ **Cons:**
- Need GitHub repo
- Deployment setup time
- Environment variable configuration
- Free tiers have limitations

---

## Quick Test Locally First

Before deploying, let's make sure everything works locally:

```bash
# 1. Install dependencies (if not already done)
cd ui/web
npm install

# 2. Start the dev server
npm run dev

# 3. Open browser
# Go to: http://localhost:3001/terminal
```

You should see the full terminal with all components working!

---

## Next Steps

1. ✅ **Test Locally**: Run it now at http://localhost:3001/terminal
2. 🔄 **Connect Backend**: Start Python API server for real data
3. 🚀 **Deploy When Ready**: Push to GitHub and deploy to Vercel + Render
4. 🔐 **Add Secrets**: Configure environment variables for live trading

---

## Troubleshooting

**Port 3001 already in use?**
```bash
# Use a different port
PORT=3002 npm run dev
```

**Terminal page not found?**
- Make sure you're going to `/terminal` not just `/`
- Check the sidebar has "Terminal" link

**WebSocket not connecting?**
- This is normal on localhost without backend
- Mock data will still work
- For real WebSocket, deploy backend to Render

**Need help?**
- Check `TERMINAL_GUIDE.md` for detailed documentation
- All components are in `components/terminal/`

