"""
Metrics endpoint for Vercel Functions.
Provides detailed metrics and performance data.
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import structlog

from api.utils.monitoring import (
    get_metrics_collector,
    create_success_response,
    create_error_response,
    logger
)

def handler(request) -> Dict[str, Any]:
    """
    Handle metrics requests.
    
    Query parameters:
    - type: Metric type filter (counter, gauge, timing)
    - name: Specific metric name filter
    - tags: Tag filters (key=value format)
    - timeframe: Time range for data (1h, 24h, 7d, 30d)
    - format: Response format (json, prometheus)
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
        metric_type = query_params.get('type')
        metric_name = query_params.get('name')
        tags_filter = query_params.get('tags')
        timeframe = query_params.get('timeframe', '24h')
        format_type = query_params.get('format', 'json')
        
        # Get metrics collector
        metrics_collector = get_metrics_collector()
        
        # Get raw metrics
        raw_metrics = metrics_collector.get_metrics()
        
        # Filter metrics
        filtered_metrics = filter_metrics(
            raw_metrics["metrics"],
            metric_type=metric_type,
            metric_name=metric_name,
            tags_filter=tags_filter
        )
        
        # Process metrics based on format
        if format_type.lower() == 'prometheus':
            response_data = format_prometheus_metrics(filtered_metrics)
            content_type = "text/plain; version=0.0.4; charset=utf-8"
        else:
            response_data = format_json_metrics(filtered_metrics, timeframe)
            content_type = "application/json"
        
        # Log metrics access
        logger.info(
            "Metrics accessed",
            metric_type=metric_type,
            metric_name=metric_name,
            timeframe=timeframe,
            format=format_type,
            metrics_count=len(filtered_metrics)
        )
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": content_type,
                "Access-Control-Allow-Origin": "*"
            },
            "body": response_data if format_type.lower() == 'prometheus' else json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error("Error in metrics endpoint", error=str(e), exc_info=True)
        return create_error_response(
            "Failed to get metrics",
            "METRICS_ERROR",
            500,
            {"error": str(e)}
        )

def filter_metrics(
    metrics: Dict[str, Any],
    metric_type: Optional[str] = None,
    metric_name: Optional[str] = None,
    tags_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Filter metrics based on criteria."""
    filtered = {}
    
    for key, metric in metrics.items():
        # Filter by type
        if metric_type and metric["type"] != metric_type:
            continue
        
        # Filter by name
        if metric_name and metric_name not in key:
            continue
        
        # Filter by tags
        if tags_filter:
            if not matches_tags_filter(metric.get("tags", {}), tags_filter):
                continue
        
        filtered[key] = metric
    
    return filtered

def matches_tags_filter(metric_tags: Dict[str, str], tags_filter: str) -> bool:
    """Check if metric tags match the filter."""
    try:
        # Parse tags filter (format: "key1=value1,key2=value2")
        filter_pairs = tags_filter.split(',')
        for pair in filter_pairs:
            if '=' not in pair:
                continue
            key, value = pair.split('=', 1)
            if metric_tags.get(key.strip()) != value.strip():
                return False
        return True
    except Exception:
        return False

def format_json_metrics(metrics: Dict[str, Any], timeframe: str) -> Dict[str, Any]:
    """Format metrics as JSON."""
    now = datetime.now(timezone.utc)
    
    # Calculate time range
    time_ranges = {
        "1h": now - timedelta(hours=1),
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30)
    }
    
    start_time = time_ranges.get(timeframe, time_ranges["24h"])
    
    # Categorize metrics
    counters = {}
    gauges = {}
    timings = {}
    
    for key, metric in metrics.items():
        if metric["type"] == "counter":
            counters[key] = metric
        elif metric["type"] == "gauge":
            gauges[key] = metric
        elif metric["type"] == "timing":
            values = metric["values"]
            timings[key] = {
                **metric,
                "count": len(values),
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "avg": sum(values) / len(values) if values else 0,
                "p50": sorted(values)[int(len(values) * 0.5)] if values else 0,
                "p95": sorted(values)[int(len(values) * 0.95)] if values else 0,
                "p99": sorted(values)[int(len(values) * 0.99)] if values else 0
            }
    
    return {
        "timestamp": now.isoformat(),
        "timeframe": timeframe,
        "start_time": start_time.isoformat(),
        "end_time": now.isoformat(),
        "metrics": {
            "counters": counters,
            "gauges": gauges,
            "timings": timings
        },
        "summary": {
            "total_metrics": len(metrics),
            "counter_count": len(counters),
            "gauge_count": len(gauges),
            "timing_count": len(timings)
        }
    }

def format_prometheus_metrics(metrics: Dict[str, Any]) -> str:
    """Format metrics in Prometheus format."""
    lines = []
    
    # Add header
    lines.append("# HELP vercel_function_metrics Vercel Function Metrics")
    lines.append("# TYPE vercel_function_metrics counter")
    
    for key, metric in metrics.items():
        if metric["type"] == "counter":
            tags_str = format_prometheus_tags(metric.get("tags", {}))
            lines.append(f"vercel_function_counter{{{tags_str}}} {metric['value']}")
        
        elif metric["type"] == "gauge":
            tags_str = format_prometheus_tags(metric.get("tags", {}))
            lines.append(f"vercel_function_gauge{{{tags_str}}} {metric['value']}")
        
        elif metric["type"] == "timing":
            values = metric["values"]
            if values:
                tags_str = format_prometheus_tags(metric.get("tags", {}))
                lines.append(f"vercel_function_timing_count{{{tags_str}}} {len(values)}")
                lines.append(f"vercel_function_timing_sum{{{tags_str}}} {sum(values)}")
                lines.append(f"vercel_function_timing_avg{{{tags_str}}} {sum(values) / len(values)}")
                lines.append(f"vercel_function_timing_min{{{tags_str}}} {min(values)}")
                lines.append(f"vercel_function_timing_max{{{tags_str}}} {max(values)}")
    
    return "\n".join(lines)

def format_prometheus_tags(tags: Dict[str, str]) -> str:
    """Format tags for Prometheus metrics."""
    if not tags:
        return ""
    
    tag_pairs = [f'{k}="{v}"' for k, v in tags.items()]
    return "," + ",".join(tag_pairs)

def get_metric_summary(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Get summary statistics for metrics."""
    total_metrics = len(metrics)
    counter_count = sum(1 for m in metrics.values() if m["type"] == "counter")
    gauge_count = sum(1 for m in metrics.values() if m["type"] == "gauge")
    timing_count = sum(1 for m in metrics.values() if m["type"] == "timing")
    
    # Calculate total values
    total_counter_value = sum(m["value"] for m in metrics.values() if m["type"] == "counter")
    total_gauge_value = sum(m["value"] for m in metrics.values() if m["type"] == "gauge")
    
    # Calculate timing statistics
    all_timing_values = []
    for m in metrics.values():
        if m["type"] == "timing" and "values" in m:
            all_timing_values.extend(m["values"])
    
    timing_stats = {}
    if all_timing_values:
        timing_stats = {
            "total_measurements": len(all_timing_values),
            "min_duration_ms": min(all_timing_values),
            "max_duration_ms": max(all_timing_values),
            "avg_duration_ms": sum(all_timing_values) / len(all_timing_values),
            "p95_duration_ms": sorted(all_timing_values)[int(len(all_timing_values) * 0.95)],
            "p99_duration_ms": sorted(all_timing_values)[int(len(all_timing_values) * 0.99)]
        }
    
    return {
        "total_metrics": total_metrics,
        "counter_count": counter_count,
        "gauge_count": gauge_count,
        "timing_count": timing_count,
        "total_counter_value": total_counter_value,
        "total_gauge_value": total_gauge_value,
        "timing_stats": timing_stats
    }
