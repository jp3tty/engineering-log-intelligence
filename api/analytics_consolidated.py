"""
Consolidated Analytics API Functions
====================================
Combines insights, reports, export, and performance analytics into a single function
to fit within Vercel Hobby plan limits (12 functions max).
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import parse_qs
import pandas as pd
from io import StringIO
import base64

# Mock analytics data for demonstration
MOCK_ANALYTICS_DATA = {
    "insights": {
        "trends": [
            {"metric": "Error Rate", "trend": "decreasing", "change": -15.2, "period": "7 days"},
            {"metric": "Response Time", "trend": "stable", "change": 2.1, "period": "7 days"},
            {"metric": "Throughput", "trend": "increasing", "change": 23.7, "period": "7 days"}
        ],
        "anomalies": [
            {"timestamp": "2025-09-29T10:30:00Z", "type": "spike", "severity": "high", "description": "Unusual error spike detected"},
            {"timestamp": "2025-09-29T14:15:00Z", "type": "pattern", "severity": "medium", "description": "New error pattern identified"}
        ],
        "recommendations": [
            {"category": "performance", "priority": "high", "description": "Consider scaling database connections"},
            {"category": "security", "priority": "medium", "description": "Review authentication patterns"}
        ]
    },
    "reports": {
        "templates": [
            {"id": "daily", "name": "Daily Operations Report", "description": "Daily system performance and health summary"},
            {"id": "weekly", "name": "Weekly Analytics Report", "description": "Weekly trends and insights"},
            {"id": "monthly", "name": "Monthly Executive Summary", "description": "Monthly business intelligence report"},
            {"id": "incident", "name": "Incident Analysis Report", "description": "Incident response and resolution analysis"}
        ],
        "generated_reports": [
            {"id": "rpt_001", "template": "daily", "status": "completed", "created_at": "2025-09-29T00:00:00Z"},
            {"id": "rpt_002", "template": "weekly", "status": "completed", "created_at": "2025-09-28T00:00:00Z"}
        ]
    },
    "performance": {
        "metrics": {
            "response_time": {"current": 245, "average": 220, "trend": "increasing"},
            "throughput": {"current": 1250, "average": 1100, "trend": "increasing"},
            "error_rate": {"current": 0.8, "average": 1.2, "trend": "decreasing"},
            "availability": {"current": 99.9, "average": 99.7, "trend": "stable"}
        },
        "capacity_forecast": {
            "cpu": {"current": 65, "forecast_30d": 78, "forecast_90d": 85},
            "memory": {"current": 45, "forecast_30d": 52, "forecast_90d": 58},
            "storage": {"current": 30, "forecast_30d": 35, "forecast_90d": 42}
        }
    }
}

def handler(request):
    """Main handler for consolidated analytics functions"""
    
    # Parse request method and path
    method = request.get('REQUEST_METHOD', 'GET')
    path = request.get('PATH_INFO', '')
    query_string = request.get('QUERY_STRING', '')
    query_params = parse_qs(query_string) if query_string else {}
    
    # Get the action from query parameters
    action = query_params.get('action', ['insights'])[0]
    
    try:
        if action == 'insights':
            return handle_insights(request, query_params)
        elif action == 'reports':
            return handle_reports(request, query_params, method)
        elif action == 'export':
            return handle_export(request, query_params)
        elif action == 'performance':
            return handle_performance(request, query_params)
        else:
            return create_response(400, {"error": "Invalid action specified"})
            
    except Exception as e:
        return create_response(500, {"error": f"Internal server error: {str(e)}"})

def handle_insights(request, query_params):
    """Handle analytics insights requests"""
    
    # Get time range from query params
    time_range = query_params.get('time_range', ['7d'])[0]
    
    # Mock ML-powered insights
    insights_data = {
        "time_range": time_range,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "trends": MOCK_ANALYTICS_DATA["insights"]["trends"],
        "anomalies": MOCK_ANALYTICS_DATA["insights"]["anomalies"],
        "recommendations": MOCK_ANALYTICS_DATA["insights"]["recommendations"],
        "summary": {
            "total_logs_analyzed": 1250000,
            "anomalies_detected": 23,
            "accuracy": 0.87
        }
    }
    
    return create_response(200, insights_data)

def handle_reports(request, query_params, method):
    """Handle report generation and management"""
    
    if method == 'GET':
        # List available reports and templates
        report_data = {
            "templates": MOCK_ANALYTICS_DATA["reports"]["templates"],
            "generated_reports": MOCK_ANALYTICS_DATA["reports"]["generated_reports"],
            "available_formats": ["pdf", "excel", "csv", "json"]
        }
        return create_response(200, report_data)
    
    elif method == 'POST':
        # Generate new report
        template_id = query_params.get('template', ['daily'])[0]
        format_type = query_params.get('format', ['pdf'])[0]
        
        # Mock report generation
        report_id = f"rpt_{int(time.time())}"
        report_data = {
            "report_id": report_id,
            "template": template_id,
            "format": format_type,
            "status": "generated",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "download_url": f"/api/analytics_consolidated?action=export&report_id={report_id}"
        }
        
        return create_response(201, report_data)
    
    return create_response(405, {"error": "Method not allowed"})

def handle_export(request, query_params):
    """Handle data export requests"""
    
    format_type = query_params.get('format', ['json'])[0]
    data_type = query_params.get('type', ['logs'])[0]
    
    # Mock export data
    if data_type == 'logs':
        export_data = [
            {"timestamp": "2025-09-29T10:00:00Z", "level": "ERROR", "message": "Database connection failed", "service": "postgres"},
            {"timestamp": "2025-09-29T10:01:00Z", "level": "WARN", "message": "High memory usage detected", "service": "elasticsearch"},
            {"timestamp": "2025-09-29T10:02:00Z", "level": "INFO", "message": "User login successful", "service": "auth"}
        ]
    
    if format_type == 'csv':
        # Convert to CSV
        df = pd.DataFrame(export_data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        return create_response(200, {
            "data": base64.b64encode(csv_content.encode()).decode(),
            "format": "csv",
            "filename": f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        })
    
    elif format_type == 'excel':
        # Convert to Excel
        df = pd.DataFrame(export_data)
        excel_buffer = StringIO()
        df.to_excel(excel_buffer, index=False)
        excel_content = excel_buffer.getvalue()
        
        return create_response(200, {
            "data": base64.b64encode(excel_content.encode()).decode(),
            "format": "excel",
            "filename": f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        })
    
    else:  # JSON
        return create_response(200, {
            "data": export_data,
            "format": "json",
            "filename": f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        })

def handle_performance(request, query_params):
    """Handle performance analytics requests"""
    
    # Mock performance data
    performance_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metrics": MOCK_ANALYTICS_DATA["performance"]["metrics"],
        "capacity_forecast": MOCK_ANALYTICS_DATA["performance"]["capacity_forecast"],
        "recommendations": [
            {"category": "scaling", "priority": "medium", "description": "Consider horizontal scaling for database"},
            {"category": "optimization", "priority": "low", "description": "Cache frequently accessed data"}
        ]
    }
    
    return create_response(200, performance_data)

def create_response(status_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a standardized response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(data)
    }

# For local testing
if __name__ == "__main__":
    # Test the handler
    test_request = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/api/analytics_consolidated',
        'QUERY_STRING': 'action=insights&time_range=7d'
    }
    
    response = handler(test_request)
    print(f"Status: {response['statusCode']}")
    print(f"Response: {json.loads(response['body'])}")
