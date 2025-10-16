"""
Lightweight ML API - Queries Pre-computed Predictions
=====================================================

This API queries predictions from the ml_predictions table that was
populated by GitHub Actions.

Author: Engineering Log Intelligence Team
Date: October 16, 2025
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
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
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        action = params.get('action', ['status'])[0]
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if action == 'status':
            response = self.handle_status()
        elif action == 'stats':
            response = self.handle_stats()
        elif action == 'analyze':
            response = self.handle_analyze()
        else:
            response = {"error": f"Unknown action: {action}"}
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def get_db_connection(self):
        """Get connection from shared pool"""
        try:
            from api._db_pool import get_db_connection
            return get_db_connection()
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
            result = cursor.fetchone()
            table_exists = result[0] if result else False
            
            if not table_exists:
                cursor.close()
                conn.close()
                return {
                    "success": True,
                    "ml_system": "not_initialized",
                    "message": "ML predictions table not yet created. Run GitHub Actions workflow.",
                    "logs_available": True,
                    "predictions_available": False
                }
            
            # Get prediction stats
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
                "latest_prediction": result[0].isoformat() if result[0] else None,
                "total_predictions": result[1],
                "logs_available": True,
                "predictions_available": True,
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
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ml_predictions'
                )
            """)
            result = cursor.fetchone()
            table_exists = result[0] if result else False
            
            if not table_exists:
                cursor.close()
                conn.close()
                return {
                    "success": True,
                    "statistics": {
                        "severity_distribution": [],
                        "anomaly_count": 0,
                        "total_predictions": 0,
                        "high_severity_count": 0
                    },
                    "message": "ML predictions table not yet created",
                    "source": "empty"
                }
            
            # Get severity distribution
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM ml_predictions
                WHERE predicted_at > NOW() - INTERVAL '24 hours'
                GROUP BY severity
                ORDER BY count DESC
            """)
            severity_results = cursor.fetchall()
            severity_stats = [{"severity": row[0], "count": row[1]} for row in severity_results]
            
            # Get anomaly stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COALESCE(SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END), 0) as anomaly_count,
                    COALESCE(SUM(CASE WHEN is_anomaly AND severity = 'high' THEN 1 ELSE 0 END), 0) as high_severity_count
                FROM ml_predictions
                WHERE predicted_at > NOW() - INTERVAL '24 hours'
            """)
            anomaly_result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            # Build response
            total = int(anomaly_result[0]) if anomaly_result else 0
            anomaly_count = int(anomaly_result[1]) if anomaly_result else 0
            high_severity_count = int(anomaly_result[2]) if anomaly_result else 0
            
            return {
                "success": True,
                "statistics": {
                    "severity_distribution": severity_stats,
                    "total_predictions": total,
                    "anomaly_count": anomaly_count,
                    "high_severity_count": high_severity_count,
                    "anomaly_rate": (anomaly_count / max(total, 1)) * 100
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
    
    def handle_analyze(self):
        """Get recent ML predictions"""
        conn = self.get_db_connection()
        
        if not conn:
            return {
                "success": False,
                "error": "Database connection unavailable"
            }
        
        try:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ml_predictions'
                )
            """)
            result = cursor.fetchone()
            table_exists = result[0] if result else False
            
            if not table_exists:
                cursor.close()
                conn.close()
                return {
                    "success": True,
                    "results": [],
                    "total": 0,
                    "message": "ML predictions table not yet created",
                    "source": "empty"
                }
            
            # Get recent predictions
            cursor.execute("""
                SELECT 
                    mp.id,
                    mp.log_entry_id,
                    mp.predicted_level,
                    mp.level_confidence,
                    mp.is_anomaly,
                    mp.anomaly_score,
                    mp.severity,
                    mp.predicted_at
                FROM ml_predictions mp
                WHERE mp.predicted_at > NOW() - INTERVAL '24 hours'
                ORDER BY mp.predicted_at DESC
                LIMIT 100
            """)
            
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convert to JSON-serializable format
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "log_entry_id": row[1],
                    "predicted_level": row[2],
                    "level_confidence": float(row[3]) if row[3] is not None else None,
                    "is_anomaly": row[4],
                    "anomaly_score": float(row[5]) if row[5] is not None else None,
                    "severity": row[6],
                    "predicted_at": row[7].isoformat() if row[7] else None
                })
            
            return {
                "success": True,
                "results": results,
                "total": len(results),
                "source": "database",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {
                "success": False,
                "error": str(e)
            }
