"""
ML Batch Analysis Script
=========================
This script runs ML analysis on logs and stores predictions in the database.

Updated: October 17, 2025 - Using enhanced business severity model

This runs in GitHub Actions (not Vercel), so we can use heavy ML libraries
without impacting the serverless function performance.

Author: Engineering Log Intelligence Team
Date: October 17, 2025
"""

import os
import sys
import pickle
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from scipy.sparse import csr_matrix, hstack

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except:
    pass

print("="*70)
print("🤖 ML BATCH ANALYSIS - Enhanced Severity Model")
print("="*70)
print()

# =============================================================================
# STEP 1: Load Enhanced ML Models
# =============================================================================
print("📂 Loading enhanced ML models...")

try:
    # Load enhanced business severity classifier
    with open('models/severity_classifier_enhanced.pkl', 'rb') as f:
        classifier = pickle.load(f)
    with open('models/severity_vectorizer_enhanced.pkl', 'rb') as f:
        severity_vectorizer = pickle.load(f)
    with open('models/severity_encoders_enhanced.pkl', 'rb') as f:
        encoders = pickle.load(f)
    with open('models/severity_metadata_enhanced.json', 'r') as f:
        metadata = json.load(f)
    
    # Load anomaly detector with its own vectorizer
    with open('models/anomaly_detector_simple.pkl', 'rb') as f:
        anomaly_detector = pickle.load(f)
    with open('models/vectorizer_simple.pkl', 'rb') as f:
        anomaly_vectorizer = pickle.load(f)
    
    print("✅ Enhanced models loaded successfully")
    print(f"   Business Severity Model: {metadata['accuracy']*100:.1f}% accuracy")
    print(f"   Total features: {metadata['total_features']}")
    print(f"   Severity levels: {', '.join(metadata['severity_levels'])}")
    print()
except Exception as e:
    print(f"❌ Failed to load models: {e}")
    print("💡 Make sure you've run train_models_severity_enhanced.py first")
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
# Include all features needed for enhanced severity prediction
cursor.execute("""
    SELECT 
        le.id, le.log_id, le.message, le.level, le.timestamp,
        le.service, le.endpoint, le.http_status, le.response_time_ms
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
        # Extract features with defaults
        message = log.get('message', '')
        service = log.get('service', 'unknown')
        endpoint = log.get('endpoint', 'unknown')
        level = log.get('level', 'INFO').upper()
        http_status = int(log.get('http_status') or 200)
        response_time = float(log.get('response_time_ms') or 0)
        
        # STEP 1: Vectorize message text (using severity vectorizer)
        X_text = severity_vectorizer.transform([message])
        
        # STEP 2: Encode categorical features (handle unknown categories gracefully)
        try:
            service_encoded = csr_matrix(
                encoders['service_encoder'].transform([service]).reshape(-1, 1)
            )
        except ValueError:
            # Unknown service - use 'unknown' or first known service
            service_encoded = csr_matrix(
                encoders['service_encoder'].transform(['unknown'] if 'unknown' in encoders['service_encoder'].classes_ else [encoders['service_encoder'].classes_[0]]).reshape(-1, 1)
            )
        
        try:
            endpoint_encoded = csr_matrix(
                encoders['endpoint_encoder'].transform([endpoint]).reshape(-1, 1)
            )
        except ValueError:
            # Unknown endpoint - use first known endpoint
            endpoint_encoded = csr_matrix(
                encoders['endpoint_encoder'].transform([encoders['endpoint_encoder'].classes_[0]]).reshape(-1, 1)
            )
        
        try:
            level_encoded = csr_matrix(
                encoders['level_encoder'].transform([level]).reshape(-1, 1)
            )
        except ValueError:
            # Unknown level - use INFO
            level_encoded = csr_matrix(
                encoders['level_encoder'].transform(['INFO']).reshape(-1, 1)
            )
        
        # STEP 3: Normalize numerical features
        http_status_normalized = http_status / 100.0
        response_time_normalized = min(response_time / 1000.0, 10.0)
        
        # Apply scaling
        X_numerical_raw = [[http_status_normalized, response_time_normalized]]
        X_numerical_scaled = encoders['scaler'].transform(X_numerical_raw)
        X_numerical = csr_matrix(X_numerical_scaled)
        
        # STEP 4: Combine all features
        X = hstack([X_text, service_encoded, endpoint_encoded, level_encoded, X_numerical])
        
        # STEP 5: Predict business severity with enhanced model
        severity = classifier.predict(X)[0]
        severity_proba = classifier.predict_proba(X)[0]
        severity_confidence = float(max(severity_proba))
        
        # STEP 6: Predict anomalies (using anomaly vectorizer)
        X_anomaly = anomaly_vectorizer.transform([message])
        is_anomaly = anomaly_detector.predict(X_anomaly)[0]
        anomaly_proba = anomaly_detector.predict_proba(X_anomaly)[0]
        anomaly_score = float(anomaly_proba[1] if len(anomaly_proba) > 1 else anomaly_proba[0])
        anomaly_confidence = float(max(anomaly_proba))
        
        # Ensure all confidence values are in valid range [0, 1]
        severity_confidence = max(0.0, min(1.0, severity_confidence))
        anomaly_score = max(0.0, min(1.0, anomaly_score))
        anomaly_confidence = max(0.0, min(1.0, anomaly_confidence))
        
        predictions.append({
            'log_entry_id': log['id'],
            'predicted_level': level,  # Use actual log level
            'level_confidence': severity_confidence,  # Using severity confidence here
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': anomaly_score,
            'anomaly_confidence': anomaly_confidence,
            'severity': severity,  # Business severity from enhanced model
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
    "model_type": "business_severity_enhanced",
    "model_accuracy": {
        "severity_classifier": metadata['accuracy'],
        "total_features": metadata['total_features']
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

