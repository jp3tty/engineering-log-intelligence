--Most suspicious logs based on ML analysis
SELECT
	le.log_id,
	le.timestamp,
	le.level,
	le.source_type,
	le.host,
	le.service,
	LEFT(le.message, 100) as message_preview,
	mp.anomaly_score,
	mp.anomaly_confidence,
	mp.severity,
	mp.predicted_level
FROM log_entries le
INNER JOIN ml_predictions mp ON le.id = mp.log_entry_id
WHERE mp.is_anomaly = TRUE
	AND le.timestamp > NOW() - INTERVAL '7 days'
ORDER BY mp.anomaly_score DESC, mp.anomaly_confidence DESC
LIMIT 25;