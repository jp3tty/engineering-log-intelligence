# 🚨 Railway Storage Emergency Guide

**Date**: October 18, 2025  
**Status**: **CRITICAL** - 80% storage capacity reached  
**Estimated Time to Full**: 1-2 days at current growth rate

---

## 📊 Current Situation

| Metric | Value |
|--------|-------|
| **Database Size** | 132.98 MB |
| **Storage Limit** | ~166 MB (Railway free tier) |
| **Current Usage** | 80% |
| **Remaining Space** | 33.24 MB |
| **Total Logs** | 190,000 logs |
| **Log Age** | All < 7 days old |
| **Growth Rate** | ~27,000 logs/day |

### Problem Analysis
- ⚠️ ALL 190k logs are fresh (< 7 days old)
- ⚠️ Indexes are 74 MB (larger than data at 48 MB!)
- ⚠️ At current rate: **FULL in 1-2 days**
- ⚠️ No cleanup policy currently in place

---

## 🆘 Immediate Solutions (Choose One)

### **Option 1: Reduce Log Retention to 7 Days** ⭐ RECOMMENDED

**What it does**: Keeps only the last 7 days of logs  
**Result**: Frees up significant space immediately  
**Risk**: Low - 7 days is standard for development environments

```bash
# 1. Preview what will be deleted (safe)
python3 cleanup_old_logs.py --days 7 --dry-run

# 2. Actually delete (requires confirmation)
python3 cleanup_old_logs.py --days 7
```

**Expected Savings**: Varies based on log age distribution

---

### **Option 2: Reduce to 3 Days (Aggressive)**

**What it does**: Keeps only the last 3 days  
**Result**: Maximum space savings  
**Risk**: Moderate - might delete logs you need

```bash
python3 cleanup_old_logs.py --days 3
```

---

### **Option 3: Upgrade Railway Plan**

**What it does**: Increases storage limit  
**Cost**: $5/month (Hobby plan) or $20/month (Pro)  
**Storage**: 8 GB (Hobby) or 32 GB (Pro)

**When to choose this**:
- Need to keep ALL historical logs
- Have budget for paid plan
- Want to avoid regular cleanup

[Upgrade on Railway →](https://railway.app/pricing)

---

## 🔄 Long-Term Solution: Automated Cleanup

### **Set Up Daily Automated Cleanup** ⭐ HIGHLY RECOMMENDED

This prevents the problem from happening again:

**1. GitHub Actions Workflow (Already Created)**
- File: `.github/workflows/daily_cleanup.yml`
- Runs: Daily at 2 AM UTC
- Retention: 7 days (configurable)

**2. Enable the Workflow**
```bash
# Commit and push to enable
git add .github/workflows/daily_cleanup.yml
git commit -m "Add daily log cleanup workflow"
git push
```

**3. Add DATABASE_URL Secret**
- Go to GitHub repository → Settings → Secrets
- Add secret: `DATABASE_URL` with your Railway connection string

**Result**: Logs older than 7 days are automatically deleted every night

---

## 📋 Step-by-Step: Emergency Cleanup NOW

### **Step 1: Preview the Cleanup**
```bash
cd engineering_log_intelligence
python3 cleanup_old_logs.py --days 7 --dry-run
```

This shows what will be deleted WITHOUT actually deleting anything.

### **Step 2: Run the Cleanup**
```bash
python3 cleanup_old_logs.py --days 7
# Type 'DELETE' when prompted
```

This will:
1. ✅ Delete logs older than 7 days
2. ✅ Delete orphaned ML predictions
3. ✅ Run VACUUM to reclaim disk space
4. ✅ Show before/after statistics

**Time**: 2-5 minutes depending on database size

### **Step 3: Verify Results**
```bash
python3 check_db_size.sh
```

You should see storage usage drop to ~50-60%

### **Step 4: Enable Automated Cleanup**
```bash
# Commit the new workflow
git add .github/workflows/daily_cleanup.yml
git add scripts/auto_cleanup_logs.py
git commit -m "Add automated log retention policy"
git push

# Add DATABASE_URL to GitHub Secrets
# (Go to GitHub repo → Settings → Secrets → Actions)
```

---

## 🔧 Advanced: Optimize Indexes

Your indexes (74 MB) are larger than your data (48 MB). This is unusual.

### **Rebuild Indexes to Reclaim Space**
```sql
-- Connect to Railway database
-- Run these commands:

REINDEX TABLE log_entries;
REINDEX TABLE ml_predictions;
VACUUM FULL log_entries;
VACUUM FULL ml_predictions;
```

**Expected Savings**: 20-40 MB

---

## 🎯 Recommended Action Plan

### **RIGHT NOW (Next 30 minutes)**
1. ✅ Run cleanup script: `python3 cleanup_old_logs.py --days 7`
2. ✅ Verify storage reduced to < 60%

### **TODAY**
1. ✅ Enable automated cleanup workflow
2. ✅ Add DATABASE_URL to GitHub Secrets
3. ✅ Test workflow: Go to Actions → Daily Log Cleanup → Run workflow

### **THIS WEEK**
1. ✅ Monitor storage daily
2. ✅ Adjust retention period if needed
3. ✅ Consider upgrading Railway plan if budget allows

---

## 📈 Storage Capacity Planning

### **Free Tier (166 MB)**
- **7-day retention**: ~130-140 MB (safe)
- **14-day retention**: Too large (exceeds limit)
- **30-day retention**: Not possible

### **Hobby Tier (8 GB)**
- **7-day retention**: ~140 MB (2% usage)
- **30-day retention**: ~600 MB (7% usage)
- **90-day retention**: ~1.8 GB (22% usage)

**Recommendation**: 
- If staying on free tier: **7 days maximum**
- If upgrading to Hobby: **30 days recommended**

---

## 🚨 Emergency Contact Info

### **If Database Fills Up Completely**

Railway will:
- ❌ Stop accepting new writes
- ❌ API endpoints will fail
- ✅ Read-only queries still work

**Recovery**:
```bash
# Emergency cleanup (keeps last 3 days only)
python3 cleanup_old_logs.py --days 3
```

---

## 📝 Monitoring Recommendations

### **Set Up Railway Alerts**
1. Go to Railway dashboard
2. Settings → Notifications
3. Enable "Volume Usage" alerts at 75%

### **Check Storage Weekly**
```bash
cd engineering_log_intelligence
python3 check_db_size.sh
```

---

## ✅ Success Criteria

After cleanup, you should see:
- ✅ Storage usage < 60%
- ✅ Remaining space > 60 MB
- ✅ Daily cleanup workflow enabled
- ✅ Estimated days until full: > 30 days

---

## 📞 Questions?

**Q: Will cleanup delete ML predictions?**  
A: Yes, but only predictions for deleted logs. Recent predictions are kept.

**Q: Can I recover deleted logs?**  
A: No. Deletion is permanent. Always run `--dry-run` first!

**Q: How often should cleanup run?**  
A: Daily is recommended. The workflow handles this automatically.

**Q: What if I need older logs?**  
A: Consider exporting to cloud storage (S3, Cloudflare R2) before deletion.

---

## 🎯 Next Steps

**Choose your path:**

**Path A: Quick Fix (Free Tier)**
1. Run cleanup script now
2. Enable daily automated cleanup
3. Monitor weekly

**Path B: Upgrade Plan (Recommended for Production)**
1. Upgrade to Railway Hobby ($5/month)
2. Increase retention to 30 days
3. Enable automated cleanup
4. Set up monitoring alerts

**Current Recommendation**: **Path A** for development, **Path B** for production use.

