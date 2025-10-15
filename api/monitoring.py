"""
Advanced Monitoring API
=======================
Provides detailed monitoring metrics for the Monitoring tab:
- Alert/Incident feed
- Resource usage metrics
- Response time percentiles (p50, p95, p99)
- System resource utilization

Author: Engineering Log Intelligence Team
Date: October 12, 2025
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal

def convert_to_json_serializable(obj):
    """Convert non-JSON-serializable types to serializable ones"""
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

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
            
            response = self.get_monitoring_data()
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
        """Get connection from shared pool (reduces Railway connection count)"""
        try:
            # Import shared connection pool
            from api._db_pool import get_db_connection
            return get_db_connection()
        except:
            return None
    
    def get_monitoring_data(self):
        """Get comprehensive monitoring data"""
        conn = self.get_db_connection()
        
        if not conn:
            return {
                "success": False,
                "error": "Database connection unavailable"
            }
        
        try:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get recent incidents (FATAL and ERROR logs)
            incidents = self.get_recent_incidents(cursor)
            
            # Get response time percentiles
            percentiles = self.get_response_time_percentiles(cursor)
            
            # Get resource usage metrics
            resources = self.get_resource_metrics(cursor)
            
            # Get ML anomaly alerts
            ml_alerts = self.get_ml_alerts(cursor)
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "data": {
                    "incidents": incidents,
                    "percentiles": percentiles,
                    "resources": resources,
                    "ml_alerts": ml_alerts
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_recent_incidents(self, cursor):
        """Get recent FATAL and ERROR incidents"""
        cursor.execute("""
            SELECT 
                log_id,
                timestamp,
                level,
                message,
                source_type,
                host,
                service,
                response_time_ms,
                http_status
            FROM log_entries
            WHERE level IN ('FATAL', 'ERROR')
                AND timestamp > NOW() - INTERVAL '24 hours'
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        
        incidents = cursor.fetchall()
        return [convert_to_json_serializable(dict(incident)) for incident in incidents]
    
    def get_response_time_percentiles(self, cursor):
        """Calculate response time percentiles (p50, p95, p99)"""
        cursor.execute("""
            SELECT 
                PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY response_time_ms) as p50,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95,
                PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99,
                MIN(response_time_ms) as min,
                MAX(response_time_ms) as max,
                AVG(response_time_ms) as avg,
                COUNT(*) as total_requests
            FROM log_entries
            WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND response_time_ms IS NOT NULL
        """)
        
        result = cursor.fetchone()
        
        if result:
            return {
                "p50": float(result['p50']) if result['p50'] else 0,
                "p95": float(result['p95']) if result['p95'] else 0,
                "p99": float(result['p99']) if result['p99'] else 0,
                "min": float(result['min']) if result['min'] else 0,
                "max": float(result['max']) if result['max'] else 0,
                "avg": float(result['avg']) if result['avg'] else 0,
                "total_requests": result['total_requests']
            }
        
        return {
            "p50": 0, "p95": 0, "p99": 0,
            "min": 0, "max": 0, "avg": 0,
            "total_requests": 0
        }
    
    def get_resource_metrics(self, cursor):
        """Get resource usage metrics"""
        # Database size
        cursor.execute("""
            SELECT pg_database_size(current_database()) as db_size
        """)
        db_size_result = cursor.fetchone()
        db_size_bytes = db_size_result['db_size'] if db_size_result else 0
        db_size_mb = db_size_bytes / (1024 * 1024)
        
        # Total logs
        cursor.execute("""
            SELECT COUNT(*) as total_logs FROM log_entries
        """)
        total_logs = cursor.fetchone()['total_logs']
        
        # Logs in last hour (throughput indicator)
        cursor.execute("""
            SELECT COUNT(*) as recent_logs 
            FROM log_entries 
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """)
        recent_logs = cursor.fetchone()['recent_logs']
        
        # Log levels distribution (last 24h)
        cursor.execute("""
            SELECT 
                level,
                COUNT(*) as count
            FROM log_entries
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY level
        """)
        
        level_distribution = {}
        for row in cursor.fetchall():
            level_distribution[row['level']] = row['count']
        
        # ML predictions count
        try:
            cursor.execute("""
                SELECT COUNT(*) as prediction_count 
                FROM ml_predictions 
                WHERE predicted_at > NOW() - INTERVAL '24 hours'
            """)
            ml_prediction_count = cursor.fetchone()['prediction_count']
        except:
            ml_prediction_count = 0
        
        return {
            "database": {
                "size_mb": round(db_size_mb, 2),
                "size_formatted": f"{db_size_mb:.2f} MB",
                "total_logs": total_logs,
                "growth_rate": f"{recent_logs} logs/hour"
            },
            "throughput": {
                "logs_per_hour": recent_logs,
                "logs_per_minute": round(recent_logs / 60, 2),
                "logs_per_second": round(recent_logs / 3600, 2)
            },
            "level_distribution": level_distribution,
            "ml_predictions": {
                "count_24h": ml_prediction_count,
                "status": "active" if ml_prediction_count > 0 else "inactive"
            }
        }
    
    def get_ml_alerts(self, cursor):
        """Get high-severity ML anomaly alerts"""
        try:
            cursor.execute("""
                SELECT 
                    mp.log_entry_id,
                    le.log_id,
                    le.timestamp,
                    le.message,
                    le.level as actual_level,
                    mp.predicted_level,
                    mp.is_anomaly,
                    mp.anomaly_score,
                    mp.severity,
                    mp.predicted_at,
                    le.source_type,
                    le.host,
                    le.service
                FROM ml_predictions mp
                JOIN log_entries le ON mp.log_entry_id = le.id
                WHERE mp.is_anomaly = true
                    AND mp.severity = 'high'
                    AND mp.predicted_at > NOW() - INTERVAL '24 hours'
                ORDER BY mp.predicted_at DESC
                LIMIT 25
            """)
            
            alerts = cursor.fetchall()
            return [convert_to_json_serializable(dict(alert)) for alert in alerts]
        except:
            return []

