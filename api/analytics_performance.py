"""
Analytics Performance API
========================

This API provides performance analytics and forecasting data.
It simulates real-time performance metrics and predictions.

Author: Engineering Log Intelligence Team
Date: October 2, 2025
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

def handler(request):
    """
    Main handler for analytics performance API.
    """
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }
    
    try:
        # Get parameters
        action = request.query.get('action', 'metrics')
        time_range = request.query.get('time_range', '7d')
        
        if action == 'metrics':
            return handleMetrics(request, headers, time_range)
        elif action == 'forecasts':
            return handleForecasts(request, headers, time_range)
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid action parameter'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handleMetrics(request, headers, time_range):
    """Handle performance metrics data."""
    
    # Generate time series data based on time range
    hours_back = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}
    points = hours_back.get(time_range, 168)
    
    now = datetime.now()
    time_series = []
    cpu_usage = []
    memory_usage = []
    response_times = []
    throughput = []
    
    for i in range(points):
        timestamp = now - timedelta(hours=i)
        time_series.append(timestamp.isoformat())
        
        # Generate realistic performance data
        cpu_usage.append(round(random.uniform(20, 80), 1))
        memory_usage.append(round(random.uniform(40, 90), 1))
        response_times.append(round(random.uniform(50, 200), 1))
        throughput.append(random.randint(100, 1000))
    
    # Reverse arrays to show chronological order
    time_series.reverse()
    cpu_usage.reverse()
    memory_usage.reverse()
    response_times.reverse()
    throughput.reverse()
    
    metrics_data = {
        'time_range': time_range,
        'time_series': time_series,
        'cpu_usage': {
            'data': cpu_usage,
            'avg': round(sum(cpu_usage) / len(cpu_usage), 1),
            'max': max(cpu_usage),
            'min': min(cpu_usage),
            'trend': round(random.uniform(-5, 5), 1)
        },
        'memory_usage': {
            'data': memory_usage,
            'avg': round(sum(memory_usage) / len(memory_usage), 1),
            'max': max(memory_usage),
            'min': min(memory_usage),
            'trend': round(random.uniform(-3, 3), 1)
        },
        'response_times': {
            'data': response_times,
            'avg': round(sum(response_times) / len(response_times), 1),
            'max': max(response_times),
            'min': min(response_times),
            'trend': round(random.uniform(-10, 10), 1)
        },
        'throughput': {
            'data': throughput,
            'avg': round(sum(throughput) / len(throughput), 0),
            'max': max(throughput),
            'min': min(throughput),
            'trend': round(random.uniform(5, 15), 1)
        },
        'alerts': [
            {
                'type': 'warning',
                'message': 'CPU usage exceeded 80% for 15 minutes',
                'timestamp': (now - timedelta(hours=2)).isoformat(),
                'severity': 'medium'
            },
            {
                'type': 'info',
                'message': 'Memory usage trending upward',
                'timestamp': (now - timedelta(hours=6)).isoformat(),
                'severity': 'low'
            }
        ],
        'generated_at': datetime.now().isoformat()
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(metrics_data)
    }

def handleForecasts(request, headers, time_range):
    """Handle performance forecasting data."""
    
    # Generate forecast data for next 24 hours
    now = datetime.now()
    forecast_hours = 24
    forecasts = []
    
    for i in range(1, forecast_hours + 1):
        forecast_time = now + timedelta(hours=i)
        forecasts.append({
            'timestamp': forecast_time.isoformat(),
            'cpu_usage': round(random.uniform(25, 85), 1),
            'memory_usage': round(random.uniform(45, 95), 1),
            'response_time': round(random.uniform(55, 180), 1),
            'throughput': random.randint(120, 1100),
            'confidence': round(random.uniform(0.7, 0.95), 2)
        })
    
    forecast_data = {
        'time_range': '24h_forecast',
        'forecasts': forecasts,
        'model_accuracy': round(random.uniform(0.85, 0.95), 2),
        'last_trained': (now - timedelta(hours=6)).isoformat(),
        'generated_at': datetime.now().isoformat()
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(forecast_data)
    }
