"""
Automated Log Retention Script
==============================
Automatically deletes logs older than retention period and reclaims space.
Designed to run daily via GitHub Actions.

Author: Engineering Log Intelligence Team
Date: October 18, 2025
"""

import os
import sys
import psycopg2
from datetime import datetime

# Default retention: 7 days
RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', '7'))


def auto_cleanup():
    """Automatically cleanup old logs"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        print(f"🧹 Starting automated log cleanup (retention: {RETENTION_DAYS} days)")
        print(f"⏰ Time: {datetime.now().isoformat()}")
        print()
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        total_logs_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_database_size(current_database())")
        db_size_before = cursor.fetchone()[0] / (1024 * 1024)
        
        # Delete ML predictions first (avoid foreign key constraint)
        cursor.execute(f"""
            DELETE FROM ml_predictions 
            WHERE log_entry_id IN (
                SELECT id FROM log_entries 
                WHERE timestamp < NOW() - INTERVAL '{RETENTION_DAYS} days'
            )
        """)
        deleted_predictions = cursor.rowcount
        
        # Then delete old logs
        cursor.execute(f"""
            DELETE FROM log_entries 
            WHERE timestamp < NOW() - INTERVAL '{RETENTION_DAYS} days'
        """)
        deleted_logs = cursor.rowcount
        
        conn.commit()
        
        # VACUUM to reclaim space (lightweight version)
        conn.set_isolation_level(0)
        cursor.execute("VACUUM ANALYZE log_entries")
        cursor.execute("VACUUM ANALYZE ml_predictions")
        conn.set_isolation_level(1)
        
        # Get new stats
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        total_logs_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_database_size(current_database())")
        db_size_after = cursor.fetchone()[0] / (1024 * 1024)
        
        space_saved = db_size_before - db_size_after
        
        print(f"✅ Cleanup complete:")
        print(f"   Deleted: {deleted_logs:,} logs + {deleted_predictions:,} predictions")
        print(f"   Space saved: {space_saved:.2f} MB")
        print(f"   DB size: {db_size_before:.2f} MB → {db_size_after:.2f} MB")
        print(f"   Remaining logs: {total_logs_after:,}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during auto-cleanup: {e}")
        return False


if __name__ == '__main__':
    success = auto_cleanup()
    sys.exit(0 if success else 1)

