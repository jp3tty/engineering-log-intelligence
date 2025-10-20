# Railway Database URL Update Instructions

**Date**: October 20, 2025  
**Reason**: Upgraded to Railway Hobby Plan

## ✅ Completed

- [x] Updated local `.env.local` file
- [x] Updated `railway_aws_confluent.txt` documentation
- [x] Verified database connection working

## 🔄 Still Need to Update

### 1. GitHub Secrets (For Automated Workflows)

Your three GitHub Actions workflows need the new DATABASE_URL:
- `daily-log-generation.yml` - Generates logs daily
- `ml_analysis.yml` - Runs ML analysis every 6 hours
- `daily_cleanup.yml` - Cleans up old logs daily

**Steps to Update:**

1. Go to: https://github.com/jp3tty/engineering_log_intelligence/settings/secrets/actions
   (Or navigate: Your Repo → Settings → Secrets and variables → Actions)

2. Find the secret named `DATABASE_URL`

3. Click **"Update"** or **"Edit"**

4. Replace with the new value:
   ```
   postgresql://postgres:aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq@switchyard.proxy.rlwy.net:51941/railway
   ```

5. Click **"Update secret"**

6. ✅ All workflows will now use the new connection!

---

### 2. Vercel Environment Variables (For API Endpoints)

Your API endpoints (`/api/logs`, `/api/metrics`, `/api/dashboard_analytics`, etc.) need the new DATABASE_URL.

**Option A: Using Vercel Dashboard (Recommended)**

1. Go to: https://vercel.com/jp3ttys-projects/engineering_log_intelligence/settings/environment-variables

2. Find `DATABASE_URL` in the list

3. Click **"Edit"** (pencil icon)

4. Replace with the new value:
   ```
   postgresql://postgres:aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq@switchyard.proxy.rlwy.net:51941/railway
   ```

5. Make sure it's set for **"Production"**, **"Preview"**, and **"Development"** environments

6. Click **"Save"**

7. **Redeploy** to apply changes:
   - Go to Deployments tab
   - Click on latest deployment
   - Click "Redeploy" button
   - OR run: `vercel --prod --force` from terminal

**Option B: Using Vercel CLI**

```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Remove old DATABASE_URL
vercel env rm DATABASE_URL production
vercel env rm DATABASE_URL preview
vercel env rm DATABASE_URL development

# Add new DATABASE_URL (will prompt for value)
vercel env add DATABASE_URL production
# Paste: postgresql://postgres:aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq@switchyard.proxy.rlwy.net:51941/railway

vercel env add DATABASE_URL preview
# Paste same value

vercel env add DATABASE_URL development
# Paste same value

# Force redeploy to production
vercel --prod --force
```

---

## 🧪 Verification Steps

After updating both GitHub Secrets and Vercel:

### Test GitHub Actions Workflows

1. Go to: https://github.com/jp3tty/engineering_log_intelligence/actions

2. **Test Log Generation:**
   - Click "Daily Log Generation"
   - Click "Run workflow"
   - Set log count to `100` (small test)
   - Click "Run workflow"
   - Wait 1-2 minutes
   - Should show ✅ Success

3. **Test ML Analysis:**
   - Click "ML Batch Analysis"
   - Click "Run workflow"
   - Should complete successfully

### Test Vercel API

After redeploying:

```bash
# Test metrics endpoint
curl -s "https://engineeringlogintelligence.vercel.app/api/metrics" | python3 -m json.tool

# Test dashboard analytics
curl -s "https://engineeringlogintelligence.vercel.app/api/dashboard_analytics" | python3 -m json.tool

# Should see real data, not simulated data
# Look for: "dataSource": "database"
```

---

## 📊 New Database Details

**Host**: `switchyard.proxy.rlwy.net`  
**Port**: `51941`  
**Database**: `railway`  
**User**: `postgres`  
**Password**: `aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq`

**Current Stats:**
- Total logs: 157,377
- Database size: 101 MB / 8 GB (1.2% used)
- Date range: Oct 15 - Oct 20, 2025

**Plan**: Railway Hobby Plan ($5/month)
- Storage: 8 GB
- Plenty of headroom for growth!

---

## 🎯 Summary

### What's Updated:
✅ Local `.env.local` (tested and working)  
✅ `railway_aws_confluent.txt` (documentation)

### What You Need to Update:
⏳ GitHub Secrets (for workflows)  
⏳ Vercel Environment Variables (for API)

### Expected Time:
- GitHub Secrets: 2 minutes
- Vercel Environment: 5 minutes (including redeploy)
- Total: ~7 minutes

Once both are updated, your entire data pipeline will be fully operational! 🎉

