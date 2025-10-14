--User session patterns and issues
SELECT
	session_id,
	ip_address,
	COUNT(*) as actions,
	COUNT(DISTINCT host) as hosts_accessed,
	MIN(timestamp) as session_start,
	MAX(timestamp) as session_end,
	EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp)))/60 as duration_minutes,
	COUNT(CASE WHEN level = 'ERROR' THEN 1 END) as errors_in_session
FROM log_entries
WHERE session_id IS NOT NULL
	AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY session_id, ip_address
HAVING COUNT(CASE WHEN level = 'ERROR' THEN 1 END) > 0   -- Sessions with errors
ORDER BY errors_in_session DESC, duration_minutes DESC
LIMIT 20;