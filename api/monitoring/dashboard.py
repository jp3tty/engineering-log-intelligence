"""
Monitoring dashboard endpoint for Vercel Functions.
Provides system metrics, health status, and performance data.
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import structlog

from api.utils.monitoring import (
    get_metrics_collector,
    get_alert_manager,
    create_success_response,
    create_error_response,
    logger
)

def handler(request) -> Dict[str, Any]:
    """
    Handle monitoring dashboard requests.
    
    Query parameters:
    - metrics: Include metrics data (true/false)
    - alerts: Include alerts data (true/false)
    - health: Include health check data (true/false)
    - timeframe: Time range for data (1h, 24h, 7d, 30d)
    """
    
    try:
        # Parse query parameters
        if hasattr(request, 'args'):
            query_params = request.args
        else:
            query_params = {}
            if hasattr(request, 'queryStringParameters') and request.queryStringParameters:
                query_params = request.queryStringParameters
        
        # Extract parameters
        include_metrics = query_params.get('metrics', 'true').lower() == 'true'
        include_alerts = query_params.get('alerts', 'true').lower() == 'true'
        include_health = query_params.get('health', 'true').lower() == 'true'
        timeframe = query_params.get('timeframe', '24h')
        
        # Build dashboard data
        dashboard_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "timeframe": timeframe
        }
        
        # Add metrics if requested
        if include_metrics:
            metrics_collector = get_metrics_collector()
            dashboard_data["metrics"] = get_system_metrics(metrics_collector, timeframe)
        
        # Add alerts if requested
        if include_alerts:
            alert_manager = get_alert_manager()
            dashboard_data["alerts"] = get_alerts_summary(alert_manager, timeframe)
        
        # Add health status if requested
        if include_health:
            dashboard_data["health"] = get_health_status()
        
        # Add system information
        dashboard_data["system"] = get_system_info()
        
        # Log dashboard access
        logger.info(
            "Monitoring dashboard accessed",
            include_metrics=include_metrics,
            include_alerts=include_alerts,
            include_health=include_health,
            timeframe=timeframe
        )
        
        return create_success_response(dashboard_data)
        
    except Exception as e:
        logger.error("Error in monitoring dashboard", error=str(e), exc_info=True)
        return create_error_response(
            "Failed to generate monitoring dashboard",
            "DASHBOARD_ERROR",
            500,
            {"error": str(e)}
        )

def get_system_metrics(metrics_collector, timeframe: str) -> Dict[str, Any]:
    """Get system metrics for the specified timeframe."""
    try:
        # Get collected metrics
        metrics_data = metrics_collector.get_metrics()
        
        # Calculate time range
        now = datetime.now(timezone.utc)
        time_ranges = {
            "1h": now - timedelta(hours=1),
            "24h": now - timedelta(hours=24),
            "7d": now - timedelta(days=7),
            "30d": now - timedelta(days=30)
        }
        
        start_time = time_ranges.get(timeframe, time_ranges["24h"])
        
        # Process metrics
        processed_metrics = {
            "counters": {},
            "gauges": {},
            "timings": {},
            "summary": {
                "total_metrics": len(metrics_data["metrics"]),
                "collection_duration_ms": metrics_data["collection_duration_ms"],
                "timeframe": timeframe,
                "start_time": start_time.isoformat(),
                "end_time": now.isoformat()
            }
        }
        
        for key, metric in metrics_data["metrics"].items():
            if metric["type"] == "counter":
                processed_metrics["counters"][key] = metric
            elif metric["type"] == "gauge":
                processed_metrics["gauges"][key] = metric
            elif metric["type"] == "timing":
                values = metric["values"]
                processed_metrics["timings"][key] = {
                    **metric,
                    "count": len(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "avg": sum(values) / len(values) if values else 0,
                    "p95": sorted(values)[int(len(values) * 0.95)] if values else 0,
                    "p99": sorted(values)[int(len(values) * 0.99)] if values else 0
                }
        
        return processed_metrics
        
    except Exception as e:
        logger.error("Error getting system metrics", error=str(e))
        return {"error": "Failed to get metrics", "details": str(e)}

def get_alerts_summary(alert_manager, timeframe: str) -> Dict[str, Any]:
    """Get alerts summary for the specified timeframe."""
    try:
        # Get all alerts
        all_alerts = alert_manager.get_alerts()
        
        # Filter by timeframe
        now = datetime.now(timezone.utc)
        time_ranges = {
            "1h": now - timedelta(hours=1),
            "24h": now - timedelta(hours=24),
            "7d": now - timedelta(days=7),
            "30d": now - timedelta(days=30)
        }
        
        start_time = time_ranges.get(timeframe, time_ranges["24h"])
        
        # Filter alerts by time
        filtered_alerts = []
        for alert in all_alerts:
            alert_time = datetime.fromisoformat(alert["created_at"].replace('Z', '+00:00'))
            if alert_time >= start_time:
                filtered_alerts.append(alert)
        
        # Categorize alerts
        alerts_by_severity = {}
        alerts_by_status = {}
        
        for alert in filtered_alerts:
            severity = alert["severity"]
            status = alert["status"]
            
            if severity not in alerts_by_severity:
                alerts_by_severity[severity] = 0
            alerts_by_severity[severity] += 1
            
            if status not in alerts_by_status:
                alerts_by_status[status] = 0
            alerts_by_status[status] += 1
        
        return {
            "total_alerts": len(filtered_alerts),
            "alerts_by_severity": alerts_by_severity,
            "alerts_by_status": alerts_by_status,
            "recent_alerts": filtered_alerts[-10:],  # Last 10 alerts
            "timeframe": timeframe,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting alerts summary", error=str(e))
        return {"error": "Failed to get alerts", "details": str(e)}

def get_health_status() -> Dict[str, Any]:
    """Get system health status."""
    try:
        # Basic health checks
        health_checks = {
            "vercel": {
                "status": "healthy",
                "message": "Vercel Functions running"
            },
            "environment": {
                "status": "warning",
                "message": "Environment variables check",
                "details": {
                    "python_version": "3.12",
                    "vercel_region": "unknown"
                }
            },
            "external_services": {
                "status": "warning",
                "message": "External service configuration check",
                "services": {
                    "database": False,
                    "elasticsearch": False,
                    "kafka": False
                }
            }
        }
        
        # Determine overall status
        statuses = [check["status"] for check in health_checks.values()]
        if "error" in statuses:
            overall_status = "unhealthy"
        elif "warning" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "checks": health_checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting health status", error=str(e))
        return {
            "status": "error",
            "message": "Failed to get health status",
            "error": str(e)
        }

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    try:
        import platform
        import sys
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting system info", error=str(e))
        return {"error": "Failed to get system info", "details": str(e)}
