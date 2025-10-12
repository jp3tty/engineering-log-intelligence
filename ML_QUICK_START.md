# ML Quick Start - Real Predictions

**Date:** October 11, 2025  
**Status:** ✅ Deployed to Production  

**TL;DR:** Get real ML predictions working in 3 steps.

---

## Prerequisites

✅ You have trained models in `models/` directory  
✅ You have `DATABASE_URL` configured  
✅ Python dependencies installed

---

## 🚀 Quick Start (3 Steps)

### Step 1: Train Models (if not done)

```bash
cd engineering_log_intelligence
python train_models_simple.py
```

Wait 1-2 minutes. You'll see:
```
✅ Accuracy: 89.5%
✅ Models saved to models/
```

### Step 2: Populate Predictions

```bash
./run_ml_analysis.sh
```

Wait 30-60 seconds. You'll see:
```
✅ Analyzed 1,234 logs
✅ Stored 1,234 predictions
```

### Step 3: Test It

```bash
# Test API
curl https://your-app.vercel.app/api/ml?action=analyze | grep source

# Should show: "source": "ml_predictions_table"
```

Or open your app:
1. Go to **Log Analysis** tab
2. Click "Run AI Analysis" on any log
3. Check browser console for `source: "ml_predictions_table"`

---

## ✅ Verification

**Models exist:**
```bash
ls models/*.pkl
# Should show 3 .pkl files
```

**Predictions in database:**
```bash
# Using psql:
psql $DATABASE_URL -c "SELECT COUNT(*) FROM ml_predictions;"

# Should return a number > 0
```

**API using real data:**
```bash
curl https://your-app.vercel.app/api/ml?action=analyze | python -m json.tool
```

Look for:
```json
{
  "data": {
    "model_status": {
      "source": "ml_predictions_table"  // ← This means it's working!
    }
  }
}
```

---

## 🔄 Automate (Optional)

### GitHub Actions Setup

1. **Add secret:**
   ```
   GitHub → Settings → Secrets → Actions
   Add: DATABASE_URL = your-postgres-url
   ```

2. **Push code:**
   ```bash
   git add .
   git commit -m "Add real ML predictions"
   git push
   ```

3. **Runs automatically every 6 hours** ✨

Or trigger manually:
```
GitHub → Actions → ML Batch Analysis → Run workflow
```

---

## 🐛 Common Issues

### "Models not found"
```bash
python train_models_simple.py
```

### "DATABASE_URL not set"
```bash
export DATABASE_URL='your-postgres-url'
# OR
echo "DATABASE_URL=your-url" > .env.local
```

### "Using mock data"
```bash
# Populate predictions:
./run_ml_analysis.sh

# Check Vercel env:
vercel env ls
vercel env add DATABASE_URL  # if missing
```

---

## 📊 What Changed

| Before | After |
|--------|-------|
| ❌ Mock/random predictions | ✅ Real ML predictions |
| ❌ Different every time | ✅ Consistent & persistent |
| ❌ Not using trained models | ✅ Uses your trained models |

---

## 📚 Full Documentation

See: [`docs/ML_REAL_PREDICTIONS_GUIDE.md`](docs/ML_REAL_PREDICTIONS_GUIDE.md)

---

## 🎉 That's It!

Your Log Analysis tab now shows **real ML predictions** from trained models.

**Need help?** Check:
- `./run_ml_analysis.sh` output
- GitHub Actions logs
- Vercel function logs

