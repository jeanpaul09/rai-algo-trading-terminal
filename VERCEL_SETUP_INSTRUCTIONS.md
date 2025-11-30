# Vercel Setup Instructions

## ✅ Fix Applied
Removed `rootDirectory` from `vercel.json` (not allowed in schema). This must be set in Vercel dashboard instead.

## 🔧 Required Vercel Configuration

### Step 1: Set Root Directory in Vercel Dashboard
1. Go to your Vercel project: https://vercel.com/dashboard
2. Click on your project → **Settings**
3. Go to **General** → **Root Directory**
4. Set root directory to: `ui/web`
5. Click **Save**

### Step 2: Set Environment Variable
1. In Vercel project → **Settings** → **Environment Variables**
2. Add new variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://web-production-e9cd4.up.railway.app`
   - **Environment**: Production, Preview, Development (select all)
3. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click **Redeploy** on the latest deployment
3. OR push a new commit to trigger auto-deploy

## 📝 What This Does

- **Root Directory (`ui/web`)**: Tells Vercel where your Next.js app lives
- **Environment Variable**: Makes backend URL available to frontend
- **Build Commands**: Now simplified (no need for `cd` since root directory is set)

## ✅ After Configuration

Once you set the root directory in Vercel dashboard:
- Build will find `package.json` in `ui/web`
- Environment variable will be available at build time
- Terminal page will connect to Railway backend
- Real data will display (no mocks)

---

**Important**: The root directory MUST be set in Vercel dashboard, NOT in `vercel.json`!

