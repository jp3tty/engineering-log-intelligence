-- Show which fields are in which tables
WITH log_cols AS (
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'log_entries'
),
ml_cols AS (
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'ml_predictions'
)
SELECT 
    COALESCE(l.column_name, m.column_name) as column_name,
    CASE 
        WHEN l.column_name IS NOT NULL AND m.column_name IS NOT NULL THEN 'Both tables'
        WHEN l.column_name IS NOT NULL THEN 'log_entries only'
        WHEN m.column_name IS NOT NULL THEN 'ml_predictions only'
    END as found_in
FROM log_cols l
FULL OUTER JOIN ml_cols m ON l.column_name = m.column_name
ORDER BY 
    CASE 
        WHEN l.column_name IS NOT NULL AND m.column_name IS NOT NULL THEN 1
        WHEN l.column_name IS NOT NULL THEN 2
        ELSE 3
    END,
    column_name;