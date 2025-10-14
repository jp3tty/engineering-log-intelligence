--Log volume by hour for last 7 days
SELECT
	DATE_TRUNC('hour', timestamp) as hour,
	source_type,
	COUNT(*) as log_count,
	COUNT(CASE WHEN level IN ('ERROR', 'FATAL') THEN 1 END) as error_count
FROM log_entries
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', timestamp), source_type
ORDER BY hour DESC, source_type;