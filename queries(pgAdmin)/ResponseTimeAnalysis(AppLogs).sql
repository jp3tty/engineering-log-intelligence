-- Slow endpoints and performance issues
SELECT 
    endpoint,
    http_method,
    COUNT(*) as request_count,
    ROUND(AVG(response_time_ms), 2) as avg_response_time,
    ROUND(MIN(response_time_ms), 2) as min_response_time,
    ROUND(MAX(response_time_ms), 2) as max_response_time,
    COUNT(CASE WHEN response_time_ms > 1000 THEN 1 END) as slow_requests,
    COUNT(CASE WHEN http_status >= 500 THEN 1 END) as server_errors
FROM log_entries
WHERE source_type = 'application'
    AND endpoint IS NOT NULL
    AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY endpoint, http_method
HAVING COUNT(*) >= 10
ORDER BY avg_response_time DESC
LIMIT 20;