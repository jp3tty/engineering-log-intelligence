"""
Populate Database with Sample Log Data
=======================================
Generates realistic log entries and inserts them into the database.
"""

import os
import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

# Load environment variables
load_dotenv('.env.local')

def generate_log_entries(count=10000):
    """Generate sample log entries"""
    
    print(f"Generating {count} log entries...")
    
    log_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
    level_weights = [0.20, 0.50, 0.15, 0.12, 0.03]  # Realistic distribution
    
    source_types = ['splunk', 'sap', 'application']
    source_weights = [0.4, 0.3, 0.3]
    
    hosts = ['web-server-01', 'web-server-02', 'app-server-01', 'app-server-02', 'db-server-01']
    services = ['webapp', 'api', 'database', 'cache', 'queue', 'auth', 'payment']
    categories = ['application', 'system', 'security', 'performance', 'business']
    
    messages = {
        'DEBUG': [
            'Debug trace for request processing',
            'Variable state: processing=true',
            'Cache lookup completed',
            'Function entry: processRequest()',
        ],
        'INFO': [
            'Request processed successfully',
            'User authentication successful',
            'Database query completed',
            'Cache hit for key',
            'Background job started',
            'File uploaded successfully',
        ],
        'WARN': [
            'High memory usage detected',
            'Slow query detected',
            'Rate limit approaching',
            'Cache miss - rebuilding',
            'Retry attempt initiated',
        ],
        'ERROR': [
            'Database connection failed',
            'API request timeout',
            'Failed to process payment',
            'File not found',
            'Invalid user input',
            'Authentication failed',
        ],
        'FATAL': [
            'Out of memory error',
            'Database server unreachable',
            'Critical system failure',
            'Data corruption detected',
        ]
    }
    
    logs = []
    base_time = datetime.now(timezone.utc) - timedelta(hours=24)
    
    for i in range(count):
        # Select log level with realistic distribution
        level = random.choices(log_levels, weights=level_weights)[0]
        source = random.choices(source_types, weights=source_weights)[0]
        
        # Generate timestamp (spread over last 24 hours)
        timestamp = base_time + timedelta(seconds=random.randint(0, 86400))
        
        # Select message based on level
        message = random.choice(messages[level])
        
        # Determine if this is an anomaly
        is_anomaly = level in ['ERROR', 'FATAL'] and random.random() < 0.3
        
        # Response time (ms)
        if level in ['ERROR', 'FATAL']:
            response_time = random.randint(500, 5000)
        elif level == 'WARN':
            response_time = random.randint(200, 1000)
        else:
            response_time = random.randint(20, 200)
        
        # HTTP status
        if level == 'ERROR':
            http_status = random.choice([400, 404, 500, 503])
        elif level == 'FATAL':
            http_status = random.choice([500, 503, 504])
        else:
            http_status = random.choice([200, 201, 204, 301, 302])
        
        log_entry = {
            'log_id': f'log-{i+1:06d}-{random.randint(1000, 9999)}',
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'source_type': source,
            'host': random.choice(hosts),
            'service': random.choice(services),
            'category': random.choice(categories),
            'is_anomaly': is_anomaly,
            'response_time_ms': response_time,
            'http_status': http_status,
        }
        
        logs.append(log_entry)
    
    print(f"✅ Generated {len(logs)} log entries")
    return logs

def insert_logs(conn, logs):
    """Insert logs into database using batch insert"""
    
    print(f"Inserting {len(logs)} logs into database...")
    
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO log_entries (
            log_id, timestamp, level, message, source_type, host, service, 
            category, is_anomaly, response_time_ms, http_status, 
            raw_log, structured_data, tags
        ) VALUES (
            %(log_id)s, %(timestamp)s, %(level)s, %(message)s, %(source_type)s, 
            %(host)s, %(service)s, %(category)s, %(is_anomaly)s, 
            %(response_time_ms)s, %(http_status)s, %(raw_log)s, 
            %(structured_data)s, %(tags)s
        )
    """
    
    # Prepare data for batch insert
    batch_data = []
    for log in logs:
        batch_data.append({
            **log,
            'raw_log': f"[{log['timestamp']}] {log['level']}: {log['message']}",
            'structured_data': '{}',
            'tags': '[]'
        })
    
    # Insert in batches of 1000
    batch_size = 1000
    for i in range(0, len(batch_data), batch_size):
        batch = batch_data[i:i + batch_size]
        execute_batch(cursor, insert_query, batch)
        conn.commit()
        print(f"  Inserted {min(i + batch_size, len(batch_data))}/{len(batch_data)} logs...")
    
    cursor.close()
    print(f"✅ All logs inserted successfully")

def populate_database(count=10000):
    """Main function to populate database"""
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    print("="*60)
    print("POPULATING DATABASE WITH LOG DATA")
    print("="*60)
    print()
    
    try:
        # Generate logs
        logs = generate_log_entries(count)
        
        # Connect to database
        print("\nConnecting to database...")
        conn = psycopg2.connect(database_url)
        print("✅ Connected successfully")
        print()
        
        # Insert logs
        insert_logs(conn, logs)
        
        # Verify insertion
        print("\nVerifying data...")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT level, COUNT(*) FROM log_entries GROUP BY level ORDER BY level")
        level_counts = cursor.fetchall()
        
        print(f"✅ Total logs in database: {total_count:,}")
        print("\nLog distribution:")
        for level, count in level_counts:
            percentage = (count / total_count) * 100
            print(f"  {level:6s}: {count:6,} ({percentage:5.1f}%)")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("✅ DATABASE POPULATED SUCCESSFULLY!")
        print("="*60)
        print()
        print("Next step: Redeploy your Vercel app to see real data")
        print("Run: vercel --prod")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    populate_database(count)

