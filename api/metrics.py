"""
Real-time Metrics API
=====================
Returns real metrics calculated from the database:
- Total log count
- Average response time
- System health (based on error rates and anomalies)

Author: Engineering Log Intelligence Team
Date: October 11, 2025
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            response = self.get_metrics()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def get_db_connection(self):
        """Get database connection"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return None
        
        try:
            conn = psycopg2.connect(database_url)
            return conn
        except:
            return None
    
    def get_metrics(self):
        """Get real metrics from database"""
        conn = self.get_db_connection()
        
        if not conn:
            return {
                "success": False,
                "error": "Database connection unavailable"
            }
        
        try:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get total log count (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) as total_logs
                FROM log_entries
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            log_count_result = cursor.fetchone()
            total_logs = log_count_result['total_logs'] if log_count_result else 0
            
            # Get average response time (last 24 hours)
            cursor.execute("""
                SELECT AVG(response_time_ms) as avg_response_time
                FROM log_entries
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND response_time_ms IS NOT NULL
            """)
            response_time_result = cursor.fetchone()
            avg_response_time = float(response_time_result['avg_response_time']) if response_time_result and response_time_result['avg_response_time'] else 0
            
            # Get error rate (ERROR and FATAL logs vs total)
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE level IN ('ERROR', 'FATAL')) as error_count,
                    COUNT(*) as total_count
                FROM log_entries
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            error_rate_result = cursor.fetchone()
            error_count = error_rate_result['error_count'] if error_rate_result else 0
            total_count = error_rate_result['total_count'] if error_rate_result else 1
            error_rate = (error_count / max(total_count, 1)) * 100
            
            # Get ML anomaly rate from ml_predictions
            try:
                cursor.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE is_anomaly = true) as anomaly_count,
                        COUNT(*) as total_predictions
                    FROM ml_predictions
                    WHERE predicted_at > NOW() - INTERVAL '24 hours'
                """)
                ml_result = cursor.fetchone()
                anomaly_count = ml_result['anomaly_count'] if ml_result else 0
                total_predictions = ml_result['total_predictions'] if ml_result else 0
                ml_anomaly_rate = (anomaly_count / max(total_predictions, 1)) * 100
            except:
                ml_anomaly_rate = 0
            
            # Calculate system health
            # Base health: 100%
            # Subtract error rate impact (errors are bad)
            # Subtract anomaly rate impact (anomalies indicate issues)
            base_health = 100.0
            error_impact = error_rate * 2  # Errors have 2x weight
            anomaly_impact = ml_anomaly_rate * 0.5  # Anomalies have 0.5x weight
            
            system_health = max(0, base_health - error_impact - anomaly_impact)
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "metrics": {
                    "total_logs": total_logs,
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "error_rate": round(error_rate, 2),
                    "ml_anomaly_rate": round(ml_anomaly_rate, 2),
                    "system_health": round(system_health, 1)
                },
                "period": "last_24_hours",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {
                "success": False,
                "error": str(e)
            }

