--Find requests that span multiple systems
SELECT
	request_id,
	COUNT(*) as log_count,
	COUNT(DISTINCT source_type) as systems_involved,
	STRING_AGG(DISTINCT source_type::text, ', ') as systems,
	MIN(timestamp) as start_time,
	MAX(timestamp) as end_time,
	EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) as duration_seconds,
	COUNT(CASE WHEN level IN ('ERROR', 'FATAL') THEN 1 END) as errors
FROM log_entries
WHERE request_id IS NOT NULL
	AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY request_id
HAVING COUNT(DISTINCT source_type) > 1   -- Only multi-system requests
ORDER BY errors DESC, duration_seconds DESC
LIMIT 20;