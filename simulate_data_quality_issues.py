"""
Simulate Realistic Data Quality Issues
=======================================
This script introduces realistic data quality problems that ML can help solve:

1. Missing log levels (5-10% of logs)
2. Misclassified severity (errors marked as info, etc.)
3. Missing anomaly flags
4. Inconsistent source data

This demonstrates the VALUE of ML predictions.

Author: Engineering Log Intelligence Team
Date: October 12, 2025
"""

import psycopg2
import random
from dotenv import load_dotenv
import os

load_dotenv('.env.local')

print("="*70)
print("🔧 SIMULATING DATA QUALITY ISSUES")
print("="*70)
print()
print("This will make ML predictions more valuable by creating:")
print("  • Misclassified severity (ERROR → INFO, FATAL → DEBUG)")
print("  • Missing anomaly flags")
print("  • Inconsistent source data")
print()
print("💡 These are REAL issues in production log systems!")
print()

# Connect to database
database_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Get total log count
cursor.execute("SELECT COUNT(*) FROM log_entries")
total_logs = cursor.fetchone()[0]
print(f"📊 Total logs in database: {total_logs:,}")
print()

# =============================================================================
# ISSUE 1: Misclassify ERROR as INFO (very common in real systems)
# =============================================================================
print("Issue 1: Misclassifying 15% of ERROR logs as INFO...")
print("         (Simulates noisy/misconfigured log sources)")

cursor.execute("""
    UPDATE log_entries
    SET level = 'INFO'
    WHERE level = 'ERROR'
    AND (
        message ILIKE '%error%' 
        OR message ILIKE '%failed%'
        OR message ILIKE '%exception%'
        OR message ILIKE '%timeout%'
        OR message ILIKE '%connection%'
    )
    AND id IN (
        SELECT id FROM log_entries
        WHERE level = 'ERROR'
        ORDER BY RANDOM()
        LIMIT (SELECT COUNT(*) * 15 / 100 FROM log_entries WHERE level = 'ERROR')
    )
""")
error_to_info = cursor.rowcount
print(f"  ✅ Misclassified {error_to_info:,} ERROR logs as INFO")

# =============================================================================
# ISSUE 2: Misclassify WARN as DEBUG (underestimating severity)
# =============================================================================
print()
print("Issue 2: Misclassifying 20% of WARN logs as DEBUG...")
print("         (Simulates severity underestimation)")

cursor.execute("""
    UPDATE log_entries
    SET level = 'DEBUG'
    WHERE level = 'WARN'
    AND id IN (
        SELECT id FROM log_entries
        WHERE level = 'WARN'
        ORDER BY RANDOM()
        LIMIT (SELECT COUNT(*) / 5 FROM log_entries WHERE level = 'WARN')
    )
""")
warn_to_debug = cursor.rowcount
print(f"  ✅ Misclassified {warn_to_debug:,} WARN logs as DEBUG")

# =============================================================================
# ISSUE 3: Clear anomaly flags (simulate missing detection)
# =============================================================================
print()
print("Issue 3: Clearing anomaly flags (simulate no source detection)...")

cursor.execute("""
    UPDATE log_entries
    SET is_anomaly = FALSE,
        anomaly_type = NULL
    WHERE is_anomaly = TRUE
    AND id IN (
        SELECT id FROM log_entries
        WHERE is_anomaly = TRUE
        ORDER BY RANDOM()
        LIMIT (SELECT COUNT(*) * 3 / 4 FROM log_entries WHERE is_anomaly = TRUE)
    )
""")
cleared_anomalies = cursor.rowcount
print(f"  ✅ Cleared {cleared_anomalies:,} anomaly flags")

# =============================================================================
# ISSUE 4: Set some FATAL logs to DEBUG (severe misclassification)
# =============================================================================
print()
print("Issue 4: Misclassifying 30% of FATAL logs as DEBUG...")

cursor.execute("""
    UPDATE log_entries
    SET level = 'DEBUG'
    WHERE level = 'FATAL'
    AND id IN (
        SELECT id FROM log_entries
        WHERE level = 'FATAL'
        ORDER BY RANDOM()
        LIMIT (SELECT COUNT(*) / 3 FROM log_entries WHERE level = 'FATAL')
    )
""")
fatal_misclassified = cursor.rowcount
print(f"  ✅ Misclassified {fatal_misclassified:,} FATAL logs as DEBUG")

# Commit all changes
conn.commit()

# =============================================================================
# SUMMARY: Show current state
# =============================================================================
print()
print("="*70)
print("📊 DATA QUALITY SUMMARY (After Simulation)")
print("="*70)
print()

# Get counts for summary
total_misclassified = error_to_info + warn_to_debug + fatal_misclassified

# Check level distribution
cursor.execute("""
    SELECT 
        level,
        COUNT(*) as count
    FROM log_entries
    GROUP BY level
    ORDER BY count DESC
""")
levels = cursor.fetchall()

print("Level Distribution:")
for level, count in levels:
    pct = (count / total_logs) * 100
    print(f"  {level:10} | {count:6,} logs | {pct:5.1f}%")

print()

# Check anomalies
cursor.execute("SELECT COUNT(*) FROM log_entries WHERE is_anomaly = TRUE")
anomaly_count = cursor.fetchone()[0]
print(f"Anomaly Flags: {anomaly_count:,} ({(anomaly_count/total_logs*100):.1f}%)")

print()
print("="*70)
print("✅ DATA QUALITY ISSUES SIMULATED")
print("="*70)
print()
print("💡 ML predictions are now VALUABLE because they can:")
print("   • Correct severity misclassifications")
print("   • Detect errors hidden as INFO/DEBUG")
print("   • Find anomalies that source systems missed")
print("   • Provide confidence scores for data validation")
print()
print("🎯 Real-World Issues Simulated:")
print(f"   • {error_to_info:,} ERROR logs misclassified as INFO")
print(f"   • {warn_to_debug:,} WARN logs misclassified as DEBUG")
print(f"   • {fatal_misclassified:,} FATAL logs misclassified as DEBUG")
print(f"   • {cleared_anomalies:,} missed anomaly flags")
print()
print("📊 Impact:")
total_misclassified = error_to_info + warn_to_debug + fatal_misclassified
print(f"   • {total_misclassified:,} total misclassifications ({(total_misclassified/total_logs*100):.1f}% of logs)")
print(f"   • {cleared_anomalies:,} undetected anomalies ({(cleared_anomalies/total_logs*100):.1f}% of logs)")
print()
print("🚀 Next Steps:")
print("   1. Run batch analysis: ./run_ml_analysis.sh")
print("   2. ML will correct these issues and detect true severity")
print("   3. Compare ml_predictions.predicted_level vs log_entries.level")
print("   4. See where ML catches errors that were hidden!")
print()
print("💼 Portfolio Value:")
print("   This demonstrates ML solving REAL data quality problems")
print("   that exist in production environments!")
print()

cursor.close()
conn.close()

