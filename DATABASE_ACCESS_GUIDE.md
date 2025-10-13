# PostgreSQL Database Access Guide

**Date:** October 13, 2025  
**Database Type:** PostgreSQL (Railway)  
**Note:** This is PostgreSQL, not MySQL

---

## 🔑 Getting Your Connection String

### Method 1: From Railway Dashboard (Recommended)

1. Go to https://railway.app/
2. Click on your project
3. Select the PostgreSQL service
4. Click the **Variables** tab
5. Copy the `DATABASE_URL` value

It will look like:
```
postgresql://postgres:PASSWORD@HOST.railway.app:5432/railway
```

### Method 2: From Vercel Environment Variables

```bash
vercel env pull .env.local
cat .env.local | grep DATABASE_URL
```

---

## 💻 Method 1: Command Line (psql) - Fastest

### Install PostgreSQL Client

**macOS:**
```bash
brew install postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql-client
```

**Windows:**
Download from: https://www.postgresql.org/download/windows/

### Connect to Database

```bash
# Option A: Direct connection with URL
psql "postgresql://postgres:PASSWORD@HOST.railway.app:5432/railway"

# Option B: Using environment variable
export DATABASE_URL="postgresql://postgres:PASSWORD@HOST.railway.app:5432/railway"
psql $DATABASE_URL
```

### Common Commands Once Connected

```sql
-- List all tables
\dt

-- Show table structure
\d log_entries

-- Count total logs
SELECT COUNT(*) FROM log_entries;

-- View recent logs
SELECT log_id, timestamp, level, message 
FROM log_entries 
ORDER BY timestamp DESC 
LIMIT 10;

-- Check log distribution
SELECT level, COUNT(*) as count 
FROM log_entries 
GROUP BY level 
ORDER BY count DESC;

-- Exit psql
\q
```

---

## 🖥️ Method 2: GUI Tools (User-Friendly)

### Option A: pgAdmin (Free, Full-Featured)

**Install:**
- Download from: https://www.pgadmin.org/download/

**Connect:**
1. Open pgAdmin
2. Right-click "Servers" → Create → Server
3. **General tab:**
   - Name: `Engineering Log Intelligence`
4. **Connection tab:**
   - Host: `your-host.railway.app` (from DATABASE_URL)
   - Port: `5432`
   - Database: `railway`
   - Username: `postgres`
   - Password: (from DATABASE_URL)
5. Click "Save"

### Option B: DBeaver (Free, Multi-Database)

**Install:**
- Download from: https://dbeaver.io/download/

**Connect:**
1. Open DBeaver
2. Database → New Database Connection
3. Select "PostgreSQL"
4. Enter connection details from DATABASE_URL
5. Test Connection → Finish

### Option C: TablePlus (Paid, Beautiful UI)

**Install:**
- Download from: https://tableplus.com/

**Connect:**
1. Click "Create a new connection"
2. Select PostgreSQL
3. Paste DATABASE_URL directly (it auto-parses)
4. Or fill in fields manually
5. Test → Connect

### Option D: DataGrip (JetBrains, Paid but Powerful)

**Install:**
- Download from: https://www.jetbrains.com/datagrip/

**Connect:**
1. Add Data Source → PostgreSQL
2. Paste DATABASE_URL or enter details
3. Download driver if prompted
4. Test Connection → OK

---

## 🐍 Method 3: Python Script (Programmatic)

### Quick Connection Test

Create `test_db_connection.py`:

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get DATABASE_URL from environment or paste directly
DATABASE_URL = os.getenv('DATABASE_URL') or "postgresql://postgres:PASSWORD@HOST:5432/railway"

def test_connection():
    """Test database connection and query some data"""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Connected successfully!\n")
        
        # Get database info
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL Version:\n{version['version']}\n")
        
        # Count tables
        cursor.execute("""
            SELECT COUNT(*) as table_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()
        print(f"📁 Total Tables: {table_count['table_count']}\n")
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print("📋 Tables:")
        for table in tables:
            print(f"   - {table['table_name']}")
        print()
        
        # Get log stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_logs,
                MIN(timestamp) as oldest_log,
                MAX(timestamp) as newest_log
            FROM log_entries
        """)
        stats = cursor.fetchone()
        print("📈 Log Statistics:")
        print(f"   Total Logs: {stats['total_logs']:,}")
        print(f"   Oldest: {stats['oldest_log']}")
        print(f"   Newest: {stats['newest_log']}")
        print()
        
        # Log level distribution
        cursor.execute("""
            SELECT level, COUNT(*) as count 
            FROM log_entries 
            GROUP BY level 
            ORDER BY count DESC
        """)
        distribution = cursor.fetchall()
        print("🎯 Log Level Distribution:")
        for row in distribution:
            print(f"   {row['level']:8} {row['count']:6,} logs")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Connection test complete!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
```

**Run it:**
```bash
cd engineering_log_intelligence
export DATABASE_URL="your-connection-string"
python test_db_connection.py
```

---

## 🔍 Method 4: From Your Existing Code

Your codebase already has database connection utilities:

```bash
cd engineering_log_intelligence

# Check database status
python check_database.py

# Test connections to all services
python test_connections.py

# Populate with test data
python populate_database.py 100
```

---

## 📊 Useful Queries

### Table Information

```sql
-- List all tables with row counts
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Show table structure
\d+ log_entries
```

### Log Analysis

```sql
-- Recent errors
SELECT log_id, timestamp, level, message, host
FROM log_entries
WHERE level IN ('ERROR', 'FATAL')
ORDER BY timestamp DESC
LIMIT 20;

-- Logs per hour (last 24 hours)
SELECT 
    date_trunc('hour', timestamp) as hour,
    COUNT(*) as log_count
FROM log_entries
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- Top error messages
SELECT message, COUNT(*) as occurrences
FROM log_entries
WHERE level = 'ERROR'
GROUP BY message
ORDER BY occurrences DESC
LIMIT 10;

-- Service health
SELECT 
    service,
    COUNT(*) as total_logs,
    SUM(CASE WHEN level IN ('ERROR', 'FATAL') THEN 1 ELSE 0 END) as error_count,
    ROUND(AVG(response_time_ms), 2) as avg_response_time
FROM log_entries
GROUP BY service
ORDER BY error_count DESC;
```

### ML Predictions

```sql
-- Check ML predictions
SELECT COUNT(*) FROM ml_predictions;

-- Recent predictions
SELECT 
    le.log_id,
    le.level as actual_level,
    mp.predicted_level,
    mp.level_confidence,
    mp.is_anomaly,
    mp.severity
FROM ml_predictions mp
JOIN log_entries le ON mp.log_entry_id = le.id
ORDER BY mp.predicted_at DESC
LIMIT 20;

-- Anomaly summary
SELECT 
    severity,
    COUNT(*) as anomaly_count
FROM ml_predictions
WHERE is_anomaly = true
GROUP BY severity
ORDER BY anomaly_count DESC;
```

---

## 🛠️ Troubleshooting

### "psql: command not found"
Install PostgreSQL client tools (see Installation section above)

### "Connection refused"
- Check if Railway database is running
- Verify DATABASE_URL is correct
- Ensure your IP isn't blocked

### "SSL connection required"
Add `sslmode=require` to connection string:
```
postgresql://user:pass@host:5432/db?sslmode=require
```

### "Password authentication failed"
- Double-check password in DATABASE_URL
- Regenerate credentials in Railway if needed

### "Database does not exist"
- Verify database name in connection string
- Check Railway dashboard for correct database name

---

## 🔐 Security Best Practices

### Do:
- ✅ Use environment variables for DATABASE_URL
- ✅ Keep credentials in `.env` (gitignored)
- ✅ Use SSL connections (`sslmode=require`)
- ✅ Rotate credentials periodically

### Don't:
- ❌ Commit DATABASE_URL to git
- ❌ Share connection strings publicly
- ❌ Use production credentials in development
- ❌ Store passwords in plain text files

---

## 📝 Quick Reference

**PostgreSQL vs MySQL Comparison:**

| Feature | PostgreSQL (You Have) | MySQL (You Asked For) |
|---------|----------------------|----------------------|
| Command | `psql` | `mysql` |
| Connection | `postgresql://...` | `mysql://...` |
| Port | 5432 | 3306 |
| Client Library | `psycopg2` | `mysql-connector` |

**You're using PostgreSQL**, which is actually more powerful for analytics and JSON data!

---

## 🚀 Next Steps

1. **Choose your preferred method** (I recommend GUI for browsing, psql for quick queries)
2. **Get your DATABASE_URL** from Railway
3. **Connect and explore** your data
4. **Save useful queries** for future use

Need help with any of these methods? Just let me know!

