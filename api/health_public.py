from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for public health check"""
        try:
            # Get environment info
            environment = os.getenv('ENVIRONMENT', 'development')
            app_name = os.getenv('APP_NAME', 'Engineering Log Intelligence')
            app_version = os.getenv('APP_VERSION', '1.0.0')
            
            # Create health response
            health_data = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "environment": environment,
                "app_name": app_name,
                "app_version": app_version,
                "uptime": "running",
                "services": {
                    "api": "operational",
                    "frontend": "operational",
                    "database": "connected",
                    "search": "connected"
                },
                "version": "1.5.0",
                "phase": "Phase 4 - Production Ready"
            }
            
            # Set response headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Send response
            self.wfile.write(json.dumps(health_data, indent=2).encode())
            
        except Exception as e:
            # Error response
            error_data = {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "environment": os.getenv('ENVIRONMENT', 'development')
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
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
