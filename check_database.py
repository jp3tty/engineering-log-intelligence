"""
Check Database Connection and Data
===================================
This script checks if the PostgreSQL database is accessible and has data.
"""

import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv('.env.local')

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    os.system("pip install psycopg2-binary")
    import psycopg2
    from psycopg2.extras import RealDictCursor

def check_database():
    """Check database connection and data"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("\nTo set it, run:")
        print("cd engineering_log_intelligence && vercel env pull")
        return False
    
    print(f"✅ DATABASE_URL found")
    print(f"   Connecting to: {database_url[:30]}...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Database connection successful!")
        
        # Check if log_entries table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'log_entries'
            )
        """)
        table_exists = cursor.fetchone()['exists']
        
        if not table_exists:
            print("❌ 'log_entries' table does not exist")
            print("\nTo create the table, run:")
            print("psql $DATABASE_URL < external-services/postgresql/schema.sql")
            print("\nOr run the setup script:")
            print("python setup_schema.py")
            return False
        
        print("✅ 'log_entries' table exists")
        
        # Check row count
        cursor.execute("SELECT COUNT(*) as count FROM log_entries")
        total_logs = cursor.fetchone()['count']
        
        print(f"📊 Total logs in database: {total_logs:,}")
        
        if total_logs == 0:
            print("⚠️  Database is empty - no log data found")
            print("\nTo populate with sample data, run:")
            print("python -m data_simulation.simulator --count 10000")
            return False
        
        # Get log distribution
        cursor.execute("""
            SELECT level, COUNT(*) as count 
            FROM log_entries 
            GROUP BY level 
            ORDER BY count DESC
        """)
        distribution = cursor.fetchall()
        
        print("\n📈 Log Level Distribution:")
        for row in distribution:
            print(f"   {row['level']:<10} {row['count']:>10,} logs")
        
        # Get recent logs
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM log_entries 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)
        recent_logs = cursor.fetchone()['count']
        
        print(f"\n⏰ Logs in last 24 hours: {recent_logs:,}")
        
        if recent_logs == 0:
            print("⚠️  No recent data - all logs are older than 24 hours")
            print("   The dashboard queries only show data from the last 24 hours")
        
        # Get date range
        cursor.execute("""
            SELECT 
                MIN(timestamp) as oldest,
                MAX(timestamp) as newest
            FROM log_entries
        """)
        date_range = cursor.fetchone()
        
        if date_range['oldest']:
            print(f"\n📅 Date Range:")
            print(f"   Oldest log: {date_range['oldest']}")
            print(f"   Newest log: {date_range['newest']}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        if recent_logs > 0:
            print("✅ DATABASE IS READY - Dashboard should show real data!")
        else:
            print("⚠️  DATABASE HAS DATA BUT IT'S OLD - Dashboard will use simulated data")
        print("="*60)
        
        return recent_logs > 0
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPossible issues:")
        print("1. Database server is not running")
        print("2. Incorrect connection credentials")
        print("3. Network/firewall blocking connection")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("DATABASE CONNECTION CHECK")
    print("="*60)
    print()
    
    success = check_database()
    
    sys.exit(0 if success else 1)

