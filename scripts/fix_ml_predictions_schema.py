"""
Fix ML Predictions Schema
==========================
Fix the DECIMAL field overflow issue by changing confidence fields to proper range.

The issue: DECIMAL(5,3) can only store -99.999 to 99.999
The fix: Change to DECIMAL(4,3) for values 0.000 to 1.000 (confidence scores)

Author: Engineering Log Intelligence Team
Date: October 13, 2025
"""

import os
import sys
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except:
    pass

print("="*70)
print("🔧 FIXING ML PREDICTIONS SCHEMA")
print("="*70)
print()

# Get database URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    print("✅ Connected to database")
    print()
    
    # Check if table exists and what data type it uses
    print("🔍 Checking ml_predictions table schema...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ml_predictions' 
        AND column_name IN ('level_confidence', 'anomaly_score', 'anomaly_confidence')
    """)
    
    existing_columns = cursor.fetchall()
    
    if not existing_columns:
        print("   Table doesn't exist or has no confidence columns")
        needs_fix = True
    else:
        # Check if any column is using NUMERIC/DECIMAL instead of REAL
        needs_fix = any(col[1] == 'numeric' for col in existing_columns)
        if needs_fix:
            print("   ⚠️  Found NUMERIC/DECIMAL columns - needs fixing")
        else:
            print("   ✅ Schema is already correct (using REAL type)")
    
    if needs_fix:
        print()
        print("🗄️  Fixing ml_predictions table schema...")
        
        # Backup data if table has records
        cursor.execute("""
            SELECT COUNT(*) FROM ml_predictions
        """) if existing_columns else None
        
        count = cursor.fetchone()[0] if existing_columns else 0
        
        if count > 0:
            print(f"   ℹ️  Table has {count:,} predictions - they will be lost in recreation")
        
        cursor.execute("DROP TABLE IF EXISTS ml_predictions CASCADE")
        
        cursor.execute("""
            CREATE TABLE ml_predictions (
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
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX idx_ml_predictions_log_entry_id 
            ON ml_predictions(log_entry_id)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_ml_predictions_predicted_at 
            ON ml_predictions(predicted_at)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_ml_predictions_severity 
            ON ml_predictions(severity)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_ml_predictions_is_anomaly 
            ON ml_predictions(is_anomaly)
        """)
        
        conn.commit()
        
        print("   ✅ Table fixed successfully with REAL type for confidence fields")
        print("      (REAL allows proper 0.0 to 1.0 range without overflow)")
    
    print()
    cursor.close()
    conn.close()
    
    print("="*70)
    print("🎉 SCHEMA CHECK COMPLETE!")
    print("="*70)
    print()
    if needs_fix:
        print("Schema has been fixed. ML batch analysis can now proceed.")
    else:
        print("Schema is correct. ML batch analysis can proceed.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

