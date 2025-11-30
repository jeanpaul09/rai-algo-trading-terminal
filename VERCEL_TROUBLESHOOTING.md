# Vercel Troubleshooting Guide

## Issue: package.json not found

### Root Cause
Vercel is trying to run `npm install` from the repository root (`/vercel/path0/`) instead of from `ui/web` where the Next.js app actually lives.

### Solutions

#### Solution 1: Ensure Root Directory Setting (Recommended)
1. Go to Vercel Dashboard → Your Project → Settings
2. Go to **General** → **Root Directory**
3. Make sure it's set to: `ui/web`
4. Click **Save**
5. **IMPORTANT**: Remove the root directory setting completely, then add it back again
6. Redeploy

#### Solution 2: Verify vercel.json
The `vercel.json` should have:
```json
{
  "buildCommand": "cd ui/web && npm install && npm run build",
  "outputDirectory": "ui/web/.next",
  "installCommand": "cd ui/web && npm install",
  "framework": null
}
```

Setting `framework: null` forces Vercel to use our custom commands instead of auto-detecting.

#### Solution 3: Check Vercel Logs
In Vercel deployment logs, check:
- What directory is being used as root
- Whether custom commands are being executed
- Any warnings about root directory

#### Solution 4: Alternative - Move vercel.json
Try moving `vercel.json` to `ui/web/vercel.json` and set root directory in dashboard to `ui/web`.

---

## Current Configuration

**Root Directory in Dashboard**: Should be `ui/web` (or empty)
**vercel.json Location**: Root of repository
**vercel.json Commands**: Explicitly `cd ui/web` before running npm commands

---

## If Still Not Working

1. **Remove root directory setting** from Vercel dashboard completely
2. Keep `vercel.json` with `cd ui/web` commands
3. Redeploy

OR

1. **Set root directory** to `ui/web` in dashboard
2. Change `vercel.json` to remove `cd ui/web` (since we're already in that directory):
   ```json
   {
     "buildCommand": "npm install && npm run build",
     "outputDirectory": ".next",
     "installCommand": "npm install",
     "framework": "nextjs"
   }
   ```
3. Redeploy

