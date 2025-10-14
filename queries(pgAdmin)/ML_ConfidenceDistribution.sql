-- See how confident the ML model is
SELECT 
    CASE 
        WHEN anomaly_confidence >= 0.9 THEN 'Very High (90-100%)'
        WHEN anomaly_confidence >= 0.75 THEN 'High (75-89%)'
        WHEN anomaly_confidence >= 0.5 THEN 'Medium (50-74%)'
        ELSE 'Low (<50%)'
    END as confidence_range,
    COUNT(*) as count,
    COUNT(CASE WHEN is_anomaly = TRUE THEN 1 END) as anomalies_in_range,
    ROUND(AVG(anomaly_score)::numeric, 3) as avg_anomaly_score
FROM ml_predictions
GROUP BY confidence_range
ORDER BY MIN(anomaly_confidence) DESC;