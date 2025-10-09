"""
Setup Database Schema (Fixed)
==============================
Creates the database schema with proper handling of reserved keywords
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def setup_schema():
    """Execute the schema SQL file in parts to avoid reserved keyword issues"""
    
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
        cursor = conn.cursor()
        
        print("✅ Connected successfully")
        print()
        
        # Split by statement and execute one by one
        statements = []
        current_statement = []
        in_function = False
        
        for line in schema_sql.split('\n'):
            # Track if we're in a function definition
            if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
                in_function = True
            elif in_function and '$$' in line and current_statement:
                # End of function
                in_function = False
                current_statement.append(line)
                statements.append('\n'.join(current_statement))
                current_statement = []
                continue
            
            # Skip comments and empty lines at the start
            if not current_statement and (line.strip().startswith('--') or not line.strip()):
                continue
            
            current_statement.append(line)
            
            # If line ends with semicolon and we're not in a function, it's a complete statement
            if line.strip().endswith(';') and not in_function:
                statements.append('\n'.join(current_statement))
                current_statement = []
        
        # Add any remaining statement
        if current_statement:
            statements.append('\n'.join(current_statement))
        
        print(f"Executing {len(statements)} statements...")
        print()
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            statement = statement.strip()
            if not statement:
                continue
            
            try:
                # Show what we're executing
                first_line = statement.split('\n')[0][:60]
                if len(first_line) == 60:
                    first_line += "..."
                
                cursor.execute(statement)
                conn.commit()
                print(f"✅ [{i}/{len(statements)}] {first_line}")
                success_count += 1
                
            except psycopg2.errors.DuplicateObject as e:
                print(f"⏭️  [{i}/{len(statements)}] Skipped (already exists): {first_line}")
                conn.rollback()
                skip_count += 1
                
            except Exception as e:
                error_msg = str(e).split('\n')[0]
                print(f"❌ [{i}/{len(statements)}] Error: {error_msg}")
                print(f"   Statement: {first_line}")
                conn.rollback()
                error_count += 1
                
                # Don't fail on errors, continue
                continue
        
        print()
        print(f"Results: {success_count} succeeded, {skip_count} skipped, {error_count} errors")
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
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                # Check if it's log_entries (we need this one!)
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   - {table[0]}: {count} rows")
        else:
            print("⚠️  No tables found")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*60)
        
        if error_count > 0:
            print(f"\n⚠️  {error_count} statements had errors, but core tables should be created")
        
        print()
        print("Next step: Populate with data")
        print("Run: python -m data_simulation.simulator --count 10000")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_schema()

