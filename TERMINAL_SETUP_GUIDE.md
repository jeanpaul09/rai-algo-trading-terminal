# 🔧 Terminal Setup Guide - Make It Work!

## Current Issue
Terminal shows mock data and has no functionality because:
1. ❌ `NEXT_PUBLIC_API_URL` not set in Vercel
2. ❌ Backend not connected
3. ⚠️  All API calls falling back to mock data

## ✅ Solution

### Step 1: Add Backend URL to Vercel (CRITICAL)

1. **Go to Vercel Dashboard**
   - https://vercel.com/dashboard
   - Select your project

2. **Add Environment Variable**
   - Go to: **Settings** → **Environment Variables**
   - Click **Add New**
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://web-production-e9cd4.up.railway.app`
   - Environment: **Production** (and Preview if you want)
   - Click **Save**

3. **Redeploy**
   - Go to **Deployments** tab
   - Click **⋯** on latest deployment → **Redeploy**
   - Or it will auto-redeploy on next push

### Step 2: Verify Backend is Running

**Check Railway:**
1. Go to https://railway.app
2. Select your project
3. Check **Logs** - should show:
   - ✅ "Anthropic client initialized"
   - ✅ "Starting RAI-ALGO API Server"
   - ✅ No errors

**Test API directly:**
```bash
curl https://web-production-e9cd4.up.railway.app/api/overview
```

Should return JSON, not an error.

### Step 3: Access Terminal

1. **Open your Vercel app**
   - https://web-4dyyrxpwv-jean-pauls-projects-7ca33fb2.vercel.app

2. **Click "Terminal" in sidebar** (left side)
   - Or go directly to: `/terminal`

3. **What you should see:**
   - ✅ Terminal UI loads
   - ✅ Status shows connection status
   - ✅ Real data from Railway backend (after env var is set)
   - ✅ AI agent responds to commands
   - ✅ Wallet info loads from Hyperliquid

## 🎯 What Works After Setup

### ✅ Real Data
- Wallet balance from Hyperliquid
- Agent status from backend
- Real-time WebSocket updates

### ✅ AI Agent
- Type commands in "Agent Chat" panel
- Claude responds intelligently
- Commands processed on backend

### ✅ Live Trading
- Toggle agent to DEMO mode
- Start strategies
- Execute paper trades on Hyperliquid

### ✅ Controls
- Mode switching (OFF/DEMO/LIVE)
- Strategy management
- Emergency stop

## 🐛 Troubleshooting

### Still seeing "Backend URL Not Set"?
- ✅ Check Vercel env var is set correctly
- ✅ Redeploy Vercel after adding env var
- ✅ Check browser console for errors

### WebSocket not connecting?
- ✅ Verify Railway URL is correct
- ✅ Check Railway logs for errors
- ✅ Try accessing Railway API directly in browser

### AI Agent not responding?
- ✅ Check Railway has `ANTHROPIC_API_KEY` set
- ✅ Check Railway logs for Anthropic errors
- ✅ Verify Claude API quota/limits

### Wallet info not loading?
- ✅ Check Railway has `HYPERLIQUID_PRIVATE_KEY` and `HYPERLIQUID_ADDRESS`
- ✅ Verify keys are correct format
- ✅ Check Railway logs for Hyperliquid errors

## 📝 Quick Checklist

- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] Vercel redeployed
- [ ] Railway backend running
- [ ] Terminal page accessible (click "Terminal" in sidebar)
- [ ] Status indicator shows connected (not "Backend URL Not Set")
- [ ] AI agent responds to commands
- [ ] Wallet info displays

## 🚀 After Setup

Your terminal will be **fully functional**:
- Real-time data from Railway
- AI agent with Claude
- Live trading on Hyperliquid
- Full strategy control

---

**The terminal IS working - you just need to connect it to the backend!** 🎯

