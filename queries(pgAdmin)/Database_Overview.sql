SELECT
	'log_entries' as table_name,
	COUNT(*) as row_count,
	MIN(timestamp) as oldest,
	MAX(timestamp) as newest
FROM log_entries
UNION ALL
SELECT
	'ml_predictions',
	COUNT(*),
	MIN(predicted_at),
	MAX(predicted_at)
FROM ml_predictions
UNION ALL
SELECT 'users', COUNT(*), MIN(created_at), MAX(created_at) FROM users
UNION ALL
SELECT 'correlations', COUNT(*), MIN(created_at), MAX(created_at) FROM correlations
UNION ALL
SELECT 'alerts', COUNT(*), MIN(created_at), MAX(created_at) FROM correlations
UNION ALL
SELECT 'dashboards', COUNT(*), MIN(created_at), MAX(created_at) FROM correlations
ORDER BY row_count DESC;