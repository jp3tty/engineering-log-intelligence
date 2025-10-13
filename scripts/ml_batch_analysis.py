"""
ML Batch Analysis Script
=========================
This script runs ML analysis on logs and stores predictions in the database.

This runs in GitHub Actions (not Vercel), so we can use heavy ML libraries
without impacting the serverless function performance.

Author: Engineering Log Intelligence Team
Date: October 11, 2025
"""

import os
import sys
import pickle
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except:
    pass

print("="*70)
print("🤖 ML BATCH ANALYSIS - Running in GitHub Actions")
print("="*70)
print()

# =============================================================================
# STEP 1: Load ML Models
# =============================================================================
print("📂 Loading ML models...")

try:
    with open('models/log_classifier_simple.pkl', 'rb') as f:
        classifier = pickle.load(f)
    with open('models/anomaly_detector_simple.pkl', 'rb') as f:
        anomaly_detector = pickle.load(f)
    with open('models/vectorizer_simple.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('models/metadata_simple.json', 'r') as f:
        metadata = json.load(f)
    
    print("✅ Models loaded successfully")
    print(f"   Classifier accuracy: {metadata['classifier_accuracy']*100:.1f}%")
    print(f"   Anomaly detector accuracy: {metadata['anomaly_detector_accuracy']*100:.1f}%")
    print()
except Exception as e:
    print(f"❌ Failed to load models: {e}")
    sys.exit(1)

# =============================================================================
# STEP 2: Connect to Database
# =============================================================================
print("📊 Connecting to database...")

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("✅ Connected to database")
    print()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

# =============================================================================
# STEP 3: Create ML Predictions Table (if it doesn't exist)
# =============================================================================
print("🗄️  Setting up ML predictions table...")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS ml_predictions (
        id SERIAL PRIMARY KEY,
        log_entry_id INTEGER REFERENCES log_entries(id),
        predicted_level VARCHAR(10),
        level_confidence REAL,
        is_anomaly BOOLEAN,
        anomaly_score REAL,
        anomaly_confidence REAL,
        severity VARCHAR(20),
        model_version VARCHAR(50),
        predicted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(log_entry_id)
    )
""")

# Create index for fast lookups
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ml_predictions_log_entry_id 
    ON ml_predictions(log_entry_id)
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ml_predictions_predicted_at 
    ON ml_predictions(predicted_at)
""")

conn.commit()
print("✅ ML predictions table ready")
print()

# =============================================================================
# STEP 4: Get Logs That Need Analysis
# =============================================================================
print("📋 Fetching logs that need ML analysis...")

# Get logs from the last 24 hours that don't have predictions yet
cursor.execute("""
    SELECT 
        le.id, le.log_id, le.message, le.level, le.timestamp
    FROM log_entries le
    LEFT JOIN ml_predictions mp ON le.id = mp.log_entry_id
    WHERE 
        le.timestamp > NOW() - INTERVAL '24 hours'
        AND le.message IS NOT NULL
        AND mp.id IS NULL
    ORDER BY le.timestamp DESC
    LIMIT 1000
""")

logs_to_analyze = cursor.fetchall()
print(f"✅ Found {len(logs_to_analyze):,} logs needing analysis")

if len(logs_to_analyze) == 0:
    print("ℹ️  No new logs to analyze. All caught up!")
    cursor.close()
    conn.close()
    sys.exit(0)

print()

# =============================================================================
# STEP 5: Run ML Analysis
# =============================================================================
print("🤖 Running ML analysis...")
print()

analyzed_count = 0
predictions = []

for log in logs_to_analyze:
    try:
        # Convert message to numbers
        X = vectorizer.transform([log['message']])
        
        # Predict with classifier
        level = classifier.predict(X)[0]
        level_proba = classifier.predict_proba(X)[0]
        level_confidence = float(max(level_proba))
        
        # Predict with anomaly detector
        is_anomaly = anomaly_detector.predict(X)[0]
        anomaly_proba = anomaly_detector.predict_proba(X)[0]
        anomaly_score = float(anomaly_proba[1] if len(anomaly_proba) > 1 else anomaly_proba[0])
        anomaly_confidence = float(max(anomaly_proba))
        
        # Ensure all confidence values are in valid range [0, 1]
        # This prevents database overflow errors
        level_confidence = max(0.0, min(1.0, level_confidence))
        anomaly_score = max(0.0, min(1.0, anomaly_score))
        anomaly_confidence = max(0.0, min(1.0, anomaly_confidence))
        
        # Determine severity
        if is_anomaly:
            severity = "high"
        elif level in ['ERROR', 'FATAL']:
            severity = "medium"
        elif level == 'WARN':
            severity = "low"
        else:
            severity = "info"
        
        predictions.append({
            'log_entry_id': log['id'],
            'predicted_level': level,
            'level_confidence': level_confidence,
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': anomaly_score,
            'anomaly_confidence': anomaly_confidence,
            'severity': severity,
            'model_version': metadata['trained_at']
        })
        
        analyzed_count += 1
        
        # Show progress every 100 logs
        if analyzed_count % 100 == 0:
            print(f"   Analyzed {analyzed_count:,} logs...")
    
    except Exception as e:
        print(f"⚠️  Error analyzing log {log['id']}: {e}")
        continue

print(f"✅ Analyzed {analyzed_count:,} logs")
print()

# =============================================================================
# STEP 6: Store Predictions in Database
# =============================================================================
print("💾 Storing predictions in database...")

stored_count = 0

for pred in predictions:
    try:
        cursor.execute("""
            INSERT INTO ml_predictions (
                log_entry_id, predicted_level, level_confidence,
                is_anomaly, anomaly_score, anomaly_confidence,
                severity, model_version
            ) VALUES (
                %(log_entry_id)s, %(predicted_level)s, %(level_confidence)s,
                %(is_anomaly)s, %(anomaly_score)s, %(anomaly_confidence)s,
                %(severity)s, %(model_version)s
            )
            ON CONFLICT (log_entry_id) DO UPDATE SET
                predicted_level = EXCLUDED.predicted_level,
                level_confidence = EXCLUDED.level_confidence,
                is_anomaly = EXCLUDED.is_anomaly,
                anomaly_score = EXCLUDED.anomaly_score,
                anomaly_confidence = EXCLUDED.anomaly_confidence,
                severity = EXCLUDED.severity,
                predicted_at = NOW()
        """, pred)
        
        stored_count += 1
        
        # Commit every 100 records
        if stored_count % 100 == 0:
            conn.commit()
            print(f"   Stored {stored_count:,} predictions...")
    
    except Exception as e:
        print(f"⚠️  Error storing prediction: {e}")
        continue

# Final commit
conn.commit()
print(f"✅ Stored {stored_count:,} predictions")
print()

# =============================================================================
# STEP 7: Generate Summary Statistics
# =============================================================================
print("📊 Generating summary statistics...")

# Count predictions by severity
cursor.execute("""
    SELECT severity, COUNT(*) as count
    FROM ml_predictions
    WHERE predicted_at > NOW() - INTERVAL '24 hours'
    GROUP BY severity
    ORDER BY count DESC
""")

severity_stats = cursor.fetchall()

print()
print("Predictions by Severity (Last 24 hours):")
for stat in severity_stats:
    print(f"   {stat['severity']:10} | {stat['count']:6,} logs")

# Count anomalies
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomalies
    FROM ml_predictions
    WHERE predicted_at > NOW() - INTERVAL '24 hours'
""")

anomaly_stats = cursor.fetchone()

print()
print(f"Anomaly Detection (Last 24 hours):")
print(f"   Total predictions: {anomaly_stats['total']:,}")
print(f"   Anomalies found:   {anomaly_stats['anomalies']:,} ({anomaly_stats['anomalies']/max(anomaly_stats['total'],1)*100:.1f}%)")

# =============================================================================
# STEP 8: Save Results to File
# =============================================================================
print()
print("📄 Saving results to file...")

results = {
    "timestamp": datetime.now().isoformat(),
    "logs_analyzed": analyzed_count,
    "predictions_stored": stored_count,
    "model_version": metadata['trained_at'],
    "model_accuracy": {
        "classifier": metadata['classifier_accuracy'],
        "anomaly_detector": metadata['anomaly_detector_accuracy']
    },
    "statistics": {
        "severity": [dict(s) for s in severity_stats],
        "total_predictions": anomaly_stats['total'],
        "anomalies_detected": anomaly_stats['anomalies'],
        "anomaly_rate": anomaly_stats['anomalies']/max(anomaly_stats['total'],1)
    }
}

with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✅ Results saved to analysis_results.json")

# Close connection
cursor.close()
conn.close()

print()
print("="*70)
print("🎉 ML BATCH ANALYSIS COMPLETE!")
print("="*70)
print()
print(f"✅ Analyzed: {analyzed_count:,} logs")
print(f"✅ Stored: {stored_count:,} predictions")
print(f"✅ Anomalies: {anomaly_stats['anomalies']:,}")
print()
print("💡 Predictions are now in the database and can be queried by your API!")
print("="*70)

