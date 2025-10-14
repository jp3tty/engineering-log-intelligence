--How many logs have ML predictions?
SELECT
	(SELECT COUNT(*) FROM log_entries) as total_logs,
	(SELECT COUNT(*) FROM ml_predictions) as logs_with_predictions,
	ROUND(100.0 * (SELECT COUNT(*) FROM ml_predictions) /
		NULLIF((SELECT COUNT(*) FROM log_entries), 0), 2) as coverage_percentage,
	(SELECT COUNT (*) FROM log_entries le
	 LEFT JOIN ml_predictions mp ON le.id = mp.log_entry_id
	 WHERE mp.id IS NULL) as logs_missing_predictions;