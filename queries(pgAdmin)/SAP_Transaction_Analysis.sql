-- SAP Transaction Analysis
SELECT 
    transaction_code,
    sap_system,
    department,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN level IN ('ERROR', 'FATAL') THEN 1 END) as failed_transactions,
    ROUND(100.0 * COUNT(CASE WHEN level IN ('ERROR', 'FATAL') THEN 1 END) / COUNT(*), 2) as error_rate
FROM log_entries
WHERE source_type = 'sap'
    AND transaction_code IS NOT NULL
GROUP BY transaction_code, sap_system, department
ORDER BY total_transactions DESC
LIMIT 20;