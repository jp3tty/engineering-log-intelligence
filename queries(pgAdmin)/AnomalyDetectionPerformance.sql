--Compare ML predictions vs orignal anomaly flags
SELECT
	CASE
		WHEN le.is_anomaly = TRUE AND mp.is_anomaly = TRUE THEN 'True Positive (Both agree)'
		WHEN le.is_anomaly = FALSE AND mp.is_anomaly = FALSE THEN 'True Negative (Both agree)'
		WHEN le.is_anomaly = TRUE AND mp.is_anomaly = FALSE THEN 'False Negative (ML missed)'
		WHEN le.is_anomaly = FALSE AND mp.is_anomaly = TRUE THEN 'False Positive (ML flageged)'
	END as prediction_type,
	COUNT(*) as count,
	ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM log_entries le
INNER JOIN ml_predictions mp ON le.id = mp.log_entry_id
GROUP BY prediction_type
ORDER BY count DESC;