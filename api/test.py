"""
Simple test endpoint for Vercel Functions.
"""

import json
from datetime import datetime


def handler(request):
    """
    Simple test handler for Vercel Functions.
    """
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "message": "Hello from Vercel Functions!",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        })
    }
