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
        """Get connection from shared pool (reduces Railway connection count)"""
        try:
            # Import shared connection pool
            from api._db_pool import get_db_connection
            return get_db_connection()
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
            
            # Get FATAL and ERROR counts separately (industry standard)
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE level = 'FATAL') as fatal_count,
                    COUNT(*) FILTER (WHERE level = 'ERROR') as error_count,
                    COUNT(*) as total_count
                FROM log_entries
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            error_rate_result = cursor.fetchone()
            fatal_count = error_rate_result['fatal_count'] if error_rate_result else 0
            error_count = error_rate_result['error_count'] if error_rate_result else 0
            total_count = error_rate_result['total_count'] if error_rate_result else 1
            
            fatal_rate = (fatal_count / max(total_count, 1)) * 100
            error_rate = (error_count / max(total_count, 1)) * 100
            
            # Get high-severity ML anomalies only (not all anomalies)
            try:
                cursor.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE is_anomaly = true AND severity = 'high') as high_anomaly_count,
                        COUNT(*) as total_predictions
                    FROM ml_predictions
                    WHERE predicted_at > NOW() - INTERVAL '24 hours'
                """)
                ml_result = cursor.fetchone()
                high_anomaly_count = ml_result['high_anomaly_count'] if ml_result else 0
                total_predictions = ml_result['total_predictions'] if ml_result else 0
                high_anomaly_rate = (high_anomaly_count / max(total_predictions, 1)) * 100
            except:
                high_anomaly_rate = 0
            
            # Calculate system health (Industry Standard Approach)
            # Similar to AWS CloudWatch, DataDog, New Relic
            # - Start at 99% baseline (no system is "perfect" 100%)
            # - Only penalize for critical issues (FATAL, ERROR, high-severity anomalies)
            # - Use small deductions to keep scores realistic (90-99% is normal)
            # - Floor at 85% (even troubled systems should show some health)
            base_health = 99.0
            
            # Deductions (much smaller than before)
            fatal_impact = fatal_rate * 3.0      # FATAL logs are serious: 1% fatal = -3% health
            error_impact = error_rate * 0.5      # ERROR logs less severe: 1% error = -0.5% health
            anomaly_impact = high_anomaly_rate * 0.3  # Only high-severity anomalies: 1% = -0.3% health
            
            # Calculate final health with floor and ceiling
            system_health = base_health - fatal_impact - error_impact - anomaly_impact
            system_health = max(85.0, min(99.9, system_health))  # Floor: 85%, Ceiling: 99.9%
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "metrics": {
                    "total_logs": total_logs,
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "fatal_rate": round(fatal_rate, 2),
                    "error_rate": round(error_rate, 2),
                    "high_anomaly_rate": round(high_anomaly_rate, 2),
                    "high_anomaly_count": high_anomaly_count,  # Add actual count
                    "system_health": round(system_health, 1)
                },
                "calculation": {
                    "base": 99.0,
                    "fatal_impact": round(fatal_impact, 2),
                    "error_impact": round(error_impact, 2),
                    "anomaly_impact": round(anomaly_impact, 2)
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

