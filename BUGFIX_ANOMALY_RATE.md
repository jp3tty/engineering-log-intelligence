# 🐛 Bug Fix: Anomaly Rate Display (830% → 8.3%)

**Date:** October 17, 2025  
**Issue:** Dashboard showing anomaly rate as 830% instead of 8.3%  
**Status:** ✅ Fixed

---

## 🔍 **Root Cause**

**Double percentage conversion** - both API and frontend were multiplying by 100:

```
API:      8.3 (already percentage)
Frontend: 8.3 × 100 = 830% ❌
```

---

## 🛠️ **Files Fixed**

### 1. **`frontend/src/composables/useMLData.js`**

**Line 157 - Before:**
```javascript
return mlStats.value.statistics.anomaly_rate * 100 // ❌ Double conversion
```

**After:**
```javascript
return mlStats.value.statistics.anomaly_rate // ✅ API already returns percentage
```

---

### 2. **`frontend/src/components/MLDashboard.vue`**

**Line 49 - Before:**
```vue
{{ ((stats.statistics?.anomaly_rate || 0) * 100).toFixed(1) }}% rate
```

**After:**
```vue
{{ (stats.statistics?.anomaly_rate || 0).toFixed(1) }}% rate
```

---

### 3. **Field Name Consistency**

**Issue:** Frontend used `anomalies_detected`, API returns `anomaly_count`

**Fixed in:**
- `useMLData.js` line 143: `anomalies_detected` → `anomaly_count`
- `MLDashboard.vue` line 48: `anomalies_detected` → `anomaly_count`

---

## ✅ **Expected Results**

After these changes, the dashboard will correctly display:

| Metric | Before | After |
|--------|--------|-------|
| Anomaly Rate | **830.0%** ❌ | **8.3%** ✅ |
| Anomalies | May be 0 | **415** ✅ |
| Display | Broken | Accurate |

---

## 📊 **API Response Structure (Reference)**

The `/api/ml_lightweight?action=stats` endpoint returns:

```json
{
  "success": true,
  "statistics": {
    "severity_distribution": [
      {"severity": "medium", "count": 706},
      {"severity": "low", "count": 663},
      {"severity": "high", "count": 413}
    ],
    "total_predictions": 5000,
    "anomaly_count": 415,           // ← Use this field
    "high_severity_count": 413,
    "anomaly_rate": 8.3              // ← Already a percentage (not 0.083)
  },
  "period": "last_24_hours"
}
```

**Note:** `anomaly_rate` is already calculated as a percentage in the API (line 209 of `ml_lightweight.py`)

---

## 🧪 **Testing**

After deploying these changes:

1. **Dashboard Widget** should show: `8.3% Anomaly Rate`
2. **ML Dashboard** should show: `415 Anomalies Detected (8.3% rate)`
3. **Values should match** the database query:
   ```sql
   SELECT 
     COUNT(*) as total,
     SUM(CASE WHEN is_anomaly THEN 1 END) as anomaly_count
   FROM ml_predictions
   WHERE predicted_at > NOW() - INTERVAL '24 hours';
   ```

---

## 🚀 **Deployment**

These are frontend-only changes. Deploy steps:

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy to Vercel (automatic on git push)

3. Clear browser cache and refresh dashboard

---

## 📝 **Lessons Learned**

1. ✅ **Standardize units** - Decide whether percentages are 0-1 or 0-100
2. ✅ **Document API responses** - Make it clear what format data is in
3. ✅ **Consistent field names** - `anomaly_count` everywhere, not mixed with `anomalies_detected`
4. ✅ **Add unit tests** - Would have caught this: `expect(8.3 * 100).not.toBe(830)`

---

**Fixed By:** Engineering Log Intelligence Team  
**Related:** Enhanced ML Integration (96.3% accuracy model)

