"""
Dashboard Analytics API
======================

This API provides analytics data for the dashboard charts.
It simulates real-time data for demonstration purposes.

For beginners: This is a backend API that provides data to our frontend charts.
When the frontend requests dashboard data, this function runs and returns
the data in a format that the charts can understand.

Author: Engineering Log Intelligence Team
Date: September 22, 2025
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

def handler(request):
    """
    Main handler function for dashboard analytics API.
    
    For beginners: This function runs when someone visits the API endpoint.
    It generates sample data and returns it as JSON.
    """
    
    # For beginners: This sets the response headers
    # CORS allows our frontend to call this API from a different domain
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests (for beginners: this is needed for CORS)
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Generate time labels for the last 24 hours
        now = datetime.now()
        time_labels = []
        for i in range(7):  # 7 data points for 24 hours
            hour = now - timedelta(hours=24 - (i * 4))
            time_labels.append(hour.strftime('%H:%M'))
        
        # Generate log volume data (simulated)
        log_volume_data = generate_log_volume_data(time_labels)
        
        # Generate log distribution data
        log_distribution_data = generate_log_distribution_data()
        
        # Generate response time data
        response_time_data = generate_response_time_data(time_labels)
        
        # Generate error types data
        error_types_data = generate_error_types_data()
        
        # Generate system metrics
        system_metrics = generate_system_metrics()
        
        # Combine all data
        analytics_data = {
            'logVolume': log_volume_data,
            'logDistribution': log_distribution_data,
            'responseTime': response_time_data,
            'errorTypes': error_types_data,
            'systemMetrics': system_metrics,
            'timestamp': now.isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(analytics_data)
        }
        
    except Exception as e:
        # For beginners: This handles errors gracefully
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Failed to generate analytics data',
                'message': str(e)
            })
        }

def generate_log_volume_data(time_labels: List[str]) -> Dict[str, Any]:
    """
    Generate log volume data for the line chart.
    
    For beginners: This creates realistic-looking data for how many logs
    were processed each hour over the last 24 hours.
    """
    # Simulate realistic log volume patterns
    base_volume = 1000
    data_points = []
    
    for i, label in enumerate(time_labels):
        # Simulate higher volume during business hours (8 AM - 6 PM)
        hour = int(label.split(':')[0])
        if 8 <= hour <= 18:
            multiplier = random.uniform(1.5, 2.5)
        else:
            multiplier = random.uniform(0.3, 0.8)
        
        volume = int(base_volume * multiplier + random.randint(-200, 200))
        data_points.append(max(0, volume))  # Ensure non-negative
    
    return {
        'labels': time_labels,
        'datasets': [{
            'label': 'Logs per hour',
            'data': data_points,
            'borderColor': 'rgb(59, 130, 246)',
            'backgroundColor': 'rgba(59, 130, 246, 0.1)',
            'tension': 0.4,
            'fill': True
        }]
    }

def generate_log_distribution_data() -> Dict[str, Any]:
    """
    Generate log distribution data for the pie chart.
    
    For beginners: This shows what percentage of logs are INFO, WARN, ERROR, etc.
    """
    # Simulate realistic log level distribution
    total_logs = 1000
    distribution = {
        'INFO': int(total_logs * 0.60),    # 60% info logs
        'WARN': int(total_logs * 0.25),    # 25% warning logs
        'ERROR': int(total_logs * 0.10),   # 10% error logs
        'DEBUG': int(total_logs * 0.04),   # 4% debug logs
        'FATAL': int(total_logs * 0.01)    # 1% fatal logs
    }
    
    return {
        'labels': list(distribution.keys()),
        'datasets': [{
            'data': list(distribution.values()),
            'backgroundColor': [
                'rgb(34, 197, 94)',   # Green for INFO
                'rgb(245, 158, 11)',  # Yellow for WARN
                'rgb(239, 68, 68)',   # Red for ERROR
                'rgb(107, 114, 128)', # Gray for DEBUG
                'rgb(147, 51, 234)'   # Purple for FATAL
            ],
            'borderWidth': 2,
            'borderColor': '#ffffff'
        }]
    }

def generate_response_time_data(time_labels: List[str]) -> Dict[str, Any]:
    """
    Generate response time data for the line chart.
    
    For beginners: This shows how fast the system responds over time.
    Lower response times are better.
    """
    data_points = []
    
    for i, label in enumerate(time_labels):
        # Simulate realistic response times with some variation
        base_time = 85  # Base response time in milliseconds
        variation = random.randint(-15, 25)  # Add some randomness
        response_time = max(50, base_time + variation)  # Minimum 50ms
        data_points.append(response_time)
    
    return {
        'labels': time_labels,
        'datasets': [{
            'label': 'Average Response Time (ms)',
            'data': data_points,
            'borderColor': 'rgb(16, 185, 129)',
            'backgroundColor': 'rgba(16, 185, 129, 0.1)',
            'tension': 0.4,
            'fill': True
        }]
    }

def generate_error_types_data() -> Dict[str, Any]:
    """
    Generate error types data for the bar chart.
    
    For beginners: This shows what types of errors are most common.
    """
    error_types = {
        'Database': random.randint(30, 60),
        'Network': random.randint(20, 45),
        'Authentication': random.randint(15, 35),
        'Validation': random.randint(10, 25),
        'System': random.randint(5, 15)
    }
    
    return {
        'labels': list(error_types.keys()),
        'datasets': [{
            'label': 'Error Count',
            'data': list(error_types.values()),
            'backgroundColor': [
                'rgba(239, 68, 68, 0.8)',
                'rgba(245, 158, 11, 0.8)',
                'rgba(147, 51, 234, 0.8)',
                'rgba(59, 130, 246, 0.8)',
                'rgba(16, 185, 129, 0.8)'
            ],
            'borderColor': [
                'rgb(239, 68, 68)',
                'rgb(245, 158, 11)',
                'rgb(147, 51, 234)',
                'rgb(59, 130, 246)',
                'rgb(16, 185, 129)'
            ],
            'borderWidth': 1
        }]
    }

def generate_system_metrics() -> Dict[str, Any]:
    """
    Generate system metrics for the dashboard cards.
    
    For beginners: This provides the numbers shown in the status cards
    at the top of the dashboard.
    """
    return {
        'logsProcessed': random.randint(120000, 130000),
        'activeAlerts': random.randint(0, 5),
        'responseTime': random.randint(80, 100),
        'systemHealth': random.choice(['Healthy', 'Warning', 'Critical']),
        'uptime': f"{random.randint(99, 100)}.{random.randint(0, 99)}%",
        'cpuUsage': random.randint(20, 80),
        'memoryUsage': random.randint(30, 70),
        'diskUsage': random.randint(40, 90)
    }
