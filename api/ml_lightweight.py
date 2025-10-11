"""
Lightweight ML API - Queries Pre-computed Predictions
=====================================================

This API doesn't run ML models - it just queries predictions that were
pre-computed by GitHub Actions. This keeps Vercel deployment small and fast!

Benefits:
- No ML libraries needed (saves 50MB+)
- Fast responses (database queries are ~10ms)
- Stays within Vercel Hobby tier limits
- Scalable for millions of logs

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
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            action = params.get('action', ['analyze'])[0]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            if action == 'analyze':
                response = self.handle_analyze()
            elif action == 'status':
                response = self.handle_status()
            elif action == 'stats':
                response = self.handle_stats()
            else:
                response = {"error": f"Unknown action: {action}"}
            
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
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            action = data.get('action', 'analyze')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            if action == 'analyze':
                response = self.handle_analyze(data)
            else:
                response = {"error": f"Unknown action: {action}"}
            
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
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
    
    def handle_status(self):
        """Return ML system status"""
        conn = self.get_db_connection()
        
        if not conn:
            return {
                "success": True,
                "ml_system": "offline",
                "message": "Database connection unavailable"
            }
        
        try:
            cursor = conn.cursor()
            
            # Check if ML predictions table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ml_predictions'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                cursor.close()
                conn.close()
                return {
                    "success": True,
                    "ml_system": "not_initialized",
                    "message": "ML predictions table not yet created. Run GitHub Actions workflow."
                }
            
            # Get latest prediction time
            cursor.execute("""
                SELECT MAX(predicted_at) as latest_prediction,
                       COUNT(*) as total_predictions
                FROM ml_predictions
            """)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "ml_system": "active",
                "architecture": "batch_processing",
                "deployment_size": "lightweight (no ML libraries in Vercel)",
                "prediction_source": "pre-computed (GitHub Actions)",
                "latest_prediction": result[0].isoformat() if result[0] else None,
                "total_predictions": result[1],
                "query_time": "~10ms (database)",
                "ml_compute_time": "~28ms (GitHub Actions)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_analyze(self, data=None):
        """Get ML predictions for logs"""
        conn = self.get_db_connection()
        
        if not conn:
            return {
                "success": False,
                "error": "Database connection unavailable"
            }
        
        try:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get recent predictions with log details
            cursor.execute("""
                SELECT 
                    le.log_id,
                    le.message,
                    le.level as actual_level,
                    mp.predicted_level,
                    mp.level_confidence,
                    mp.is_anomaly,
                    mp.anomaly_score,
                    mp.severity,
                    mp.predicted_at
                FROM ml_predictions mp
                JOIN log_entries le ON mp.log_entry_id = le.id
                WHERE mp.predicted_at > NOW() - INTERVAL '24 hours'
                ORDER BY mp.predicted_at DESC
                LIMIT 100
            """)
            
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "results": [dict(r) for r in results],
                "total": len(results),
                "source": "pre-computed_predictions",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_stats(self):
        """Get ML statistics"""
        conn = self.get_db_connection()
        
        if not conn:
            return {
                "success": False,
                "error": "Database connection unavailable"
            }
        
        try:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get severity distribution
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM ml_predictions
                WHERE predicted_at > NOW() - INTERVAL '24 hours'
                GROUP BY severity
                ORDER BY count DESC
            """)
            severity_stats = cursor.fetchall()
            
            # Get anomaly stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomalies
                FROM ml_predictions
                WHERE predicted_at > NOW() - INTERVAL '24 hours'
            """)
            anomaly_stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "statistics": {
                    "severity_distribution": [dict(s) for s in severity_stats],
                    "total_predictions": anomaly_stats['total'],
                    "anomalies_detected": anomaly_stats['anomalies'],
                    "anomaly_rate": anomaly_stats['anomalies'] / max(anomaly_stats['total'], 1)
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

