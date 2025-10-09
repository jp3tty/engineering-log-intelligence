"""
Authentication endpoint for Vercel Functions.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for auth API"""
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
            
            # Generate auth status data
            auth_data = {
                "success": True,
                "data": {
                    "authentication": {
                        "status": "active",
                        "method": "JWT",
                        "expires_in": 1800
                    },
                    "user_info": {
                        "username": "demo_user",
                        "role": "analyst",
                        "permissions": ["read_logs", "view_dashboard", "create_reports"]
                    },
                    "session": {
                        "created_at": datetime.utcnow().isoformat(),
                        "last_activity": datetime.utcnow().isoformat(),
                        "ip_address": "127.0.0.1"
                    }
                },
                "environment": environment,
                "app_name": app_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send response
            self.wfile.write(json.dumps(auth_data, indent=2).encode())
            
        except Exception as e:
            # Error response
            error_data = {
                "success": False,
                "error": "AUTH_ERROR",
                "message": f"Authentication API error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data, indent=2).encode())
    
    def do_POST(self):
        """Handle POST requests for auth API (login)"""
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
            
            # Generate mock login response
            login_data = {
                "success": True,
                "data": {
                    "access_token": f"mock_jwt_token_{secrets.token_hex(16)}",
                    "refresh_token": f"mock_refresh_token_{secrets.token_hex(16)}",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "user": {
                        "id": 1,
                        "username": "demo_user",
                        "email": "demo@example.com",
                        "role": "analyst",
                        "permissions": ["read_logs", "view_dashboard", "create_reports"]
                    }
                },
                "environment": environment,
                "app_name": app_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send response
            self.wfile.write(json.dumps(login_data, indent=2).encode())
            
        except Exception as e:
            # Error response
            error_data = {
                "success": False,
                "error": "AUTH_ERROR",
                "message": f"Authentication API error: {str(e)}",
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