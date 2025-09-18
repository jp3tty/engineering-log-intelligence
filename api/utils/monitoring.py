"""
Monitoring and logging utilities for Vercel Functions.
Provides structured logging, metrics collection, and performance monitoring.
"""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import structlog
from functools import wraps

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class MetricsCollector:
    """Collects and stores metrics for Vercel Functions."""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = self._get_metric_key(name, tags)
        if key not in self.metrics:
            self.metrics[key] = {"type": "counter", "value": 0, "tags": tags or {}}
        self.metrics[key]["value"] += value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        key = self._get_metric_key(name, tags)
        self.metrics[key] = {"type": "gauge", "value": value, "tags": tags or {}}
    
    def record_timing(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric."""
        key = self._get_metric_key(name, tags)
        if key not in self.metrics:
            self.metrics[key] = {"type": "timing", "values": [], "tags": tags or {}}
        self.metrics[key]["values"].append(duration_ms)
    
    def _get_metric_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Generate a unique key for a metric."""
        if not tags:
            return name
        tag_str = ",".join([f"{k}={v}" for k, v in sorted(tags.items())])
        return f"{name}[{tag_str}]"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "metrics": self.metrics,
            "collection_duration_ms": (time.time() - self.start_time) * 1000,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

class PerformanceMonitor:
    """Monitors function performance and execution times."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.execution_id = str(uuid.uuid4())
    
    def start(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        logger.info("Function execution started", execution_id=self.execution_id)
    
    def end(self):
        """End performance monitoring."""
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000
        logger.info(
            "Function execution completed",
            execution_id=self.execution_id,
            duration_ms=duration_ms
        )
        return duration_ms
    
    def get_execution_time(self) -> Optional[float]:
        """Get execution time in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None

def monitor_function(metric_name: str = None, tags: Optional[Dict[str, str]] = None):
    """Decorator to monitor function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function name if not provided
            function_name = metric_name or func.__name__
            
            # Initialize monitoring
            monitor = PerformanceMonitor()
            metrics = MetricsCollector()
            
            # Start monitoring
            monitor.start()
            metrics.increment_counter(f"{function_name}.invocations", tags=tags)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Record success metrics
                metrics.increment_counter(f"{function_name}.success", tags=tags)
                
                # End monitoring
                duration_ms = monitor.end()
                metrics.record_timing(f"{function_name}.duration", duration_ms, tags=tags)
                
                # Log success
                logger.info(
                    "Function executed successfully",
                    function=function_name,
                    duration_ms=duration_ms,
                    execution_id=monitor.execution_id
                )
                
                return result
                
            except Exception as e:
                # Record error metrics
                metrics.increment_counter(f"{function_name}.errors", tags=tags)
                
                # End monitoring
                duration_ms = monitor.end()
                metrics.record_timing(f"{function_name}.duration", duration_ms, tags=tags)
                
                # Log error
                logger.error(
                    "Function execution failed",
                    function=function_name,
                    error=str(e),
                    duration_ms=duration_ms,
                    execution_id=monitor.execution_id,
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator

def log_function_call(func_name: str, request_data: Dict[str, Any], response_data: Dict[str, Any] = None):
    """Log function call details."""
    logger.info(
        "Function call",
        function=func_name,
        request_data=request_data,
        response_data=response_data,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context."""
    logger.error(
        "Error occurred",
        error=str(error),
        error_type=type(error).__name__,
        context=context or {},
        timestamp=datetime.now(timezone.utc).isoformat(),
        exc_info=True
    )

def log_performance_metrics(metrics: Dict[str, Any]):
    """Log performance metrics."""
    logger.info(
        "Performance metrics",
        metrics=metrics,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

def create_health_check_response(
    status: str,
    checks: Dict[str, Any],
    version: str = "0.1.0",
    environment: str = "development"
) -> Dict[str, Any]:
    """Create standardized health check response."""
    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Engineering Log Intelligence System",
        "version": version,
        "environment": environment,
        "checks": checks
    }

def create_error_response(
    error_message: str,
    error_code: str = "INTERNAL_ERROR",
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "error": error_code,
            "message": error_message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    }

def create_success_response(
    data: Dict[str, Any],
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create standardized success response."""
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps({
            **data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    }

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self):
        self.alerts = []
    
    def create_alert(
        self,
        title: str,
        description: str,
        severity: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new alert."""
        alert_id = str(uuid.uuid4())
        alert = {
            "id": alert_id,
            "title": title,
            "description": description,
            "severity": severity,
            "source": source,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "open"
        }
        
        self.alerts.append(alert)
        
        # Log alert
        logger.warning(
            "Alert created",
            alert_id=alert_id,
            title=title,
            severity=severity,
            source=source
        )
        
        return alert_id
    
    def get_alerts(self, status: str = None) -> List[Dict[str, Any]]:
        """Get alerts, optionally filtered by status."""
        if status:
            return [alert for alert in self.alerts if alert["status"] == status]
        return self.alerts

# Global instances
metrics_collector = MetricsCollector()
alert_manager = AlertManager()

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return metrics_collector

def get_alert_manager() -> AlertManager:
    """Get the global alert manager."""
    return alert_manager
