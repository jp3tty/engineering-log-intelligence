"""
Logs endpoint for Vercel Functions.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for logs API"""
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Get environment info
            environment = os.getenv('ENVIRONMENT', 'development')
            app_name = os.getenv('APP_NAME', 'Engineering Log Intelligence')
            
            # Generate sample logs data
            logs_data = {
                "success": True,
                "data": {
                    "logs": [
                        {
                            "id": "log_001",
                            "timestamp": datetime.utcnow().isoformat(),
                            "level": "INFO",
                            "message": "System startup completed successfully",
                            "source": "application",
                            "service": "main"
                        },
                        {
                            "id": "log_002",
                            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                            "level": "WARNING",
                            "message": "High memory usage detected",
                            "source": "monitoring",
                            "service": "system"
                        },
                        {
                            "id": "log_003",
                            "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                            "level": "ERROR",
                            "message": "Database connection timeout",
                            "source": "database",
                            "service": "postgres"
                        }
                    ],
                    "summary": {
                        "total_logs": 3,
                        "error_count": 1,
                        "warning_count": 1,
                        "info_count": 1
                    }
                },
                "environment": environment,
                "app_name": app_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send response
            self.wfile.write(json.dumps(logs_data, indent=2).encode())
            
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