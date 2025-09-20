"""
Logs endpoint for Vercel Functions.
"""

import json
from datetime import datetime


def handler(request):
    """
    Logs handler for Vercel Functions.
    """
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "message": "Logs endpoint",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        })
    }
