# ML Feature Enablement Guide (Batch Processing Architecture)

**Date:** October 11, 2025  
**Version:** 2.0  
**Status:** Production-Ready with Vercel Hobby Tier Optimizations

---

## 🎯 What This Guide Covers

This guide will help you enable ML features using a **batch processing architecture** that:
- ✅ Works perfectly with Vercel Hobby tier limits
- ✅ Is 10x faster than serverless ML
- ✅ Scales to millions of logs
- ✅ Costs nothing (free GitHub Actions)

---

## 📋 Prerequisites

**Current Status (October 11, 2025):**
- ✅ Database: Connected with `log_entries` table
- ✅ Data: 12,010 logs available (exceeds minimum requirement)
- ✅ Schema: Includes all necessary fields for ML training
- ✅ Ready: All prerequisites met for ML enablement

**What You Need:**
1. Python 3.12+ installed locally
2. PostgreSQL database with log data (you have this!)
3. GitHub repository (for Actions)
4. Vercel account (for API deployment)

---

## 🏗️ Architecture Overview

### Traditional Approach (❌ Not Recommended for Hobby Tier)
```
User → Vercel Function → Load ML Libraries (55MB) → Predict → Return
        ↑
   Slow (3-5s), Large, Expensive
```

### **Batch Processing Approach (✅ Recommended)**
```
GitHub Actions (every 6 hours)
    ↓
Load ML Models → Analyze 1000s of logs → Store in PostgreSQL
                                              ↓
User → Vercel Function → Query Database (10ms) → Return
        ↑
   Fast, Tiny (5MB), Free
```

**See [`ML_ARCHITECTURE_DECISION.md`](ML_ARCHITECTURE_DECISION.md) for detailed comparison.**

---

## 🚀 Step-by-Step Implementation

### Step 1: Train ML Models Locally ✅ COMPLETED

You've already done this! You have:
- `models/log_classifier_simple.pkl` (100% accuracy)
- `models/anomaly_detector_simple.pkl` (90.2% accuracy)
- `models/vectorizer_simple.pkl`
- `models/metadata_simple.json`

These models were trained on 10,000 real logs and are ready to use.

---

### Step 2: Set Up GitHub Actions for Batch Processing

#### 2.1 Add Database Secret to GitHub

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add secret:
   - **Name:** `DATABASE_URL`
   - **Value:** Your PostgreSQL connection string (from `.env.local`)
   - Click **Add secret**

#### 2.2 Commit and Push ML Files

```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Add all ML files
git add models/
git add scripts/ml_batch_analysis.py
git add .github/workflows/ml_analysis.yml
git add api/ml_lightweight.py

git commit -m "Add batch ML processing system

- GitHub Actions workflow for automated analysis
- Batch analysis script (processes 1000s of logs)
- Lightweight API endpoint (no ML libraries)
- Database schema for ml_predictions table"

git push
```

#### 2.3 Run First Batch Analysis

**Option 1: Manual Trigger (Recommended for first run)**
1. Go to GitHub → Your Repository → **Actions** tab
2. Click **"ML Log Analysis"** workflow
3. Click **"Run workflow"** button
4. Select branch: `main`
5. Click **"Run workflow"**

**Option 2: Wait for Automatic Run**
- The workflow runs automatically every 6 hours

#### 2.4 Monitor the Run

1. Click on the running workflow
2. Click **"analyze_logs"** job
3. Watch the steps:
   ```
   ✅ Checkout code
   ✅ Set up Python
   ✅ Install dependencies (scikit-learn, numpy, psycopg2)
   ✅ Run ML analysis
      📂 Loading ML models...
      📊 Connecting to database...
      🗄️  Setting up ML predictions table...
      📋 Fetching logs that need analysis...
      🤖 Running ML analysis...
      💾 Storing predictions in database...
      📊 Generating summary statistics...
      📄 Saving results to file...
   ✅ Upload analysis results
   ```

**Expected Output:**
```
🎉 ML BATCH ANALYSIS COMPLETE!
======================================================================
✅ Analyzed: 1,000 logs
✅ Stored: 1,000 predictions
✅ Anomalies: 45

💡 Predictions are now in the database and can be queried by your API!
======================================================================
```

---

### Step 3: Deploy Lightweight API to Vercel

#### 3.1 Deploy to Production

```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Deploy to Vercel
vercel --prod
```

**What gets deployed:**
- ✅ `api/ml_lightweight.py` (queries database, NO ML libraries)
- ✅ Only `psycopg2-binary` dependency (~5MB)
- ✅ Fast cold starts (~200ms)
- ✅ Minimal function usage (1 function)

#### 3.2 Test the API

```bash
# Check ML system status
curl https://engineeringlogintelligence.vercel.app/api/ml_lightweight?action=status

# Expected response:
{
  "success": true,
  "ml_system": "active",
  "architecture": "batch_processing",
  "deployment_size": "lightweight (no ML libraries in Vercel)",
  "prediction_source": "pre-computed (GitHub Actions)",
  "latest_prediction": "2025-10-11T14:30:00Z",
  "total_predictions": 1000,
  "query_time": "~10ms (database)",
  "ml_compute_time": "~28ms (GitHub Actions)"
}

# Get recent predictions
curl https://engineeringlogintelligence.vercel.app/api/ml_lightweight?action=analyze

# Get statistics
curl https://engineeringlogintelligence.vercel.app/api/ml_lightweight?action=stats
```

---

### Step 4: Integrate with Frontend Dashboard

#### 4.1 Update Dashboard to Use New Endpoint

Your dashboard should call:
```javascript
// Get ML predictions
fetch('https://engineeringlogintelligence.vercel.app/api/ml_lightweight?action=analyze')
  .then(res => res.json())
  .then(data => {
    console.log(`Got ${data.total} predictions`);
    console.log(`Query time: ${data.query_time}`);
    // Display predictions in UI
  });

// Get ML statistics
fetch('https://engineeringlogintelligence.vercel.app/api/ml_lightweight?action=stats')
  .then(res => res.json())
  .then(data => {
    console.log(`Anomaly rate: ${data.statistics.anomaly_rate * 100}%`);
    // Display stats in dashboard
  });
```

#### 4.2 Add ML Status Indicator

Show users that predictions are pre-computed:
```javascript
fetch('https://engineeringlogintelligence.vercel.app/api/ml_lightweight?action=status')
  .then(res => res.json())
  .then(status => {
    // Show: "ML: Active (Batch Processing)"
    // Show: "Last Update: 2 hours ago"
    // Show: "Next Update: in 4 hours"
  });
```

---

## 📊 How the System Works

### Continuous ML Analysis Loop

```
1. New logs arrive in database
   ↓
2. Every 6 hours, GitHub Actions runs:
   - Finds logs without predictions
   - Loads trained models
   - Analyzes all new logs in batch
   - Stores predictions in ml_predictions table
   ↓
3. Your API queries ml_predictions table
   - Fast database queries (10ms)
   - Always returns recent predictions
   - No ML computation in Vercel
   ↓
4. Dashboard displays predictions
   - Shows classification results
   - Highlights anomalies
   - Displays confidence scores
```

---

## 🎨 Database Schema

The batch processing creates this table:

```sql
CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    log_entry_id INTEGER REFERENCES log_entries(id),
    predicted_level VARCHAR(10),        -- INFO, WARN, ERROR, etc.
    level_confidence DECIMAL(5,3),      -- 0.000 to 1.000
    is_anomaly BOOLEAN,                 -- true if anomalous
    anomaly_score DECIMAL(5,3),         -- 0.000 to 1.000
    anomaly_confidence DECIMAL(5,3),    -- model confidence
    severity VARCHAR(20),                -- low, medium, high, critical
    model_version VARCHAR(50),           -- training timestamp
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_ml_predictions_log_entry_id ON ml_predictions(log_entry_id);
CREATE INDEX idx_ml_predictions_predicted_at ON ml_predictions(predicted_at);
```

---

## 📈 Performance Comparison

| Metric | Serverless ML | Batch Processing |
|--------|---------------|------------------|
| **Response Time** | 500ms - 3s | 10-50ms |
| **Cold Start** | 3-5 seconds | 200-300ms |
| **Deployment Size** | 55MB+ | 5MB |
| **Scalability** | 1 log at a time | 1000s at once |
| **Vercel Functions** | 2-3 functions | 1 function |
| **Cost per 1000 predictions** | High | Near zero |
| **Hobby Tier Compatible** | ❌ Barely | ✅ Perfect |

**Result: 10x faster, 90% smaller deployment!**

---

## 🔧 Configuration Options

### Change Analysis Frequency

Edit `.github/workflows/ml_analysis.yml`:

```yaml
on:
  schedule:
    # Every 6 hours (default)
    - cron: '0 */6 * * *'
    
    # Or every hour for faster updates
    # - cron: '0 * * * *'
    
    # Or every 30 minutes
    # - cron: '*/30 * * * *'
```

### Change Batch Size

Edit `scripts/ml_batch_analysis.py`:

```python
# Analyze last 24 hours (default)
WHERE le.timestamp > NOW() - INTERVAL '24 hours'

# Or analyze last 1 hour
WHERE le.timestamp > NOW() - INTERVAL '1 hour'

# Or limit to specific number
LIMIT 1000  # Change to 5000 for more
```

---

## 🐛 Troubleshooting

### Issue: Workflow fails with "DATABASE_URL not set"

**Solution:** Add `DATABASE_URL` secret in GitHub:
- Settings → Secrets and variables → Actions
- New repository secret
- Name: `DATABASE_URL`, Value: Your PostgreSQL URL

### Issue: "No module named 'sklearn'"

**Solution:** The workflow installs it automatically. If it fails:
1. Check the "Install dependencies" step in Actions
2. Ensure `requirements.txt` in the workflow is correct

### Issue: "ml_predictions table doesn't exist"

**Solution:** The batch script creates it automatically on first run.
If it fails, run manually:
```bash
python scripts/ml_batch_analysis.py
```

### Issue: "No logs to analyze"

**Solution:** This means all recent logs already have predictions!
- This is normal after the first run
- New logs will be analyzed in the next batch
- Check with: `SELECT COUNT(*) FROM ml_predictions;`

### Issue: API returns empty results

**Solution:** 
1. Check if batch processing has run: Look at Actions tab
2. Check predictions exist: Query `ml_predictions` table
3. Check time range: API returns last 24 hours only

---

## 🎓 What You Learned

1. **Why batch processing is better than serverless ML**
   - Smaller deployments
   - Faster responses
   - More scalable
   - Fits Vercel Hobby tier

2. **How GitHub Actions works**
   - Free compute for ML processing
   - Scheduled workflows (cron)
   - Secrets management

3. **Database-backed ML predictions**
   - Pre-compute expensive operations
   - Fast queries for serving
   - Historical prediction data

4. **Separation of concerns**
   - Heavy compute: GitHub Actions
   - Lightweight serving: Vercel
   - Storage: PostgreSQL

---

## ✅ Success Criteria

Your ML system is working when:

1. ✅ GitHub Actions workflow completes successfully
2. ✅ `ml_predictions` table contains data
3. ✅ API `/api/ml_lightweight?action=status` returns `"ml_system": "active"`
4. ✅ API `/api/ml_lightweight?action=analyze` returns predictions
5. ✅ Dashboard displays ML classifications and anomalies

---

## 🚀 Next Steps

Once the basic system is working:

1. **Add Real-time Alerts**
   - Set up notifications for anomalies
   - Send Slack/email alerts for critical issues

2. **Improve Models**
   - Retrain with more data monthly
   - Experiment with different algorithms
   - Track model performance over time

3. **Add A/B Testing**
   - Train multiple model versions
   - Compare accuracy in production
   - Automatically select best model

4. **Scale Up**
   - Increase batch frequency (hourly)
   - Analyze more logs per batch (10,000+)
   - Add model versioning and rollback

---

## 📚 Related Documentation

- [ML Architecture Decision](ML_ARCHITECTURE_DECISION.md) - Why we chose batch processing
- [Data Overview for ML](DATA_OVERVIEW_FOR_ML.md) - Understanding your log data
- [Technical Architecture](../TECHNICAL_ARCHITECTURE.md) - Overall system design

---

## 🎉 Congratulations!

You now have a production-ready ML system that:
- Analyzes thousands of logs automatically
- Provides fast predictions via API
- Scales efficiently within free tier limits
- Follows industry best practices

This architecture is how major companies handle ML at scale!

