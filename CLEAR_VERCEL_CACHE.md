# How to Clear Vercel Cache

## Method 1: Automatic (Recommended)
The `next.config.ts` file has been updated with a timestamped build version that forces Vercel to rebuild with a fresh cache.

**Just push the code - Vercel will automatically rebuild with the new version.**

## Method 2: Manual Vercel Dashboard
1. Go to your Vercel project dashboard
2. Click on the "Deployments" tab
3. Find your latest deployment
4. Click the "..." menu (three dots)
5. Select "Redeploy"
6. **IMPORTANT**: Check "Use existing Build Cache" to **UNCHECK** it (disable cache)
7. Click "Redeploy"

## Method 3: Force Rebuild via API
```bash
# This requires Vercel CLI
vercel --force
```

## Method 4: Browser Cache (User Side)
Tell users to:
1. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
2. Or clear browser cache in dev tools
3. Or use incognito/private browsing mode

## Method 5: Update Environment Variable
We can also force a rebuild by updating an environment variable in Vercel dashboard, which triggers a new build.

---

**Current Build Version:** Check `next.config.ts` - it should have a timestamp that changes on each commit.

