--See which systems are generating what type of logs
SELECT
	source_type,
	level,
	COUNT(*) as count,
	ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM log_entries
GROUP BY source_type, level
ORDER BY source_type, count DESC;