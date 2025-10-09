"""
Fix Railway Database Connection
================================
This script tests the connection and creates the database if it doesn't exist.
"""

import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv('.env.local')

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("Installing psycopg2...")
    os.system("pip install psycopg2-binary")
    import psycopg2
    from psycopg2 import sql

def fix_database():
    """Test connection and create database if needed"""
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    print("="*60)
    print("RAILWAY DATABASE CONNECTION FIX")
    print("="*60)
    print()
    
    # Parse the connection string
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
    
    if not match:
        print("❌ Invalid DATABASE_URL format")
        return False
    
    user, password, host, port, dbname = match.groups()
    
    print(f"Connection Details:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  User: {user}")
    print(f"  Database: {dbname}")
    print()
    
    # First, try to connect to the default 'postgres' database
    print("Step 1: Connecting to default 'postgres' database...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to postgres database")
        
        # Check if our target database exists
        print(f"\nStep 2: Checking if '{dbname}' database exists...")
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = %s
        """, (dbname,))
        
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{dbname}' exists!")
            cursor.close()
            conn.close()
            
            # Now try to connect to the actual database
            print(f"\nStep 3: Testing connection to '{dbname}'...")
            try:
                test_conn = psycopg2.connect(database_url)
                test_cursor = test_conn.cursor()
                
                # Check if logs table exists
                test_cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'logs'
                    )
                """)
                table_exists = test_cursor.fetchone()[0]
                
                if table_exists:
                    print(f"✅ 'logs' table exists")
                    
                    # Check row count
                    test_cursor.execute("SELECT COUNT(*) FROM logs")
                    count = test_cursor.fetchone()[0]
                    print(f"📊 Database has {count:,} log entries")
                    
                    if count == 0:
                        print("\n⚠️  Database is empty - needs to be populated")
                        print("   Run: python -m data_simulation.simulator --count 10000")
                else:
                    print(f"⚠️  'logs' table doesn't exist")
                    print("   Run: psql $DATABASE_URL < external-services/postgresql/schema.sql")
                
                test_cursor.close()
                test_conn.close()
                
                print("\n" + "="*60)
                print("✅ CONNECTION SUCCESSFUL - Database is accessible!")
                print("="*60)
                return True
                
            except Exception as e:
                print(f"❌ Failed to connect to '{dbname}': {e}")
                return False
        else:
            print(f"⚠️  Database '{dbname}' does NOT exist")
            print(f"\nStep 3: Creating database '{dbname}'...")
            try:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(dbname)
                ))
                print(f"✅ Database '{dbname}' created successfully!")
                
                cursor.close()
                conn.close()
                
                print("\nNext steps:")
                print("1. Initialize schema: psql $DATABASE_URL < external-services/postgresql/schema.sql")
                print("2. Populate data: python -m data_simulation.simulator --count 10000")
                
                print("\n" + "="*60)
                print("✅ DATABASE CREATED - Ready for schema setup")
                print("="*60)
                return True
                
            except Exception as e:
                print(f"❌ Failed to create database: {e}")
                cursor.close()
                conn.close()
                return False
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("1. Railway service is sleeping/inactive - check dashboard")
        print("2. Firewall blocking connection")
        print("3. Credentials expired or changed")
        print("\nTo fix:")
        print("1. Go to https://railway.app/dashboard")
        print("2. Find your PostgreSQL service")
        print("3. Check if it's 'Active' (restart if needed)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = fix_database()
    sys.exit(0 if success else 1)


