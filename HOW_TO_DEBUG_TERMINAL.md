# How to Debug Terminal Page Error

## Step 1: Open Browser Console

**Chrome/Edge:**
1. Press `F12` OR
2. Right-click page → "Inspect" → Click "Console" tab OR  
3. Press `Ctrl+Shift+J` (Windows/Linux) or `Cmd+Option+J` (Mac)

**Firefox:**
1. Press `F12` OR
2. Right-click → "Inspect Element" → "Console" tab OR
3. Press `Ctrl+Shift+K` (Windows/Linux) or `Cmd+Option+K` (Mac)

**Safari:**
1. Enable Developer menu: Preferences → Advanced → Check "Show Develop menu"
2. Press `Cmd+Option+C`

## Step 2: Check Console Errors

Look for:
- **Red error messages** - These show what broke
- **Stack traces** - Shows which file/line caused the error
- **Failed network requests** - Check if API calls are failing

## Step 3: Common Issues

### Issue: "Cannot find module" or "Import error"
**Solution:** Missing dependency - Check if package.json has all required packages

### Issue: "window is not defined" or "document is not defined"
**Solution:** Server-side rendering issue - Component needs "use client" directive

### Issue: "TypeError: Cannot read property X of undefined"
**Solution:** Null/undefined check missing - Data not loaded yet

### Issue: Network errors (CORS, 404, 500)
**Solution:** Backend not running or wrong API URL

## Step 4: Share the Error

Copy the **entire error message** from the console and share it. Include:
- The error message
- The file name and line number
- Any stack trace

## Quick Test

Try this minimal version first - replace `page.tsx` temporarily with `page-simple.tsx` to see if basic rendering works.

