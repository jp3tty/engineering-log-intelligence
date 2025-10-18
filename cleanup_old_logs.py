"""
Emergency Database Cleanup Script
==================================
Deletes old logs to free up Railway database space.

USAGE:
  python3 cleanup_old_logs.py --days 7   # Keep last 7 days
  python3 cleanup_old_logs.py --days 14  # Keep last 14 days
  python3 cleanup_old_logs.py --dry-run  # Preview without deleting

Author: Engineering Log Intelligence Team
Date: October 18, 2025
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv()


def cleanup_old_logs(retention_days=7, dry_run=False):
    """
    Delete logs older than retention_days
    
    Args:
        retention_days: Number of days to keep (default: 7)
        dry_run: If True, only show what would be deleted
    """
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("🧹 DATABASE CLEANUP SCRIPT")
        print("=" * 70)
        print(f"Retention Policy: Keep last {retention_days} days")
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE DELETION'}")
        print()
        
        # Get current stats
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        total_logs_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_database_size(current_database())")
        db_size_before = cursor.fetchone()[0] / (1024 * 1024)  # MB
        
        # Count logs to delete
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM log_entries 
            WHERE timestamp < NOW() - INTERVAL '{retention_days} days'
        """)
        logs_to_delete = cursor.fetchone()[0]
        logs_to_keep = total_logs_before - logs_to_delete
        
        print(f"📊 Current Status:")
        print(f"   Total Logs: {total_logs_before:,}")
        print(f"   Database Size: {db_size_before:.2f} MB")
        print()
        print(f"🗑️  Cleanup Plan:")
        print(f"   Logs to Delete: {logs_to_delete:,} (older than {retention_days} days)")
        print(f"   Logs to Keep: {logs_to_keep:,}")
        print(f"   Estimated Space Saved: ~{(logs_to_delete / total_logs_before) * db_size_before:.2f} MB")
        print()
        
        if dry_run:
            print("✅ DRY RUN COMPLETE - No changes made")
            cursor.close()
            conn.close()
            return True
        
        # Confirm deletion
        print("⚠️  WARNING: This will permanently delete logs!")
        response = input(f"Type 'DELETE' to proceed with deleting {logs_to_delete:,} logs: ")
        
        if response != 'DELETE':
            print("❌ Cancelled - No changes made")
            cursor.close()
            conn.close()
            return False
        
        print()
        
        # IMPORTANT: Delete ML predictions FIRST to avoid foreign key constraint violation
        print("🗑️  Step 1: Deleting ML predictions for old logs...")
        cursor.execute(f"""
            DELETE FROM ml_predictions 
            WHERE log_entry_id IN (
                SELECT id FROM log_entries 
                WHERE timestamp < NOW() - INTERVAL '{retention_days} days'
            )
        """)
        deleted_predictions = cursor.rowcount
        print(f"   ✅ Deleted {deleted_predictions:,} ML predictions")
        
        # Step 2: Delete old log entries
        print("🗑️  Step 2: Deleting old logs...")
        cursor.execute(f"""
            DELETE FROM log_entries 
            WHERE timestamp < NOW() - INTERVAL '{retention_days} days'
        """)
        deleted_logs = cursor.rowcount
        print(f"   ✅ Deleted {deleted_logs:,} logs")
        
        conn.commit()
        
        print()
        
        # VACUUM to reclaim space
        print("🔄 Step 3: Running VACUUM to reclaim disk space...")
        print("   (This may take 2-3 minutes...)")
        
        # Close the transaction before VACUUM
        conn.set_isolation_level(0)
        cursor.execute("VACUUM FULL log_entries")
        print("   ✅ Vacuumed log_entries")
        cursor.execute("VACUUM FULL ml_predictions")
        print("   ✅ Vacuumed ml_predictions")
        conn.set_isolation_level(1)
        print()
        
        # Get new stats
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        total_logs_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT pg_database_size(current_database())")
        db_size_after = cursor.fetchone()[0] / (1024 * 1024)  # MB
        
        space_saved = db_size_before - db_size_after
        
        print("=" * 70)
        print("✅ CLEANUP COMPLETE")
        print("=" * 70)
        print(f"Before:  {total_logs_before:,} logs | {db_size_before:.2f} MB")
        print(f"After:   {total_logs_after:,} logs | {db_size_after:.2f} MB")
        print(f"Removed: {deleted_logs:,} logs + {deleted_predictions:,} predictions")
        print(f"Saved:   {space_saved:.2f} MB")
        print(f"New Usage: ~{(db_size_after / 166) * 100:.1f}% of Railway limit")
        print()
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    # Parse arguments
    dry_run = '--dry-run' in sys.argv
    retention_days = 7  # Default
    
    for i, arg in enumerate(sys.argv):
        if arg == '--days' and i + 1 < len(sys.argv):
            try:
                retention_days = int(sys.argv[i + 1])
            except ValueError:
                print("❌ Invalid --days value. Using default: 7")
    
    # Run cleanup
    success = cleanup_old_logs(retention_days=retention_days, dry_run=dry_run)
    sys.exit(0 if success else 1)

