# Environment Variables Guide

## Current Status

✅ **Railway (Backend)**: I've only added `PORT=8000` (auto-detected)  
❌ **Vercel (Frontend)**: `NEXT_PUBLIC_API_URL` still needs to be added

---

## Required Environment Variables

### 🔴 Critical (Must Have)

#### Vercel Frontend
```bash
NEXT_PUBLIC_API_URL=https://web-production-e9cd4.up.railway.app
```
**Status**: ❌ **YOU NEED TO ADD THIS**
- Go to Vercel Dashboard → Settings → Environment Variables
- Add the variable above
- Redeploy

#### Railway Backend
```bash
PORT=8000
```
**Status**: ✅ Already set (Railway auto-detects)

---

## Optional Environment Variables (For Live Trading)

### 🟡 Hyperliquid Trading (Optional - Only for LIVE trading)

These are **ONLY needed if you want to execute live trades**:

```bash
HYPERLIQUID_PRIVATE_KEY=your_wallet_private_key_here
HYPERLIQUID_ADDRESS=your_wallet_address_here
HYPERLIQUID_TESTNET=true  # Set to "true" for testnet, "false" for mainnet
```

**Status**: ❌ Not added yet (not required for demo/backtesting)

**Where to add**: Railway Dashboard → Variables Tab

**Security**: These are **SENSITIVE** - use Railway's encrypted secrets, never commit to Git!

---

## Optional: LLM/Agent API Keys (For AI Agent Features)

If you want to use the AI agent features in the terminal, add one of these:

### Claude (Anthropic)
```bash
ANTHROPIC_API_KEY=sk-ant-...
```
**Where**: Railway Dashboard → Variables Tab

### OpenAI
```bash
OPENAI_API_KEY=sk-...
```
**Where**: Railway Dashboard → Variables Tab

**Status**: ❌ Not added yet (not required for basic terminal)

---

## Summary: What You Need To Do

### ✅ Already Done (by me):
- Railway `PORT` variable (auto-detected)

### ❌ You Need To Add:

1. **Vercel** (Required for frontend to connect to backend):
   - `NEXT_PUBLIC_API_URL` = `https://web-production-e9cd4.up.railway.app`

2. **Railway** (Optional - only if you want live trading):
   - `HYPERLIQUID_PRIVATE_KEY` (if you want to trade)
   - `HYPERLIQUID_ADDRESS` (if you want to trade)
   - `HYPERLIQUID_TESTNET=true` (for testnet trading)

3. **Railway** (Optional - only if you want AI agent features):
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

---

## Quick Setup Instructions

### 1. Connect Frontend to Backend (REQUIRED)

**Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings → Environment Variables
4. Add:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://web-production-e9cd4.up.railway.app`
5. Save → Redeploy

### 2. Enable Live Trading (OPTIONAL)

**Railway Dashboard:**
1. Go to https://railway.app
2. Select your project
3. Variables Tab
4. Add these (if you want live trading):
   - `HYPERLIQUID_PRIVATE_KEY` = (your key)
   - `HYPERLIQUID_ADDRESS` = (your address)
   - `HYPERLIQUID_TESTNET` = `true` (for testing)
5. Redeploy

⚠️ **Warning**: Only add trading keys if you want to execute real trades!

### 3. Enable AI Agent (OPTIONAL)

**Railway Dashboard:**
1. Variables Tab
2. Add:
   - `ANTHROPIC_API_KEY` = (your Claude API key) **OR**
   - `OPENAI_API_KEY` = (your OpenAI API key)
3. Redeploy

---

## Current State

✅ **Backend API**: Working (uses public APIs, no keys needed)  
✅ **Market Data**: Working (Hyperliquid/Binance public APIs)  
✅ **Terminal UI**: Working (with mock data)  
❌ **Frontend-Backend Connection**: Need to add `NEXT_PUBLIC_API_URL`  
❌ **Live Trading**: Disabled (no keys added - safe for now!)  
❌ **AI Agent**: Disabled (no LLM keys added)

---

**For now, the terminal works with demo/mock data. Add `NEXT_PUBLIC_API_URL` to Vercel to see real data!**

