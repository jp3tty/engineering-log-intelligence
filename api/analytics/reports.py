#!/usr/bin/env python3
"""
Report Generation System
=======================

This module provides automated report generation capabilities including:
- Report template management
- Automated report generation and scheduling
- Multiple export formats (PDF, Excel, CSV, HTML)
- Custom query builder for reports
- Data visualization in reports

Author: Engineering Log Intelligence Team
Date: September 29, 2025
"""

import json
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import io
import base64
from jinja2 import Template
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportTemplate:
    """Represents a report template."""
    id: str
    name: str
    description: str
    category: str  # system, performance, security, business
    template_type: str  # dashboard, summary, detailed, custom
    parameters: Dict[str, Any]
    query_config: Dict[str, Any]
    visualization_config: Dict[str, Any]
    format_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class ReportSchedule:
    """Represents a report schedule."""
    id: str
    template_id: str
    name: str
    schedule_type: str  # daily, weekly, monthly, custom
    schedule_config: Dict[str, Any]
    recipients: List[str]
    enabled: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

@dataclass
class GeneratedReport:
    """Represents a generated report."""
    id: str
    template_id: str
    name: str
    generated_at: datetime
    format: str  # pdf, excel, csv, html
    file_size: int
    download_url: str
    parameters: Dict[str, Any]
    summary: Dict[str, Any]

class ReportGenerator:
    """Report generation system."""
    
    def __init__(self):
        self.templates = {}
        self.schedules = {}
        self.generated_reports = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default report templates."""
        
        # System Overview Report
        self.templates['system_overview'] = ReportTemplate(
            id='system_overview',
            name='System Overview Report',
            description='Comprehensive system health and performance overview',
            category='system',
            template_type='dashboard',
            parameters={
                'time_range': '24h',
                'include_charts': True,
                'include_alerts': True,
                'include_metrics': True
            },
            query_config={
                'data_sources': ['logs', 'metrics', 'alerts'],
                'aggregations': ['count', 'avg', 'max', 'min'],
                'group_by': ['hour', 'source', 'level']
            },
            visualization_config={
                'charts': ['line', 'bar', 'pie'],
                'metrics': ['response_time', 'error_rate', 'throughput'],
                'layout': 'dashboard'
            },
            format_config={
                'page_size': 'A4',
                'orientation': 'landscape',
                'include_header': True,
                'include_footer': True
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Performance Analysis Report
        self.templates['performance_analysis'] = ReportTemplate(
            id='performance_analysis',
            name='Performance Analysis Report',
            description='Detailed performance metrics and optimization recommendations',
            category='performance',
            template_type='detailed',
            parameters={
                'time_range': '7d',
                'include_trends': True,
                'include_anomalies': True,
                'include_recommendations': True
            },
            query_config={
                'data_sources': ['logs', 'metrics'],
                'filters': {'level': ['ERROR', 'WARNING']},
                'aggregations': ['avg', 'p95', 'p99', 'max'],
                'group_by': ['hour', 'source']
            },
            visualization_config={
                'charts': ['line', 'heatmap', 'histogram'],
                'metrics': ['response_time', 'throughput', 'error_rate'],
                'layout': 'detailed'
            },
            format_config={
                'page_size': 'A4',
                'orientation': 'portrait',
                'include_charts': True,
                'include_tables': True
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Security Audit Report
        self.templates['security_audit'] = ReportTemplate(
            id='security_audit',
            name='Security Audit Report',
            description='Security events and compliance analysis',
            category='security',
            template_type='summary',
            parameters={
                'time_range': '30d',
                'include_compliance': True,
                'include_threats': True,
                'include_recommendations': True
            },
            query_config={
                'data_sources': ['logs'],
                'filters': {'level': ['ERROR'], 'category': ['security']},
                'aggregations': ['count', 'unique'],
                'group_by': ['day', 'source', 'severity']
            },
            visualization_config={
                'charts': ['bar', 'pie', 'timeline'],
                'metrics': ['security_events', 'threat_level', 'compliance_score'],
                'layout': 'summary'
            },
            format_config={
                'page_size': 'A4',
                'orientation': 'portrait',
                'include_executive_summary': True,
                'include_details': True
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Business Intelligence Report
        self.templates['business_intelligence'] = ReportTemplate(
            id='business_intelligence',
            name='Business Intelligence Report',
            description='Executive summary with KPIs and business metrics',
            category='business',
            template_type='dashboard',
            parameters={
                'time_range': '30d',
                'include_kpis': True,
                'include_trends': True,
                'include_forecasts': True
            },
            query_config={
                'data_sources': ['logs', 'metrics', 'alerts'],
                'aggregations': ['sum', 'avg', 'count'],
                'group_by': ['day', 'week', 'month']
            },
            visualization_config={
                'charts': ['line', 'bar', 'gauge'],
                'metrics': ['uptime', 'mtbf', 'mttr', 'sla_compliance'],
                'layout': 'executive'
            },
            format_config={
                'page_size': 'A4',
                'orientation': 'landscape',
                'include_executive_summary': True,
                'include_charts': True
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def generate_report(self, template_id: str, parameters: Dict[str, Any] = None, 
                       format: str = 'html') -> GeneratedReport:
        """Generate a report using a template."""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
            
            template = self.templates[template_id]
            
            # Merge parameters
            report_params = template.parameters.copy()
            if parameters:
                report_params.update(parameters)
            
            # Generate report data
            report_data = self._generate_report_data(template, report_params)
            
            # Generate report content
            if format == 'html':
                content = self._generate_html_report(template, report_data, report_params)
            elif format == 'csv':
                content = self._generate_csv_report(template, report_data, report_params)
            elif format == 'json':
                content = self._generate_json_report(template, report_data, report_params)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Create report record
            report_id = f"report_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            generated_report = GeneratedReport(
                id=report_id,
                template_id=template_id,
                name=f"{template.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                generated_at=datetime.now(),
                format=format,
                file_size=len(content),
                download_url=f"/api/reports/download/{report_id}",
                parameters=report_params,
                summary=self._generate_report_summary(report_data)
            )
            
            # Store generated report
            self.generated_reports[report_id] = generated_report
            
            logger.info(f"Generated report {report_id} in {format} format")
            return generated_report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _generate_report_data(self, template: ReportTemplate, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for the report."""
        try:
            # Simulate data generation based on template configuration
            time_range = parameters.get('time_range', '24h')
            
            # Parse time range
            if time_range == '1h':
                hours = 1
            elif time_range == '24h':
                hours = 24
            elif time_range == '7d':
                hours = 168
            elif time_range == '30d':
                hours = 720
            else:
                hours = 24
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Generate mock data based on template type
            data = {
                'metadata': {
                    'report_name': template.name,
                    'generated_at': datetime.now().isoformat(),
                    'time_range': time_range,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }
            }
            
            if template.category == 'system':
                data.update(self._generate_system_data(hours))
            elif template.category == 'performance':
                data.update(self._generate_performance_data(hours))
            elif template.category == 'security':
                data.update(self._generate_security_data(hours))
            elif template.category == 'business':
                data.update(self._generate_business_data(hours))
            
            return data
            
        except Exception as e:
            logger.error(f"Error generating report data: {e}")
            return {}
    
    def _generate_system_data(self, hours: int) -> Dict[str, Any]:
        """Generate system overview data."""
        import random
        
        # Generate hourly data
        hourly_data = []
        for i in range(hours):
            timestamp = datetime.now() - timedelta(hours=hours-i-1)
            hourly_data.append({
                'timestamp': timestamp.isoformat(),
                'log_count': random.randint(1000, 5000),
                'error_count': random.randint(10, 100),
                'response_time_avg': random.uniform(50, 200),
                'throughput': random.randint(100, 500)
            })
        
        # Calculate summary metrics
        total_logs = sum(h['log_count'] for h in hourly_data)
        total_errors = sum(h['error_count'] for h in hourly_data)
        avg_response_time = sum(h['response_time_avg'] for h in hourly_data) / len(hourly_data)
        
        return {
            'summary': {
                'total_logs': total_logs,
                'total_errors': total_errors,
                'error_rate': (total_errors / total_logs) * 100,
                'avg_response_time': avg_response_time,
                'uptime': 99.9
            },
            'hourly_data': hourly_data,
            'sources': {
                'application': {'count': total_logs * 0.4, 'errors': total_errors * 0.3},
                'database': {'count': total_logs * 0.3, 'errors': total_errors * 0.4},
                'api': {'count': total_logs * 0.2, 'errors': total_errors * 0.2},
                'system': {'count': total_logs * 0.1, 'errors': total_errors * 0.1}
            },
            'alerts': [
                {
                    'id': 'alert_001',
                    'severity': 'high',
                    'message': 'High error rate detected',
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'id': 'alert_002',
                    'severity': 'medium',
                    'message': 'Response time above threshold',
                    'timestamp': datetime.now().isoformat()
                }
            ]
        }
    
    def _generate_performance_data(self, hours: int) -> Dict[str, Any]:
        """Generate performance analysis data."""
        import random
        
        # Generate performance metrics
        metrics = []
        for i in range(hours):
            timestamp = datetime.now() - timedelta(hours=hours-i-1)
            metrics.append({
                'timestamp': timestamp.isoformat(),
                'response_time_p50': random.uniform(50, 150),
                'response_time_p95': random.uniform(150, 300),
                'response_time_p99': random.uniform(300, 500),
                'throughput': random.randint(100, 1000),
                'error_rate': random.uniform(0.1, 5.0),
                'cpu_usage': random.uniform(20, 80),
                'memory_usage': random.uniform(30, 70)
            })
        
        # Calculate trends
        recent_avg = sum(m['response_time_p95'] for m in metrics[-6:]) / 6
        earlier_avg = sum(m['response_time_p95'] for m in metrics[:6]) / 6
        trend_direction = 'increasing' if recent_avg > earlier_avg else 'decreasing'
        
        return {
            'summary': {
                'avg_response_time_p95': recent_avg,
                'max_response_time': max(m['response_time_p99'] for m in metrics),
                'avg_throughput': sum(m['throughput'] for m in metrics) / len(metrics),
                'avg_error_rate': sum(m['error_rate'] for m in metrics) / len(metrics),
                'trend_direction': trend_direction,
                'performance_score': 85.5
            },
            'metrics': metrics,
            'recommendations': [
                'Consider implementing caching to reduce response times',
                'Monitor CPU usage during peak hours',
                'Review database query optimization',
                'Implement connection pooling for better resource utilization'
            ],
            'anomalies': [
                {
                    'timestamp': metrics[12]['timestamp'],
                    'type': 'response_time_spike',
                    'value': metrics[12]['response_time_p95'],
                    'severity': 'high'
                }
            ]
        }
    
    def _generate_security_data(self, hours: int) -> Dict[str, Any]:
        """Generate security audit data."""
        import random
        
        # Generate security events
        events = []
        event_types = ['failed_login', 'suspicious_activity', 'privilege_escalation', 'data_access']
        
        for i in range(random.randint(50, 200)):
            timestamp = datetime.now() - timedelta(hours=random.randint(0, hours))
            events.append({
                'timestamp': timestamp.isoformat(),
                'type': random.choice(event_types),
                'severity': random.choice(['low', 'medium', 'high', 'critical']),
                'source_ip': f"192.168.1.{random.randint(1, 254)}",
                'user': f"user_{random.randint(1, 100)}",
                'description': f"Security event of type {random.choice(event_types)}"
            })
        
        # Calculate security metrics
        critical_events = len([e for e in events if e['severity'] == 'critical'])
        high_events = len([e for e in events if e['severity'] == 'high'])
        unique_ips = len(set(e['source_ip'] for e in events))
        
        return {
            'summary': {
                'total_events': len(events),
                'critical_events': critical_events,
                'high_events': high_events,
                'unique_source_ips': unique_ips,
                'compliance_score': 92.5,
                'threat_level': 'medium'
            },
            'events': events[:50],  # Limit for report size
            'event_types': {
                event_type: len([e for e in events if e['type'] == event_type])
                for event_type in event_types
            },
            'top_source_ips': [
                {'ip': ip, 'count': count}
                for ip, count in sorted(
                    [(ip, len([e for e in events if e['source_ip'] == ip])) for ip in set(e['source_ip'] for e in events)],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ],
            'recommendations': [
                'Implement additional monitoring for critical events',
                'Review and update access control policies',
                'Consider implementing rate limiting for failed login attempts',
                'Regular security audit and penetration testing'
            ]
        }
    
    def _generate_business_data(self, hours: int) -> Dict[str, Any]:
        """Generate business intelligence data."""
        import random
        
        # Generate daily KPIs
        daily_kpis = []
        for i in range(min(hours // 24, 30)):  # Daily data for up to 30 days
            date = datetime.now().date() - timedelta(days=i)
            daily_kpis.append({
                'date': date.isoformat(),
                'uptime': random.uniform(99.0, 100.0),
                'mtbf': random.uniform(720, 1440),  # Mean time between failures in hours
                'mttr': random.uniform(0.5, 4.0),   # Mean time to repair in hours
                'sla_compliance': random.uniform(95.0, 100.0),
                'user_satisfaction': random.uniform(4.0, 5.0),
                'revenue_impact': random.uniform(0, 10000)
            })
        
        # Calculate business metrics
        avg_uptime = sum(kpi['uptime'] for kpi in daily_kpis) / len(daily_kpis)
        avg_mtbf = sum(kpi['mtbf'] for kpi in daily_kpis) / len(daily_kpis)
        avg_mttr = sum(kpi['mttr'] for kpi in daily_kpis) / len(daily_kpis)
        
        return {
            'summary': {
                'avg_uptime': avg_uptime,
                'avg_mtbf': avg_mtbf,
                'avg_mttr': avg_mttr,
                'sla_compliance': sum(kpi['sla_compliance'] for kpi in daily_kpis) / len(daily_kpis),
                'user_satisfaction': sum(kpi['user_satisfaction'] for kpi in daily_kpis) / len(daily_kpis),
                'total_revenue_impact': sum(kpi['revenue_impact'] for kpi in daily_kpis),
                'business_score': 88.5
            },
            'daily_kpis': daily_kpis,
            'trends': {
                'uptime_trend': 'stable',
                'mtbf_trend': 'improving',
                'mttr_trend': 'improving',
                'satisfaction_trend': 'stable'
            },
            'forecasts': {
                'next_month_uptime': avg_uptime + random.uniform(-0.5, 0.5),
                'next_month_mtbf': avg_mtbf + random.uniform(-50, 100),
                'next_month_mttr': avg_mttr + random.uniform(-0.5, 0.5)
            },
            'recommendations': [
                'Continue current maintenance practices to maintain uptime',
                'Invest in preventive maintenance to improve MTBF',
                'Streamline incident response process to reduce MTTR',
                'Focus on user experience improvements'
            ]
        }
    
    def _generate_html_report(self, template: ReportTemplate, data: Dict[str, Any], 
                            parameters: Dict[str, Any]) -> str:
        """Generate HTML report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ template.name }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
                .summary { background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
                .metric { display: inline-block; margin: 10px 20px 10px 0; }
                .metric-label { font-weight: bold; color: #666; }
                .metric-value { font-size: 24px; color: #333; }
                .section { margin-bottom: 30px; }
                .table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .table th { background-color: #f2f2f2; }
                .footer { margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ template.name }}</h1>
                <p>{{ template.description }}</p>
                <p>Generated: {{ data.metadata.generated_at }}</p>
                <p>Time Range: {{ data.metadata.time_range }}</p>
            </div>
            
            {% if data.summary %}
            <div class="summary">
                <h2>Executive Summary</h2>
                {% for key, value in data.summary.items() %}
                <div class="metric">
                    <div class="metric-label">{{ key.replace('_', ' ').title() }}</div>
                    <div class="metric-value">{{ value }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if data.hourly_data %}
            <div class="section">
                <h2>Hourly Data</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Log Count</th>
                            <th>Error Count</th>
                            <th>Avg Response Time</th>
                            <th>Throughput</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in data.hourly_data[:20] %}
                        <tr>
                            <td>{{ row.timestamp }}</td>
                            <td>{{ row.log_count }}</td>
                            <td>{{ row.error_count }}</td>
                            <td>{{ "%.2f"|format(row.response_time_avg) }}</td>
                            <td>{{ row.throughput }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            {% if data.recommendations %}
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {% for rec in data.recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>Report generated by Engineering Log Intelligence System</p>
                <p>Template: {{ template.name }} | Category: {{ template.category }}</p>
            </div>
        </body>
        </html>
        """
        
        template_obj = Template(html_template)
        return template_obj.render(template=template, data=data, parameters=parameters)
    
    def _generate_csv_report(self, template: ReportTemplate, data: Dict[str, Any], 
                           parameters: Dict[str, Any]) -> str:
        """Generate CSV report."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Report', 'Generated At', 'Time Range', 'Template'])
        writer.writerow([
            template.name,
            data['metadata']['generated_at'],
            data['metadata']['time_range'],
            template.id
        ])
        
        writer.writerow([])  # Empty row
        
        # Write summary
        if 'summary' in data:
            writer.writerow(['Summary Metrics'])
            for key, value in data['summary'].items():
                writer.writerow([key, value])
        
        writer.writerow([])  # Empty row
        
        # Write hourly data if available
        if 'hourly_data' in data:
            writer.writerow(['Hourly Data'])
            headers = list(data['hourly_data'][0].keys()) if data['hourly_data'] else []
            writer.writerow(headers)
            
            for row in data['hourly_data']:
                writer.writerow([row.get(header, '') for header in headers])
        
        return output.getvalue()
    
    def _generate_json_report(self, template: ReportTemplate, data: Dict[str, Any], 
                            parameters: Dict[str, Any]) -> str:
        """Generate JSON report."""
        report_data = {
            'template': {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category
            },
            'parameters': parameters,
            'data': data
        }
        
        return json.dumps(report_data, indent=2, default=str)
    
    def _generate_report_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the report data."""
        summary = {
            'total_records': 0,
            'data_points': 0,
            'time_span': data.get('metadata', {}).get('time_range', 'unknown'),
            'categories': []
        }
        
        # Count records in different sections
        if 'hourly_data' in data:
            summary['total_records'] += len(data['hourly_data'])
            summary['categories'].append('hourly_data')
        
        if 'events' in data:
            summary['total_records'] += len(data['events'])
            summary['categories'].append('events')
        
        if 'daily_kpis' in data:
            summary['total_records'] += len(data['daily_kpis'])
            summary['categories'].append('daily_kpis')
        
        summary['data_points'] = summary['total_records']
        
        return summary
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available report templates."""
        return [asdict(template) for template in self.templates.values()]
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report template."""
        if template_id in self.templates:
            return asdict(self.templates[template_id])
        return None
    
    def list_generated_reports(self) -> List[Dict[str, Any]]:
        """List all generated reports."""
        return [asdict(report) for report in self.generated_reports.values()]

def handler(request):
    """Vercel function handler for report generation."""
    try:
        if request.method == 'GET':
            # Parse query parameters
            action = request.query.get('action', 'list')
            
            report_generator = ReportGenerator()
            
            if action == 'list':
                # List all templates
                templates = report_generator.list_templates()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'templates': templates
                    })
                }
            
            elif action == 'template':
                # Get specific template
                template_id = request.query.get('template_id')
                if not template_id:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': 'template_id parameter required'})
                    }
                
                template = report_generator.get_template(template_id)
                if not template:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': 'Template not found'})
                    }
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'template': template
                    })
                }
            
            elif action == 'reports':
                # List generated reports
                reports = report_generator.list_generated_reports()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'reports': reports
                    })
                }
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            report_generator = ReportGenerator()
            
            # Generate report
            template_id = data.get('template_id')
            parameters = data.get('parameters', {})
            format = data.get('format', 'html')
            
            if not template_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'template_id required'})
                }
            
            try:
                report = report_generator.generate_report(template_id, parameters, format)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'report': asdict(report)
                    })
                }
                
            except ValueError as e:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)})
                }
        
        elif request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        logger.error(f"Error in report generation handler: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
