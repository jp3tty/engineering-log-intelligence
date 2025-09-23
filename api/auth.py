"""
Authentication endpoint for Vercel Functions.
"""

import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets


def handler(request):
    """
    Authentication handler for Vercel Functions.
    """
    
    # Set CORS headers
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"message": "CORS preflight successful"})
        }
    
    try:
        if request.method == 'POST':
            # Handle login request
            if hasattr(request, 'body'):
                body = request.body
            else:
                body = request.get('body', '{}')
            
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
            
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            # Demo credentials for testing
            demo_users = {
                'admin': {
                    'password': 'password123',
                    'role': 'admin',
                    'permissions': ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data', 'manage_users', 'manage_system', 'configure_alerts']
                },
                'analyst': {
                    'password': 'password123',
                    'role': 'analyst',
                    'permissions': ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data']
                },
                'user': {
                    'password': 'password123',
                    'role': 'user',
                    'permissions': ['read_logs', 'view_dashboard', 'create_alerts']
                }
            }
            
            # Check credentials
            if username in demo_users and demo_users[username]['password'] == password:
                # Generate tokens (simplified for demo)
                access_token = f"demo_access_token_{username}_{int(datetime.utcnow().timestamp())}"
                refresh_token = f"demo_refresh_token_{username}_{int(datetime.utcnow().timestamp())}"
                
                user_data = {
                    'id': 1,
                    'username': username,
                    'email': f'{username}@example.com',
                    'role': demo_users[username]['role'],
                    'permissions': demo_users[username]['permissions'],
                    'first_name': username.title(),
                    'last_name': 'User'
                }
                
                return {
                    "statusCode": 200,
                    "headers": headers,
                    "body": json.dumps({
                        "user": user_data,
                        "tokens": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "expires_in": 1800
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }
            else:
                return {
                    "statusCode": 401,
                    "headers": headers,
                    "body": json.dumps({
                        "error": "Invalid credentials",
                        "message": "Username or password is incorrect"
                    })
                }
        
        else:
            # Handle GET request - return endpoint info
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Authentication endpoint",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success",
                    "environment": os.getenv("ENVIRONMENT", "development"),
                    "available_methods": ["POST", "GET", "OPTIONS"]
                })
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
