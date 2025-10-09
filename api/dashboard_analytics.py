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
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from http.server import BaseHTTPRequestHandler

# Database connection
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    """
    Main handler class for dashboard analytics API.
    
    For beginners: This class runs when someone visits the API endpoint.
    It generates sample data and returns it as JSON.
    """
    
    def do_GET(self):
        """Handle GET requests"""
        self._send_response()
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests for CORS"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def _send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _send_response(self):
        """Generate and send the analytics data response"""
        try:
            # Try to connect to database
            db_conn, db_error = get_database_connection()
            use_real_data = db_conn is not None
            
            # Generate time labels for the last 24 hours
            now = datetime.now()
            time_labels = []
            for i in range(7):  # 7 data points for 24 hours
                hour = now - timedelta(hours=24 - (i * 4))
                time_labels.append(hour.strftime('%H:%M'))
            
            if use_real_data:
                # Fetch real data from database
                log_volume_data = fetch_log_volume_from_db(db_conn, time_labels)
                log_distribution_data = fetch_log_distribution_from_db(db_conn)
                response_time_data = fetch_response_time_from_db(db_conn, time_labels)
                error_types_data = fetch_error_types_from_db(db_conn)
                system_metrics = fetch_system_metrics_from_db(db_conn)
                db_conn.close()
            else:
                # Fallback to simulated data if database is unavailable
                log_volume_data = generate_log_volume_data(time_labels)
                log_distribution_data = generate_log_distribution_data()
                response_time_data = generate_response_time_data(time_labels)
                error_types_data = generate_error_types_data()
                system_metrics = generate_system_metrics()
            
            # Combine all data
            analytics_data = {
                'logVolume': log_volume_data,
                'logDistribution': log_distribution_data,
                'responseTime': response_time_data,
                'errorTypes': error_types_data,
                'systemMetrics': system_metrics,
                'timestamp': now.isoformat(),
                'dataSource': 'database' if use_real_data else 'simulated',
                'debug': {
                    'DATABASE_AVAILABLE': DATABASE_AVAILABLE,
                    'DATABASE_URL_SET': bool(os.environ.get('DATABASE_URL')),
                    'db_connection_successful': use_real_data,
                    'db_error': db_error if not use_real_data else None
                }
            }
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(analytics_data).encode())
            
        except Exception as e:
            # Handle errors gracefully
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            error_response = {
                'error': 'Failed to generate analytics data',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())

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

# ============================================================================
# DATABASE CONNECTION AND QUERY FUNCTIONS
# ============================================================================

def get_database_connection() -> tuple:
    """
    Establish connection to PostgreSQL database.
    Returns (connection, error_message) tuple.
    """
    if not DATABASE_AVAILABLE:
        return None, "psycopg2 not available"
    
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return None, "DATABASE_URL environment variable not set"
        
        conn = psycopg2.connect(database_url)
        conn.autocommit = True  # Prevent transaction abort issues
        return conn, None
    except Exception as e:
        error_msg = f"Connection failed: {str(e)}"
        return None, error_msg

def fetch_log_volume_from_db(conn, time_labels: List[str]) -> Dict[str, Any]:
    """
    Fetch log volume data from database for the last 24 hours.
    """
    try:
        cursor = conn.cursor()
        
        # Query log counts grouped by hour
        cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as log_count
            FROM log_entries
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour
        """)
        
        results = cursor.fetchall()
        cursor.close()
        
        # If we have data, use it; otherwise fall back to simulated
        if results:
            data_points = [row[1] for row in results]
            # Pad or truncate to 7 data points
            while len(data_points) < 7:
                data_points.append(0)
            data_points = data_points[:7]
        else:
            # No data in database, generate simulated
            data_points = [random.randint(800, 2500) for _ in range(7)]
        
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
    except Exception as e:
        print(f"Error fetching log volume: {e}")
        return generate_log_volume_data(time_labels)

def fetch_log_distribution_from_db(conn) -> Dict[str, Any]:
    """
    Fetch log level distribution from database.
    """
    try:
        cursor = conn.cursor()
        
        # Query log counts by level
        cursor.execute("""
            SELECT 
                level,
                COUNT(*) as count
            FROM log_entries
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY level
        """)
        
        results = cursor.fetchall()
        cursor.close()
        
        # Build distribution dictionary
        distribution = {'INFO': 0, 'WARN': 0, 'ERROR': 0, 'DEBUG': 0, 'FATAL': 0}
        for row in results:
            level = row[0].upper()
            if level in distribution:
                distribution[level] = row[1]
        
        # If no data, use simulated
        if sum(distribution.values()) == 0:
            total_logs = 1000
            distribution = {
                'INFO': int(total_logs * 0.60),
                'WARN': int(total_logs * 0.25),
                'ERROR': int(total_logs * 0.10),
                'DEBUG': int(total_logs * 0.04),
                'FATAL': int(total_logs * 0.01)
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
    except Exception as e:
        print(f"Error fetching log distribution: {e}")
        return generate_log_distribution_data()

def fetch_response_time_from_db(conn, time_labels: List[str]) -> Dict[str, Any]:
    """
    Fetch average response times from database.
    """
    try:
        cursor = conn.cursor()
        
        # Query average response time by hour
        cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                AVG(response_time_ms) as avg_response_time
            FROM log_entries
            WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND response_time_ms IS NOT NULL
            GROUP BY hour
            ORDER BY hour
        """)
        
        results = cursor.fetchall()
        cursor.close()
        
        if results:
            data_points = [int(row[1]) if row[1] else 85 for row in results]
            while len(data_points) < 7:
                data_points.append(85)
            data_points = data_points[:7]
        else:
            data_points = [random.randint(70, 110) for _ in range(7)]
        
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
    except Exception as e:
        print(f"Error fetching response time: {e}")
        return generate_response_time_data(time_labels)

def fetch_error_types_from_db(conn) -> Dict[str, Any]:
    """
    Fetch error type distribution from database.
    """
    try:
        cursor = conn.cursor()
        
        # Query error counts by type
        cursor.execute("""
            SELECT 
                error_type,
                COUNT(*) as count
            FROM log_entries
            WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND level IN ('ERROR', 'FATAL')
                AND error_type IS NOT NULL
            GROUP BY error_type
            ORDER BY count DESC
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        cursor.close()
        
        if results:
            error_types = {row[0]: row[1] for row in results}
        else:
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
    except Exception as e:
        print(f"Error fetching error types: {e}")
        return generate_error_types_data()

def fetch_system_metrics_from_db(conn) -> Dict[str, Any]:
    """
    Fetch system metrics from database.
    """
    try:
        cursor = conn.cursor()
        
        # Query total logs processed (all time)
        cursor.execute("""
            SELECT COUNT(*) FROM log_entries
        """)
        logs_processed = cursor.fetchone()[0]
        
        # Query active alerts
        cursor.execute("""
            SELECT COUNT(*) FROM log_entries 
            WHERE timestamp > NOW() - INTERVAL '1 hour'
                AND level IN ('ERROR', 'FATAL')
        """)
        active_alerts = cursor.fetchone()[0]
        
        # Query average response time
        cursor.execute("""
            SELECT AVG(response_time_ms) FROM log_entries 
            WHERE timestamp > NOW() - INTERVAL '1 hour'
                AND response_time_ms IS NOT NULL
        """)
        avg_response = cursor.fetchone()[0]
        response_time = int(avg_response) if avg_response else 85
        
        cursor.close()
        
        return {
            'logsProcessed': logs_processed,
            'activeAlerts': active_alerts,
            'responseTime': response_time,
            'systemHealth': 'Healthy' if active_alerts < 10 else 'Warning',
            'uptime': '99.9%',
            'cpuUsage': 45,
            'memoryUsage': 52,
            'diskUsage': 63
        }
    except Exception as e:
        error_msg = f"Error fetching system metrics: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        # Return error in metrics for debugging
        fallback = generate_system_metrics()
        fallback['_db_error'] = error_msg
        return fallback
