SELECT
	pg_database.datname AS database_name,
	pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'railway';