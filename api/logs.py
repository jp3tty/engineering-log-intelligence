"""
Logs endpoint for Vercel Functions.
Fetches real log data from PostgreSQL database.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

# Database connection
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

def get_database_connection():
    """Establish connection to PostgreSQL database."""
    if not DATABASE_AVAILABLE:
        return None, "psycopg2 not available"
    
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return None, "DATABASE_URL not set"
        
        conn = psycopg2.connect(database_url, sslmode='require')
        return conn, None
    except Exception as e:
        return None, str(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for logs API"""
        try:
            # Parse query parameters
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            
            # Extract filters
            search_query = params.get('search', [''])[0]
            log_level = params.get('level', [''])[0]
            source_system = params.get('source', [''])[0]
            time_range = params.get('timeRange', ['24h'])[0]
            page = int(params.get('page', ['1'])[0])
            page_size = int(params.get('pageSize', ['50'])[0])
            
            # Try to fetch from database
            db_conn, db_error = get_database_connection()
            use_real_data = db_conn is not None
            
            if use_real_data:
                logs_data = fetch_logs_from_db(
                    db_conn, search_query, log_level, source_system, 
                    time_range, page, page_size
                )
                db_conn.close()
            else:
                # Fallback to sample data
                logs_data = generate_sample_logs(page, page_size)
                logs_data['dataSource'] = 'simulated'
                logs_data['db_error'] = db_error
            
            # Set CORS headers and send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Send response with custom JSON encoder for special types
            try:
                response_json = json.dumps(logs_data, indent=2, default=str)
                self.wfile.write(response_json.encode())
            except Exception as json_error:
                print(f"JSON serialization error: {str(json_error)}")
                # Try without special handling
                self.wfile.write(json.dumps(logs_data, default=str).encode())
            
        except Exception as e:
            # Error response
            error_data = {
                "success": False,
                "error": "LOGS_ERROR",
                "message": f"Logs API error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

def fetch_logs_from_db(conn, search_query, log_level, source_system, time_range, page, page_size):
    """Fetch logs from database with filtering and pagination."""
    try:
        print(f"🔍 fetch_logs_from_db called with: search={search_query}, level={log_level}, source={source_system}, time={time_range}, page={page}, size={page_size}")
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Parse time range
        time_mapping = {
            '1h': '1 hour',
            '6h': '6 hours',
            '24h': '24 hours',
            '7d': '7 days',
            '30d': '30 days'
        }
        time_interval = time_mapping.get(time_range, '24 hours')
        
        # Build WHERE clause dynamically
        where_clauses = [f"timestamp > NOW() - INTERVAL '{time_interval}'"]
        params = []
        
        if search_query:
            where_clauses.append("message ILIKE %s")
            params.append(f'%{search_query}%')
        
        if log_level:
            where_clauses.append("level = %s")
            params.append(log_level)
        
        if source_system:
            where_clauses.append("source_type = %s")
            params.append(source_system)
        
        where_clause = " AND ".join(where_clauses)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM log_entries WHERE {where_clause}"
        print(f"🔍 Count query: {count_query}")
        print(f"🔍 Params: {params}")
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['total']
        print(f"📊 Total logs found: {total_count}")
        
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Fetch paginated logs
        logs_query = f"""
            SELECT 
                id,
                timestamp,
                level,
                message,
                source_type,
                response_time_ms,
                session_id,
                ip_address,
                host,
                service,
                category,
                tags,
                is_anomaly
            FROM log_entries 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(logs_query, params + [page_size, offset])
        logs = cursor.fetchall()
        
        # Convert to list of dicts and format
        formatted_logs = []
        for log in logs:
            # Handle different id types (UUID or integer)
            log_id = str(log['id']) if log['id'] else None
            
            formatted_logs.append({
                'id': log_id,
                'timestamp': log['timestamp'].isoformat() if log['timestamp'] else None,
                'level': log['level'] or 'INFO',
                'message': log['message'] or '',
                'source': log['source_type'] or 'UNKNOWN',
                'responseTime': float(log['response_time_ms']) if log['response_time_ms'] else None,
                'host': log['host'],
                'service': log['service'],
                'category': log['category'],
                'tags': log['tags'] if log['tags'] else [],
                'isAnomaly': bool(log['is_anomaly']),
                'sessionId': log['session_id'],
                'ipAddress': str(log['ip_address']) if log['ip_address'] else None
            })
        
        # Calculate summary stats
        cursor.execute(f"""
            SELECT 
                level,
                COUNT(*) as count
            FROM log_entries 
            WHERE {where_clause}
            GROUP BY level
        """, params)
        level_counts = cursor.fetchall()
        
        summary = {
            'total_logs': total_count,
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'fatal_count': 0
        }
        
        for row in level_counts:
            level = row['level'].lower()
            summary[f'{level}_count'] = row['count']
        
        cursor.close()
        
        return {
            "success": True,
            "data": {
                "logs": formatted_logs,
                "summary": summary,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            },
            "dataSource": "database",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return fallback data on error
        fallback = generate_sample_logs(page, page_size)
        fallback['dataSource'] = 'simulated'
        fallback['db_error'] = str(e)
        return fallback

def generate_sample_logs(page, page_size):
    """Generate sample log data as fallback."""
    sample_logs = [
        {
            "id": 1,
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": "System startup completed successfully",
            "source": "APPLICATION",
            "responseTime": 45,
            "userId": None,
            "metadata": None
        },
        {
            "id": 2,
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "level": "WARN",
            "message": "High CPU usage detected on server-01: 95% utilization",
            "source": "SPLUNK",
            "responseTime": 120,
            "userId": "system",
            "metadata": None
        },
        {
            "id": 3,
            "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
            "level": "ERROR",
            "message": "Database connection timeout after 30 seconds",
            "source": "APPLICATION",
            "responseTime": 30000,
            "userId": None,
            "metadata": None
        },
        {
            "id": 4,
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "level": "INFO",
            "message": "User authentication successful for admin@company.com",
            "source": "SAP",
            "responseTime": 85,
            "userId": "admin@company.com",
            "metadata": None
        },
        {
            "id": 5,
            "timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
            "level": "FATAL",
            "message": "Out of memory error: Unable to allocate 512MB for process",
            "source": "SYSTEM",
            "responseTime": None,
            "userId": None,
            "metadata": None
        }
    ]
    
    return {
        "success": True,
        "data": {
            "logs": sample_logs,
            "summary": {
                "total_logs": len(sample_logs),
                "error_count": 1,
                "warning_count": 1,
                "info_count": 2,
                "fatal_count": 1,
                "debug_count": 0
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": len(sample_logs),
                "total_pages": 1
            }
        },
        "dataSource": "simulated",
        "timestamp": datetime.utcnow().isoformat()
    }