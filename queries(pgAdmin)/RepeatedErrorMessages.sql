-- Find recurring error patterns
SELECT 
    LEFT(message, 80) as error_pattern,
    source_type,
    COUNT(*) as occurrences,
    COUNT(DISTINCT host) as affected_hosts,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen,
    MAX(timestamp) - MIN(timestamp) as duration
FROM log_entries
WHERE level IN ('ERROR', 'FATAL')
    AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY LEFT(message, 80), source_type
HAVING COUNT(*) >= 10  -- At least 10 occurrences
ORDER BY occurrences DESC
LIMIT 20;