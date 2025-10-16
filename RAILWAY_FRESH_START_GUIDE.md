# Railway Fresh Database Setup Guide

**Date**: October 15, 2025  
**Issue**: Old database ran out of disk space (1GB limit)  
**Solution**: Create fresh PostgreSQL database on Railway free tier  

---

## Step-by-Step Instructions

### Step 1: Create New Railway PostgreSQL Database

1. **Go to Railway Dashboard**: https://railway.app/dashboard

2. **Click on your project** (or create new one if needed)

3. **Add New Service**:
   - Click **"+ New"** button
   - Select **"Database"**
   - Choose **"PostgreSQL"**
   - Wait 2-3 minutes for provisioning

4. **Get Connection String**:
   - Click on the new PostgreSQL service
   - Go to **"Connect"** tab
   - Copy the **"DATABASE_URL"** or **"Postgres Connection URL"**
   - Should look like: `postgresql://postgres:PASSWORD@HOST:PORT/railway`

5. **Save it here for the next steps** (we'll use it below)

---

### Step 2: Update Vercel Environment Variable

Now we need to update your Vercel deployment with the new database URL.

**Option A: Using Vercel Dashboard (Easiest)**

1. Go to: https://vercel.com/jp3ttys-projects/engineering_log_intelligence/settings/environment-variables
2. Find **DATABASE_URL**
3. Click **"Edit"**
4. Paste your new Railway DATABASE_URL
5. Make sure it's set for **"Production"** environment
6. Click **"Save"**

**Option B: Using Vercel CLI**

```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Add new DATABASE_URL (will prompt for value)
vercel env rm DATABASE_URL production
vercel env add DATABASE_URL production

# Paste your new Railway DATABASE_URL when prompted
```

---

### Step 3: Update Local Environment Files

Update your local `.env` files with the new database URL:

```bash
# Update .env.local
echo "DATABASE_URL=YOUR_NEW_RAILWAY_URL_HERE" > .env.local

# Or edit manually
nano .env.local
```

---

### Step 4: Setup Database Schema

Run the schema setup script to create all tables:

```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Set the new DATABASE_URL for this session
export DATABASE_URL="YOUR_NEW_RAILWAY_URL_HERE"

# Run schema setup
python3 setup_schema_fixed.py
```

Expected output:
```
✅ Connected to database successfully
✅ Schema setup complete
✅ All tables created
```

---

### Step 5: Populate with Sample Data

Generate realistic sample data (10,000 log entries):

```bash
# Generate 10,000 logs
python3 populate_database.py 10000
```

Expected output:
```
✅ Generated 10,000 log entries
✅ Connected successfully
✅ All logs inserted successfully
Total logs in database: 10,000
```

**Adjust data volume** if needed:
- **Smaller dataset** (stays well under 1GB): `python3 populate_database.py 5000`
- **Larger dataset** (for demo purposes): `python3 populate_database.py 20000`

---

### Step 6: Redeploy to Vercel

Force a new deployment to pick up the new DATABASE_URL:

```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Force redeploy to production
vercel --prod --force
```

---

### Step 7: Verify Everything Works

After deployment completes (2-3 minutes), test the endpoints:

```bash
# Test health endpoint
curl -s "https://engineeringlogintelligence.vercel.app/api/health"

# Test metrics (should show real data)
curl -s "https://engineeringlogintelligence.vercel.app/api/metrics" | python3 -m json.tool

# Test dashboard (should show 10,000 logs)
curl -s "https://engineeringlogintelligence.vercel.app/api/dashboard_analytics" | grep -E "(logsProcessed|dataSource)"
```

Expected output:
```json
{
  "logsProcessed": 10000,
  "dataSource": "database"
}
```

---

### Step 8: Test in Browser

1. Open: https://engineeringlogintelligence.vercel.app
2. Check **System Health** = "Healthy" ✅
3. Verify **log counts** show ~10,000 logs
4. Check all charts display real data

---

## Quick Reference Commands

Once you have your new DATABASE_URL, run these commands in order:

```bash
# Navigate to project
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Set DATABASE_URL (replace with your new URL)
export DATABASE_URL="postgresql://postgres:PASSWORD@HOST:PORT/railway"

# Setup schema
python3 setup_schema_fixed.py

# Populate data
python3 populate_database.py 10000

# Update Vercel and redeploy
vercel env rm DATABASE_URL production
vercel env add DATABASE_URL production
# (paste DATABASE_URL when prompted)

vercel --prod --force
```

---

## Monitoring Disk Usage

To avoid this issue in the future:

### Check Current Usage
```bash
# Connect to Railway database
export DATABASE_URL="your_new_railway_url"

python3 -c "
import psycopg2
import os

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

# Get database size
cursor.execute(\"\"\"
    SELECT pg_size_pretty(pg_database_size('railway')) as db_size
\"\"\")
print(f'Database size: {cursor.fetchone()[0]}')

# Get table sizes
cursor.execute(\"\"\"
    SELECT 
        relname as table,
        pg_size_pretty(pg_total_relation_size(relid)) as size
    FROM pg_catalog.pg_statio_user_tables
    ORDER BY pg_total_relation_size(relid) DESC
    LIMIT 10;
\"\"\")
print('\\nTop 10 tables by size:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

cursor.close()
conn.close()
"
```

### Set Up Monitoring
Railway free tier = **1GB storage limit**

Keep your database under **800MB** to have headroom:
- **10,000 logs**: ~50-100MB ✅ Safe
- **50,000 logs**: ~250-500MB ✅ Safe
- **100,000 logs**: ~500-800MB ⚠️ Monitor closely
- **200,000+ logs**: Risk of hitting 1GB limit

### Auto-cleanup Script (Optional)
Create a cleanup script to run periodically:

```python
# cleanup_old_logs.py
import psycopg2
import os

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

# Delete logs older than 30 days
cursor.execute("""
    DELETE FROM log_entries 
    WHERE timestamp < NOW() - INTERVAL '30 days'
""")
deleted = cursor.rowcount

# Reclaim space
cursor.execute("VACUUM FULL log_entries")

conn.commit()
print(f"Deleted {deleted} old logs")
cursor.close()
conn.close()
```

---

## Troubleshooting

### Issue: Schema setup fails
**Error**: "relation already exists"
**Solution**: Schema already created, skip to Step 5 (populate data)

### Issue: "too many connections" error
**Solution**: This should be fixed with your new connection pool! But if it happens:
- Check connection count in Railway dashboard
- Verify all API files use `api._db_pool.py`
- Reduce `maxconn` in `_db_pool.py` from 2 to 1

### Issue: Vercel still shows old data or errors
**Solution**: 
```bash
# Clear Vercel cache and force redeploy
vercel --prod --force
```

### Issue: Can't connect to new database
**Solution**:
- Check DATABASE_URL is correct (no extra spaces/newlines)
- Verify database is running in Railway dashboard
- Check Railway service status

---

## What Changed vs Old Database

| Aspect | Old Database | New Database |
|--------|--------------|--------------|
| Disk Space Used | 1GB+ (full) | ~50-100MB |
| Connection Pool | Implemented ✅ | Same (2 connections) |
| Data | 10,000+ logs (old) | 10,000 logs (fresh) |
| Status | Crashed | Running ✅ |
| Performance | Degraded | Optimal |

---

## Success Checklist

- [ ] Created new Railway PostgreSQL database
- [ ] Copied new DATABASE_URL
- [ ] Updated Vercel environment variable
- [ ] Updated local .env.local file
- [ ] Ran schema setup script successfully
- [ ] Populated database with 10,000 logs
- [ ] Redeployed to Vercel
- [ ] Verified API endpoints return real data
- [ ] Checked frontend shows "Healthy" status
- [ ] Confirmed log counts show ~10,000

---

## Next Steps After Setup

1. **Delete old Railway database** to free up resources:
   - Go to Railway dashboard
   - Select old PostgreSQL service
   - Settings → Delete Service

2. **Update documentation** with new DATABASE_URL location

3. **Monitor disk usage** weekly to avoid future issues

4. **Consider upgrading** if you need more than 1GB storage

---

**Created**: October 15, 2025  
**Status**: Ready to execute  
**Estimated Time**: 15-20 minutes  

