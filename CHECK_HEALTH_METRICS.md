# How to Check Your Health Metrics

## Quick Check

Visit this URL in your browser:

```
https://engineeringlogintelligence.vercel.app/api/metrics
```

**Current Production URL:** `https://engineeringlogintelligence.vercel.app`

This will show you the **exact calculation** that's being used for System Health.

## What to Look For

The response will show:

```json
{
  "success": true,
  "metrics": {
    "total_logs": <count>,           // Logs in last 24 hours
    "avg_response_time_ms": <ms>,
    "fatal_rate": <percentage>,      // % of logs that are FATAL (last 24h)
    "error_rate": <percentage>,      // % of logs that are ERROR (last 24h)
    "high_anomaly_rate": <percentage>, // % flagged as high-severity anomalies
    "high_anomaly_count": <count>,
    "system_health": <percentage>    // Final health score
  },
  "calculation": {
    "base": 99.0,
    "fatal_impact": <number>,        // fatal_rate × 3.0
    "error_impact": <number>,        // error_rate × 0.5
    "anomaly_impact": <number>       // high_anomaly_rate × 0.3
  },
  "period": "last_24_hours"
}
```

## Understanding the Results

### If fatal_rate is high (>1%)
- **Cause:** You have FATAL-level logs in last 24h
- **Impact:** Each 1% FATAL = -3% health (heavily penalized)
- **Solution:** FATAL logs should be rare in healthy systems

### If error_rate is high (>20%)
- **Cause:** You have many ERROR logs in last 24h
- **Impact:** Each 1% ERROR = -0.5% health
- **Solution:** 20% error rate = -10% health impact

### If high_anomaly_rate is high (>10%)
- **Cause:** ML model flagged many logs as high-severity anomalies
- **Impact:** Each 1% anomaly = -0.3% health
- **Solution:** Check ML predictions table

## Time Window Discrepancy

**Dashboard "Active Alerts":**
- Time window: **Last 1 hour**
- Query: `COUNT(*) WHERE timestamp > NOW() - INTERVAL '1 hour' AND level IN ('ERROR', 'FATAL')`
- Your value: **127 alerts**

**System Health Calculation:**
- Time window: **Last 24 hours**
- Query: `COUNT(*) WHERE timestamp > NOW() - INTERVAL '24 hours' AND level = 'ERROR'`
- Estimated: **127 × 24 = ~3,048 ERROR logs in 24h**

**This is why the numbers don't match!**

## Your Actual Values (October 14, 2025)

Your `/api/metrics` currently returns:
```json
{
  "metrics": {
    "total_logs": 66574,      // Last 24h
    "fatal_rate": 4.14,       // 2,756 FATAL logs (4.14%)
    "error_rate": 10.13,      // 6,744 ERROR logs (10.13%)
    "high_anomaly_rate": 3.17,// 127 high-severity anomalies
    "high_anomaly_count": 127,
    "system_health": 85.0
  },
  "calculation": {
    "base": 99.0,
    "fatal_impact": 12.43,    // 4.14% × 3.0
    "error_impact": 5.06,     // 10.13% × 0.5
    "anomaly_impact": 0.95    // 3.17% × 0.3
  }
}
```

**Your Calculation:**
```
Base:            99.0%
- Fatal impact:  -12.43%  (4.14% × 3.0)
- Error impact:  -5.06%   (10.13% × 0.5)
- Anomaly:       -0.95%   (3.17% × 0.3)
─────────────────────────
Calculated:      80.56%
System Health:   85.0% → DEGRADED ⚠️ (floored at minimum)
```

**Reality Check:**
- 66,574 logs in last 24 hours
- 2,756 FATAL logs (4.14%) - **This is high!**
- 6,744 ERROR logs (10.13%) - **This is concerning!**
- Total error/fatal: 9,500 logs (14.27% of all logs)

This level of errors would be concerning in a real production system.

## Quick Fix Options

### Option A: Accept It (Recommended)
- Your system IS reporting real issues
- 127 ERROR/FATAL logs per hour is actually concerning
- "Degraded" status is accurate

### Option B: Adjust the Calculation
If you think the calculation is too strict, you can:

1. **Reduce ERROR weight:** Change `error_rate * 0.5` to `error_rate * 0.2`
2. **Raise DEGRADED threshold:** Change 88% to 85% for "Healthy"
3. **Exclude certain log types:** Filter out expected errors

File to edit: `/api/metrics.py` lines 143-148

### Option C: Fix the Log Quality
- Reduce ERROR/FATAL logs by fixing issues
- Tune ML model to reduce false positive anomalies
- This is the "real" solution

## Conclusion

The "Degraded" status is likely **accurate** - you have a high volume of ERROR logs in the last 24 hours relative to total log volume. The calculation is working as designed to reflect **current** system state, not historical averages.

The dashboard "127 alerts" is misleading because it shows only the **last hour**, while health uses **last 24 hours**.

