"""
Setup Database Schema
=====================
Creates the database schema from schema.sql
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def setup_schema():
    """Execute the schema SQL file"""
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    print("="*60)
    print("SETTING UP DATABASE SCHEMA")
    print("="*60)
    print()
    
    try:
        # Read the schema file
        schema_path = 'external-services/postgresql/schema.sql'
        print(f"Reading schema from: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print(f"✅ Schema file loaded ({len(schema_sql)} characters)")
        print()
        
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected successfully")
        print()
        
        # Execute schema
        print("Executing schema SQL...")
        cursor.execute(schema_sql)
        
        print("✅ Schema created successfully!")
        print()
        
        # Verify tables were created
        print("Verifying tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Created {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  No tables found")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*60)
        print()
        print("Next step: Populate with data")
        print("Run: python -m data_simulation.simulator --count 10000")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Schema file not found: {schema_path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_schema()

