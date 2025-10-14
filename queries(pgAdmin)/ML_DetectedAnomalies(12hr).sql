-- Show logs with ML-detected anomalies in last 12 hours
SELECT 
    le.log_id,
    le.timestamp,
    le.level,
    le.message,
    le.source_type,
    le.host,
    le.is_anomaly as log_entry_anomaly,
    mp.is_anomaly as ml_predicted_anomaly,
    mp.predicted_level,
    mp.anomaly_score,
    mp.level_confidence
FROM log_entries le
INNER JOIN ml_predictions mp ON le.id = mp.log_entry_id
WHERE mp.is_anomaly = TRUE
    AND le.timestamp > NOW() - INTERVAL '12 hours'
ORDER BY le.timestamp DESC;