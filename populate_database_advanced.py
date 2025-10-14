"""
Populate Database with Advanced Simulation Data
================================================
Uses the sophisticated data_simulation module to generate realistic
SPLUNK, SAP, and Application logs with complex anomaly patterns.

ENHANCED: Now extracts and maps all source-specific fields from metadata:
  • SAP fields: transaction_code, sap_system, department, amount, currency, document_number
  • Application fields: application_type, framework, http_method, endpoint, response_time_ms
  • SPLUNK fields: splunk_source, splunk_host
  • Correlation fields: request_id, session_id, correlation_id, ip_address
  • Anomaly fields: anomaly_type, error_details, performance_metrics, business_context

This ensures all specialized columns in the database schema are properly populated.
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
    import json
    
    # Extract basic fields
    log_id = log_entry.get('log_id', '')
    timestamp = log_entry.get('timestamp', datetime.now(timezone.utc))
    level = log_entry.get('level', 'INFO')
    message = log_entry.get('message', '')
    
    # Get metadata for field extraction
    metadata = log_entry.get('metadata', {})
    
    # Extract source_type from either top-level or metadata.generator
    source_type = log_entry.get('source_type') or metadata.get('generator', 'application')
    
    host = log_entry.get('host') or metadata.get('host', 'unknown')
    service = log_entry.get('service') or metadata.get('service', 'unknown')
    category = log_entry.get('category', 'application')
    
    # Determine if anomaly
    is_anomaly = log_entry.get('is_anomaly', False)
    anomaly_type = log_entry.get('anomaly_type', None)
    
    # Extract correlation fields
    request_id = log_entry.get('request_id', metadata.get('request_id', None))
    session_id = log_entry.get('session_id', metadata.get('session_id', None))
    correlation_id = log_entry.get('correlation_id', metadata.get('correlation_id', None))
    ip_address = log_entry.get('ip_address', metadata.get('ip_address', None))
    
    # Extract Application-specific fields
    application_type = metadata.get('application_type', None)
    framework = metadata.get('framework', None)
    http_method = log_entry.get('http_method', metadata.get('http_method', None))
    http_status = log_entry.get('http_status', metadata.get('http_status', 200))
    endpoint = log_entry.get('endpoint', metadata.get('endpoint', None))
    response_time_ms = log_entry.get('response_time_ms', metadata.get('response_time_ms', None))
    
    # Override with performance_metrics if available
    if 'performance_metrics' in log_entry:
        response_time_ms = log_entry['performance_metrics'].get('response_time_ms', response_time_ms)
    
    # Adjust HTTP status for errors
    if level in ['ERROR', 'FATAL'] and http_status == 200:
        http_status = 500
    
    # Extract SAP-specific fields
    transaction_code = metadata.get('transaction_code', None)
    sap_system = metadata.get('sap_system', None)
    department = metadata.get('department', None)
    amount = metadata.get('amount', None)
    currency = metadata.get('currency', None)
    document_number = metadata.get('document_number', None)
    
    # Extract SPLUNK-specific fields
    splunk_source = metadata.get('splunk_source', None)
    splunk_host = metadata.get('splunk_host', None)
    
    # Build raw log string
    raw_log = log_entry.get('raw_log', f"[{timestamp}] {level}: {message}")
    
    # Build structured data (JSON string) - store original metadata
    structured_data = '{}'
    if metadata:
        structured_data = json.dumps(metadata)
    elif 'transaction_data' in log_entry:
        structured_data = json.dumps(log_entry['transaction_data'])
    elif 'error_details' in log_entry:
        structured_data = json.dumps(log_entry['error_details'])
    
    # Build error_details, performance_metrics, business_context JSON fields
    error_details = json.dumps(log_entry.get('error_details', {}))
    performance_metrics = json.dumps(log_entry.get('performance_metrics', {}))
    business_context = json.dumps(log_entry.get('business_context', {}))
    
    # Build tags
    tags = log_entry.get('tags', [])
    tags_str = json.dumps(tags) if tags else '[]'
    
    return {
        # Basic fields
        'log_id': log_id,
        'timestamp': timestamp,
        'level': level,
        'message': message,
        'source_type': source_type,
        'host': host,
        'service': service,
        'category': category,
        'raw_log': raw_log,
        'structured_data': structured_data,
        'tags': tags_str,
        
        # Correlation fields
        'request_id': request_id,
        'session_id': session_id,
        'correlation_id': correlation_id,
        'ip_address': ip_address,
        
        # Application-specific fields
        'application_type': application_type,
        'framework': framework,
        'http_method': http_method,
        'http_status': http_status,
        'endpoint': endpoint,
        'response_time_ms': int(response_time_ms) if response_time_ms else None,
        
        # SAP-specific fields
        'transaction_code': transaction_code,
        'sap_system': sap_system,
        'department': department,
        'amount': float(amount) if amount else None,
        'currency': currency,
        'document_number': document_number,
        
        # SPLUNK-specific fields
        'splunk_source': splunk_source,
        'splunk_host': splunk_host,
        
        # Anomaly and error information
        'is_anomaly': is_anomaly,
        'anomaly_type': anomaly_type,
        'error_details': error_details,
        'performance_metrics': performance_metrics,
        'business_context': business_context
    }


def insert_logs(conn, logs):
    """Insert logs into database using batch insert."""
    print(f"\n📥 Inserting {len(logs)} logs into database...")
    
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO log_entries (
            log_id, timestamp, level, message, source_type, host, service, 
            category, raw_log, structured_data, tags,
            request_id, session_id, correlation_id, ip_address,
            application_type, framework, http_method, http_status, endpoint, response_time_ms,
            transaction_code, sap_system, department, amount, currency, document_number,
            splunk_source, splunk_host,
            is_anomaly, anomaly_type, error_details, performance_metrics, business_context
        ) VALUES (
            %(log_id)s, %(timestamp)s, %(level)s, %(message)s, %(source_type)s, 
            %(host)s, %(service)s, %(category)s, %(raw_log)s, 
            %(structured_data)s, %(tags)s,
            %(request_id)s, %(session_id)s, %(correlation_id)s, %(ip_address)s,
            %(application_type)s, %(framework)s, %(http_method)s, %(http_status)s, 
            %(endpoint)s, %(response_time_ms)s,
            %(transaction_code)s, %(sap_system)s, %(department)s, %(amount)s, 
            %(currency)s, %(document_number)s,
            %(splunk_source)s, %(splunk_host)s,
            %(is_anomaly)s, %(anomaly_type)s, %(error_details)s, 
            %(performance_metrics)s, %(business_context)s
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
    # Get source from metadata.generator or top-level source_type
    sources = Counter(log.get('source_type') or log.get('metadata', {}).get('generator', 'unknown') for log in logs)
    anomalies = sum(1 for log in logs if log.get('is_anomaly', False))
    
    # Count source-specific fields
    sap_with_tcodes = sum(1 for log in logs 
                          if (log.get('source_type') == 'sap' or log.get('metadata', {}).get('generator') == 'sap')
                          and log.get('metadata', {}).get('transaction_code'))
    app_with_endpoints = sum(1 for log in logs 
                             if (log.get('source_type') == 'application' or log.get('metadata', {}).get('generator') == 'application')
                             and log.get('metadata', {}).get('endpoint'))
    logs_with_correlations = sum(1 for log in logs 
                                  if log.get('request_id') or 
                                  log.get('metadata', {}).get('request_id'))
    
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
    
    print(f"\n🔍 Source-Specific Fields:")
    sap_total = sources.get('sap', 0)
    app_total = sources.get('application', 0)
    print(f"  SAP with transaction codes: {sap_with_tcodes:,} / {sap_total:,}")
    print(f"  Apps with endpoints: {app_with_endpoints:,} / {app_total:,}")
    print(f"  Logs with correlation IDs: {logs_with_correlations:,} / {total:,}")
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
        
        # Verify source-specific fields are populated
        print("\n🔍 Verifying Source-Specific Fields:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM log_entries 
            WHERE source_type = 'sap' AND transaction_code IS NOT NULL
        """)
        sap_with_tcodes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM log_entries WHERE source_type = 'sap'
        """)
        total_sap = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM log_entries 
            WHERE source_type = 'application' AND endpoint IS NOT NULL
        """)
        app_with_endpoints = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM log_entries WHERE request_id IS NOT NULL
        """)
        with_request_ids = cursor.fetchone()[0]
        
        print(f"  SAP logs with transaction codes: {sap_with_tcodes:,} / {total_sap:,}")
        print(f"  Application logs with endpoints: {app_with_endpoints:,}")
        print(f"  Logs with correlation request_id: {with_request_ids:,}")
        
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

