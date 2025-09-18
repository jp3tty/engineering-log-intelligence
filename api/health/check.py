"""
Health check endpoint for the Engineering Log Intelligence System.
This function verifies that the system is running and can connect to external services.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
import structlog

from api.utils.monitoring import (
    create_health_check_response,
    create_error_response,
    monitor_function,
    logger
)


@monitor_function("health_check")
def handler(request) -> Dict[str, Any]:
    """
    Health check handler for Vercel Functions.

    Returns:
        Dict containing system status and health information
    """

    # Basic system information
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Engineering Log Intelligence System",
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "environment": os.getenv("VERCEL_ENV", "development"),
        "checks": {},
    }

    # Check if we're running in Vercel
    if os.getenv("VERCEL"):
        health_status["checks"]["vercel"] = {
            "status": "ok",
            "message": "Running on Vercel platform",
        }
    else:
        health_status["checks"]["vercel"] = {
            "status": "warning",
            "message": "Running locally",
        }

    # Check environment variables
    required_env_vars = ["JWT_SECRET_KEY", "DATABASE_URL", "ELASTICSEARCH_URL"]

    env_status = "ok"
    missing_vars = []

    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            env_status = "error"

    health_status["checks"]["environment"] = {
        "status": env_status,
        "message": f"Environment variables check: {len(missing_vars)} missing"
        if missing_vars
        else "All required variables present",
        "missing_variables": missing_vars,
    }

    # Check external service connectivity (basic check)
    external_services = {
        "database": os.getenv("DATABASE_URL") is not None,
        "elasticsearch": os.getenv("ELASTICSEARCH_URL") is not None,
        "kafka": os.getenv("KAFKA_BOOTSTRAP_SERVERS") is not None,
    }

    health_status["checks"]["external_services"] = {
        "status": "ok" if all(external_services.values()) else "warning",
        "message": "External service configuration check",
        "services": external_services,
    }

    # Determine overall status
    if health_status["checks"]["environment"]["status"] == "error":
        health_status["status"] = "unhealthy"
    elif any(
        check["status"] == "warning" for check in health_status["checks"].values()
    ):
        health_status["status"] = "degraded"

    # Return appropriate HTTP status code
    status_code = 200
    if health_status["status"] == "unhealthy":
        status_code = 503
    elif health_status["status"] == "degraded":
        status_code = 200  # Still operational but with warnings

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        "body": json.dumps(health_status, indent=2),
    }
