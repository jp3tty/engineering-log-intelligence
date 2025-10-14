--Find which hosts/services are generating the most errors
SELECT
	host,
	service,
	COUNT(*) as error_count,
	COUNT(DISTINCT DATE_TRUNC('hour', timestamp)) as hours_with_errors,
	MIN(timestamp) as first_error,
	MAX(timestamp) as last_error
FROM log_entries
WHERE level IN ('ERROR', 'FATAL')
	AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY host, service
HAVING COUNT(*) >= 5    --At least 5 errors
ORDER BY  error_count DESC
LIMIT 20;