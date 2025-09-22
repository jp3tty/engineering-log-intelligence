"""
Optimized Health check endpoint for the Engineering Log Intelligence System.
This function includes performance optimizations and caching strategies.
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any
from functools import lru_cache

# Global variables for caching (Vercel Functions persist between invocations)
_cached_health_data = None
_last_health_check = 0
_CACHE_TTL = 30  # Cache for 30 seconds


@lru_cache(maxsize=1)
def get_environment_info() -> Dict[str, Any]:
    """Cache environment information to avoid repeated os.getenv calls."""
    return {
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "environment": os.getenv("VERCEL_ENV", "development"),
        "is_vercel": bool(os.getenv("VERCEL")),
        "required_vars": ["JWT_SECRET_KEY", "APP_NAME", "ENVIRONMENT"]
    }


@lru_cache(maxsize=1)
def get_external_services_config() -> Dict[str, bool]:
    """Cache external service configuration check."""
    return {
        "database": bool(os.getenv("DATABASE_URL")),
        "elasticsearch": bool(os.getenv("ELASTICSEARCH_URL")),
        "kafka": bool(os.getenv("KAFKA_BOOTSTRAP_SERVERS")),
    }


def check_environment_variables(required_vars: list) -> Dict[str, Any]:
    """Optimized environment variable checking."""
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    return {
        "status": "error" if missing_vars else "ok",
        "message": f"Environment variables check: {len(missing_vars)} missing" if missing_vars else "All required variables present",
        "missing_variables": missing_vars,
    }


def get_cached_health_data() -> Dict[str, Any]:
    """Get cached health data if still valid, otherwise refresh."""
    global _cached_health_data, _last_health_check
    
    current_time = time.time()
    
    # Return cached data if still valid
    if _cached_health_data and (current_time - _last_health_check) < _CACHE_TTL:
        return _cached_health_data
    
    # Generate new health data
    env_info = get_environment_info()
    external_services = get_external_services_config()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Engineering Log Intelligence System",
        "version": env_info["version"],
        "environment": env_info["environment"],
        "checks": {
            "vercel": {
                "status": "ok" if env_info["is_vercel"] else "warning",
                "message": "Running on Vercel platform" if env_info["is_vercel"] else "Running locally",
            },
            "environment": check_environment_variables(env_info["required_vars"]),
            "external_services": {
                "status": "ok" if all(external_services.values()) else "warning",
                "message": "External service configuration check",
                "services": external_services,
            }
        },
    }
    
    # Determine overall status
    if health_status["checks"]["environment"]["status"] == "error":
        health_status["status"] = "unhealthy"
    elif any(check["status"] == "warning" for check in health_status["checks"].values()):
        health_status["status"] = "degraded"
    
    # Cache the result
    _cached_health_data = health_status
    _last_health_check = current_time
    
    return health_status


def handler(request) -> Dict[str, Any]:
    """
    Optimized health check handler for Vercel Functions.
    Includes caching and performance optimizations.
    """
    try:
        # Get cached or fresh health data
        health_status = get_cached_health_data()
        
        # Determine HTTP status code
        status_code = 200
        if health_status["status"] == "unhealthy":
            status_code = 503
        elif health_status["status"] == "degraded":
            status_code = 200  # Still operational but with warnings
        
        # Pre-built headers for better performance
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Cache-Control": "public, max-age=30",  # Cache for 30 seconds
            "X-Response-Time": f"{time.time():.3f}s"
        }
        
        return {
            "statusCode": status_code,
            "headers": headers,
            "body": json.dumps(health_status, separators=(',', ':')),  # Compact JSON
        }
        
    except Exception as e:
        # Error handling with minimal overhead
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "status": "error",
                "message": "Health check failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
