"""
Populate Database with Advanced Simulation Data
================================================
Uses the sophisticated data_simulation module to generate realistic
SPLUNK, SAP, and Application logs with complex anomaly patterns.
"""

import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

# Import the advanced simulation system
from data_simulation.simulator import DataSimulator, create_default_config

# Load environment variables
load_dotenv('.env.local')
load_dotenv()


def convert_to_db_format(log_entry):
    """Convert simulator log format to database schema format."""
    # Extract basic fields
    log_id = log_entry.get('log_id', '')
    timestamp = log_entry.get('timestamp', datetime.now(timezone.utc))
    level = log_entry.get('level', 'INFO')
    message = log_entry.get('message', '')
    source_type = log_entry.get('source_type', 'application')
    host = log_entry.get('host', 'unknown')
    service = log_entry.get('service', 'unknown')
    category = log_entry.get('category', 'application')
    
    # Determine if anomaly
    is_anomaly = log_entry.get('is_anomaly', False)
    
    # Extract or generate response time
    response_time_ms = log_entry.get('response_time_ms', 100)
    if 'performance_metrics' in log_entry:
        response_time_ms = log_entry['performance_metrics'].get('response_time_ms', response_time_ms)
    
    # Extract or generate HTTP status
    http_status = log_entry.get('http_status', 200)
    if level in ['ERROR', 'FATAL'] and http_status == 200:
        http_status = 500
    
    # Build raw log string
    raw_log = log_entry.get('raw_log', f"[{timestamp}] {level}: {message}")
    
    # Build structured data (JSON string)
    structured_data = '{}'
    if 'metadata' in log_entry:
        import json
        structured_data = json.dumps(log_entry['metadata'])
    elif 'transaction_data' in log_entry:
        import json
        structured_data = json.dumps(log_entry['transaction_data'])
    elif 'error_details' in log_entry:
        import json
        structured_data = json.dumps(log_entry['error_details'])
    
    # Build tags
    tags = log_entry.get('tags', [])
    import json
    tags_str = json.dumps(tags) if tags else '[]'
    
    return {
        'log_id': log_id,
        'timestamp': timestamp,
        'level': level,
        'message': message,
        'source_type': source_type,
        'host': host,
        'service': service,
        'category': category,
        'is_anomaly': is_anomaly,
        'response_time_ms': int(response_time_ms),
        'http_status': http_status,
        'raw_log': raw_log,
        'structured_data': structured_data,
        'tags': tags_str
    }


def insert_logs(conn, logs):
    """Insert logs into database using batch insert."""
    print(f"\n📥 Inserting {len(logs)} logs into database...")
    
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
    
    # Convert all logs to database format
    batch_data = [convert_to_db_format(log) for log in logs]
    
    # Insert in batches of 1000
    batch_size = 1000
    for i in range(0, len(batch_data), batch_size):
        batch = batch_data[i:i + batch_size]
        execute_batch(cursor, insert_query, batch)
        conn.commit()
        print(f"  ✅ Inserted {min(i + batch_size, len(batch_data))}/{len(batch_data)} logs...")
    
    cursor.close()
    print(f"✅ All logs inserted successfully")


def analyze_generated_data(logs):
    """Analyze and display statistics about generated logs."""
    from collections import Counter
    
    total = len(logs)
    levels = Counter(log.get('level', 'UNKNOWN') for log in logs)
    sources = Counter(log.get('source_type', 'unknown') for log in logs)
    anomalies = sum(1 for log in logs if log.get('is_anomaly', False))
    
    print("\n📊 Generated Data Statistics:")
    print("=" * 60)
    print(f"Total Logs: {total:,}")
    print(f"\n📈 By Log Level:")
    for level in ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']:
        count = levels.get(level, 0)
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {level:6s}: {count:6,} ({pct:5.1f}%)")
    
    print(f"\n📂 By Source Type:")
    for source, count in sources.most_common():
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {source:15s}: {count:6,} ({pct:5.1f}%)")
    
    print(f"\n⚠️  Anomalies:")
    pct = (anomalies / total * 100) if total > 0 else 0
    print(f"  Total: {anomalies:,} ({pct:5.1f}%)")
    print("=" * 60)


def populate_database_advanced(count=10000):
    """Main function to populate database using advanced simulation."""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        print("Please set DATABASE_URL environment variable or add it to .env.local")
        return False
    
    print("=" * 60)
    print("🚀 ADVANCED DATA SIMULATION - DATABASE POPULATION")
    print("=" * 60)
    print()
    print("Using sophisticated multi-source log generation:")
    print("  • SPLUNK logs (infrastructure & systems)")
    print("  • SAP logs (enterprise transactions)")
    print("  • Application logs (API & services)")
    print()
    
    try:
        # Create simulator with default configuration
        print("🔧 Initializing advanced data simulator...")
        config = create_default_config()
        simulator = DataSimulator(config)
        print("✅ Simulator initialized with 3 generators")
        
        # Generate sample data
        print(f"\n🎲 Generating {count:,} realistic log entries...")
        logs = simulator.generate_sample_data(count=count)
        print(f"✅ Generated {len(logs):,} log entries")
        
        # Show statistics about generated data
        analyze_generated_data(logs)
        
        # Connect to database
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(database_url, sslmode='require')
        print("✅ Connected successfully")
        
        # Insert logs
        insert_logs(conn, logs)
        
        # Verify insertion
        print("\n🔍 Verifying data in database...")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT level, COUNT(*) FROM log_entries GROUP BY level ORDER BY level")
        level_counts = cursor.fetchall()
        
        cursor.execute("SELECT source_type, COUNT(*) FROM log_entries GROUP BY source_type ORDER BY source_type")
        source_counts = cursor.fetchall()
        
        print(f"✅ Total logs in database: {total_count:,}")
        print("\n📊 Database Log Distribution:")
        for level, count in level_counts:
            percentage = (count / total_count) * 100
            print(f"  {level:6s}: {count:6,} ({percentage:5.1f}%)")
        
        print("\n📂 Database Source Distribution:")
        for source, count in source_counts:
            percentage = (count / total_count) * 100
            print(f"  {source:15s}: {count:6,} ({percentage:5.1f}%)")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ ADVANCED DATA POPULATION COMPLETE!")
        print("=" * 60)
        print()
        print("🎯 Your database now contains sophisticated, multi-source logs")
        print("   with realistic anomaly patterns from:")
        print("   - SPLUNK (system failures, security breaches)")
        print("   - SAP (transaction errors, business rule violations)")
        print("   - Application (performance issues, API errors)")
        print()
        print("📊 Next step: Run ML analysis to detect anomalies")
        print("   ./run_ml_analysis.sh")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    
    print(f"\n🎯 Target: {count:,} log entries")
    
    success = populate_database_advanced(count)
    sys.exit(0 if success else 1)

