#!/bin/bash
# Check Railway Database Size and Usage
# Run periodically to monitor storage

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    echo "Usage: export DATABASE_URL='...' && ./check_db_size.sh"
    exit 1
fi

echo "🔍 Railway Database Storage Report"
echo "=================================="
echo ""

python3 -c "
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    
    # Get database size
    cursor.execute(\"SELECT pg_database_size('railway') as size\")
    size_bytes = cursor.fetchone()[0]
    size_mb = size_bytes / (1024 * 1024)
    size_gb = size_bytes / (1024 * 1024 * 1024)
    
    # Railway free tier limit
    limit_gb = 1.0
    limit_mb = 1024
    usage_pct = (size_mb / limit_mb) * 100
    
    print(f'📦 Database Size:')
    print(f'   {size_mb:.2f} MB ({size_gb:.3f} GB)')
    print()
    print(f'📊 Railway Free Tier Limit: {limit_mb} MB')
    print(f'   Usage: {usage_pct:.1f}%')
    print()
    
    # Visual progress bar
    bar_width = 40
    filled = int(bar_width * usage_pct / 100)
    bar = '█' * filled + '░' * (bar_width - filled)
    
    if usage_pct < 50:
        status = '✅ Plenty of space'
        color = ''
    elif usage_pct < 70:
        status = '⚠️  Monitor usage'
        color = ''
    elif usage_pct < 85:
        status = '⚠️  Getting full'
        color = ''
    else:
        status = '🚨 CRITICAL - Clean up soon!'
        color = ''
    
    print(f'   [{bar}] {usage_pct:.1f}%')
    print(f'   {status}')
    print()
    
    # Get log count
    cursor.execute('SELECT COUNT(*) FROM log_entries')
    log_count = cursor.fetchone()[0]
    bytes_per_log = size_bytes / log_count if log_count > 0 else 0
    
    print(f'📝 Log Entries: {log_count:,}')
    print(f'   Avg size per log: {bytes_per_log:.0f} bytes')
    print()
    
    # Calculate capacity
    remaining_bytes = (limit_mb * 1024 * 1024) - size_bytes
    remaining_logs = int(remaining_bytes / bytes_per_log) if bytes_per_log > 0 else 0
    
    print(f'💾 Remaining Capacity:')
    print(f'   {(limit_mb - size_mb):.2f} MB free')
    print(f'   ~{remaining_logs:,} more logs can fit')
    print()
    
    # Get table sizes
    cursor.execute(\"\"\"
        SELECT 
            relname as table_name,
            pg_size_pretty(pg_total_relation_size(relid)) as total_size,
            pg_size_pretty(pg_relation_size(relid)) as table_size,
            pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as index_size
        FROM pg_catalog.pg_statio_user_tables
        ORDER BY pg_total_relation_size(relid) DESC
        LIMIT 5;
    \"\"\")
    
    print(f'📊 Largest Tables:')
    print(f'   {\"Table\":<20} {\"Total\":<12} {\"Data\":<12} {\"Indexes\":<12}')
    print(f'   {\"─\"*20} {\"─\"*12} {\"─\"*12} {\"─\"*12}')
    for row in cursor.fetchall():
        print(f'   {row[0]:<20} {row[1]:<12} {row[2]:<12} {row[3]:<12}')
    print()
    
    # Recommendations
    if usage_pct > 85:
        print('🚨 RECOMMENDATIONS:')
        print('   1. Delete old logs: DELETE FROM log_entries WHERE timestamp < NOW() - INTERVAL \\'30 days\\'')
        print('   2. Run VACUUM FULL to reclaim space')
        print('   3. Consider upgrading Railway plan')
    elif usage_pct > 70:
        print('💡 RECOMMENDATIONS:')
        print('   • Monitor usage weekly')
        print('   • Consider setting up auto-cleanup for old logs')
    else:
        print('✅ Storage looks healthy!')
        print(f'   You can add ~{remaining_logs:,} more logs safely')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

echo ""
echo "=================================="
echo "Last checked: $(date)"

