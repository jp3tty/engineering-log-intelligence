--See if we have data that COULD create correlations
SELECT
	'request_id' as correlation_field,
	COUNT(*) as logs_with_field,
	COUNT(DISTINCT request_id) as unique_values
FROM log_entries
WHERE request_id IS NOT NULL
UNION ALL
SELECT
	'session_id',
	COUNT(*),
	COUNT(DISTINCT session_id)
FROM log_entries
WHERE session_id IS NOT NULL
UNION ALL
SELECT
	'ip_address',
	COUNT(*),
	COUNT(DISTINCT ip_address)
FROM log_entries
WHERE ip_address IS NOT NULL
UNION ALL
SELECT
	'correlation_id',
	COUNT(*),
	COUNT(DISTINCT correlation_id)
FROM log_entries
WHERE correlation_id IS NOT NULL;