"""
Generate Severity Training Data
================================

This script connects to the database, fetches logs, and labels them
with business severity using our calculate_severity function.

The labeled data is then used to train the ML model.

Author: Engineering Log Intelligence Team
Date: October 16, 2025
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from calculate_severity import calculate_business_severity, get_severity_stats
from collections import Counter

print("=" * 70)
print("📊 GENERATING SEVERITY TRAINING DATA")
print("=" * 70)
print()

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    pass

# Get database connection
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set in environment")
    print("   Set it with: export DATABASE_URL='your-postgres-url'")
    sys.exit(1)

print("🔌 Connecting to database...")
try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("✅ Connected successfully")
    print()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Fetch logs (prioritize business-realistic ones with service names like payment-api, user-api, etc.)
print("📥 Fetching logs from database...")
try:
    cursor.execute("""
        SELECT 
            id,
            log_id,
            level,
            message,
            source_type,
            service,
            endpoint,
            http_status,
            response_time_ms,
            is_anomaly,
            timestamp
        FROM log_entries 
        WHERE message IS NOT NULL 
        AND level IS NOT NULL
        AND service IS NOT NULL
        AND (service LIKE '%-api' OR service LIKE '%-service' OR service LIKE 'test-%' OR service LIKE '%check%')
        ORDER BY timestamp DESC 
        LIMIT 10000
    """)
    
    logs = cursor.fetchall()
    print(f"✅ Fetched {len(logs):,} logs")
    print()
except Exception as e:
    print(f"❌ Query failed: {e}")
    cursor.close()
    conn.close()
    sys.exit(1)

# Convert to dict and calculate severities
print("🏷️  Labeling logs with business severity...")
labeled_data = []
severity_counter = Counter()

for log in logs:
    # Convert RealDictRow to regular dict
    log_dict = dict(log)
    
    # Calculate severity
    severity = calculate_business_severity(log_dict)
    severity_counter[severity] += 1
    
    # Create training record
    labeled_data.append({
        'id': log_dict['id'],
        'log_id': log_dict['log_id'],
        'message': log_dict['message'],
        'severity': severity,  # This is our ML target
        'original_level': log_dict['level'],
        'source_type': log_dict['source_type'],
        'service': log_dict.get('service', log_dict['source_type']),  # Include service field
        'endpoint': log_dict['endpoint'],
        'http_status': log_dict['http_status'],
        'response_time_ms': log_dict['response_time_ms'],
        'is_anomaly': log_dict['is_anomaly'],
        'timestamp': log_dict['timestamp'].isoformat() if log_dict['timestamp'] else None
    })

print(f"✅ Labeled {len(labeled_data):,} logs")
print()

# Show severity distribution
print("📊 Severity Distribution:")
print("-" * 40)
total = len(labeled_data)
for severity in ['critical', 'high', 'medium', 'low']:
    count = severity_counter[severity]
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {severity:10} | {count:5,} logs | {pct:5.1f}%")
print("-" * 40)
print(f"  {'TOTAL':10} | {total:5,} logs | 100.0%")
print()

# Validate distribution
print("🔍 Validating severity distribution...")
low_pct = (severity_counter['low'] / total * 100)
medium_pct = (severity_counter['medium'] / total * 100)
high_pct = (severity_counter['high'] / total * 100)
critical_pct = (severity_counter['critical'] / total * 100)

issues = []
if low_pct < 40:
    issues.append(f"⚠️  LOW too rare ({low_pct:.1f}%) - expected 40-70%")
if critical_pct > 5:
    issues.append(f"⚠️  CRITICAL too common ({critical_pct:.1f}%) - expected <3%")
if high_pct > 20:
    issues.append(f"⚠️  HIGH too common ({high_pct:.1f}%) - expected 8-12%")

if issues:
    print("⚠️  Distribution concerns:")
    for issue in issues:
        print(f"   {issue}")
    print()
else:
    print("✅ Distribution looks healthy")
    print()

# Save to JSON file
output_file = 'severity_training_data.json'
print(f"💾 Saving training data to {output_file}...")
try:
    with open(output_file, 'w') as f:
        json.dump(labeled_data, f, indent=2, default=str)
    print(f"✅ Saved {len(labeled_data):,} labeled records")
    print()
except Exception as e:
    print(f"❌ Failed to save: {e}")
    cursor.close()
    conn.close()
    sys.exit(1)

# Show sample records
print("📋 Sample labeled records:")
print("-" * 70)
for i in range(min(5, len(labeled_data))):
    record = labeled_data[i]
    print(f"  {i+1}. [{record['severity'].upper():8}] {record['original_level']:5} | {record['message'][:50]}")
print("-" * 70)
print()

# Clean up
cursor.close()
conn.close()

# Summary
print("=" * 70)
print("✅ TRAINING DATA GENERATION COMPLETE")
print("=" * 70)
print()
print(f"📁 Output file: {output_file}")
print(f"📊 Total records: {len(labeled_data):,}")
print()
print("🎯 Severity Breakdown:")
for severity in ['critical', 'high', 'medium', 'low']:
    count = severity_counter[severity]
    pct = (count / total * 100) if total > 0 else 0
    print(f"   {severity.capitalize():8}: {count:5,} ({pct:5.1f}%)")
print()
print("🚀 Next step: Run train_models_severity.py to train the ML model")
print()

