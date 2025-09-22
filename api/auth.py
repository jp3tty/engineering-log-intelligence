"""
Authentication endpoint for Vercel Functions.
"""

import json
import os
from datetime import datetime


def handler(request):
    """
    Authentication handler for Vercel Functions.
    """
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "message": "Authentication endpoint",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "environment": os.getenv("ENVIRONMENT", "development")
        })
    }
