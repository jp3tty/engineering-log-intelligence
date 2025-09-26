"""
Enhanced Alerting System for Engineering Log Intelligence.

This module provides comprehensive alerting capabilities including:
- Multi-channel alerting (Email, Slack, Webhook)
- Alert correlation and deduplication
- Integration with incident response system
- Alert lifecycle management
- Notification templates and routing
"""

import json
import uuid
import smtplib
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NotificationTemplate:
    """Template for notifications."""
    name: str
    channel: str  # email, slack, webhook
    subject_template: str
    body_template: str
    variables: List[str] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []


@dataclass
class AlertRule:
    """Defines alert rules for automatic alert generation."""
    id: str
    name: str
    description: str
    condition: str  # SQL-like condition or expression
    severity: str  # low, medium, high, critical
    category: str  # system, security, performance, business
    enabled: bool = True
    cooldown_minutes: int = 15
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ['email', 'slack']


class NotificationService:
    """Handles sending notifications through various channels."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.config = self._load_notification_config()
    
    def _initialize_templates(self) -> Dict[str, NotificationTemplate]:
        """Initialize notification templates."""
        return {
            'critical_alert_email': NotificationTemplate(
                name='critical_alert_email',
                channel='email',
                subject_template='🚨 CRITICAL ALERT: {title}',
                body_template='''
                <h2>Critical Alert Detected</h2>
                <p><strong>Title:</strong> {title}</p>
                <p><strong>Description:</strong> {description}</p>
                <p><strong>Severity:</strong> {severity}</p>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Source:</strong> {source}</p>
                <p><strong>Time:</strong> {timestamp}</p>
                <p><strong>Alert ID:</strong> {alert_id}</p>
                
                <h3>Recommended Actions:</h3>
                <ul>
                    <li>Check system status immediately</li>
                    <li>Review related logs</li>
                    <li>Escalate if necessary</li>
                </ul>
                
                <p><a href="{dashboard_url}">View in Dashboard</a></p>
                ''',
                variables=['title', 'description', 'severity', 'category', 'source', 'timestamp', 'alert_id', 'dashboard_url']
            ),
            
            'high_alert_slack': NotificationTemplate(
                name='high_alert_slack',
                channel='slack',
                subject_template='',
                body_template='''
                🔴 *HIGH PRIORITY ALERT*
                
                *Title:* {title}
                *Description:* {description}
                *Severity:* {severity}
                *Category:* {category}
                *Time:* {timestamp}
                *Alert ID:* {alert_id}
                
                <{dashboard_url}|View in Dashboard>
                ''',
                variables=['title', 'description', 'severity', 'category', 'timestamp', 'alert_id', 'dashboard_url']
            ),
            
            'incident_created': NotificationTemplate(
                name='incident_created',
                channel='slack',
                subject_template='',
                body_template='''
                🚨 *NEW INCIDENT CREATED*
                
                *Incident ID:* {incident_id}
                *Title:* {title}
                *Severity:* {severity}
                *Assigned Team:* {assigned_team}
                *Created:* {timestamp}
                
                <{dashboard_url}|View Incident>
                ''',
                variables=['incident_id', 'title', 'severity', 'assigned_team', 'timestamp', 'dashboard_url']
            ),
            
            'escalation_notification': NotificationTemplate(
                name='escalation_notification',
                channel='email',
                subject_template='⚠️ ESCALATION: {incident_title}',
                body_template='''
                <h2>Incident Escalated</h2>
                <p>The following incident has been escalated and requires your attention:</p>
                
                <p><strong>Incident ID:</strong> {incident_id}</p>
                <p><strong>Title:</strong> {incident_title}</p>
                <p><strong>Severity:</strong> {severity}</p>
                <p><strong>Escalation Level:</strong> {escalation_level}</p>
                <p><strong>Escalated To:</strong> {escalated_to}</p>
                <p><strong>Reason:</strong> {escalation_reason}</p>
                <p><strong>Time:</strong> {timestamp}</p>
                
                <h3>Immediate Actions Required:</h3>
                <ul>
                    <li>Acknowledge the incident</li>
                    <li>Assess the situation</li>
                    <li>Begin resolution process</li>
                    <li>Update incident status</li>
                </ul>
                
                <p><a href="{dashboard_url}">View Incident</a></p>
                ''',
                variables=['incident_id', 'incident_title', 'severity', 'escalation_level', 'escalated_to', 'escalation_reason', 'timestamp', 'dashboard_url']
            )
        }
    
    def _load_notification_config(self) -> Dict[str, Any]:
        """Load notification configuration."""
        return {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'alerts@engineeringlogintelligence.com',
                'password': 'your-app-password',
                'from_address': 'alerts@engineeringlogintelligence.com'
            },
            'slack': {
                'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
                'channel': '#alerts',
                'username': 'Log Intelligence Bot',
                'icon_emoji': ':robot_face:'
            },
            'webhook': {
                'url': 'https://your-webhook-endpoint.com/alerts',
                'timeout': 30,
                'retry_attempts': 3
            }
        }
    
    def send_notification(self, template_name: str, data: Dict[str, Any], recipients: List[str] = None) -> Dict[str, Any]:
        """Send notification using specified template."""
        try:
            if template_name not in self.templates:
                raise ValueError(f"Template {template_name} not found")
            
            template = self.templates[template_name]
            
            # Render template
            rendered = self._render_template(template, data)
            
            # Send based on channel
            if template.channel == 'email':
                return self._send_email(rendered, recipients or self._get_default_email_recipients())
            elif template.channel == 'slack':
                return self._send_slack(rendered)
            elif template.channel == 'webhook':
                return self._send_webhook(rendered, data.get('webhook_url'))
            else:
                raise ValueError(f"Unsupported channel: {template.channel}")
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {
                'success': False,
                'error': str(e),
                'template': template_name,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _render_template(self, template: NotificationTemplate, data: Dict[str, Any]) -> Dict[str, str]:
        """Render template with data."""
        rendered = {}
        
        # Render subject
        if template.subject_template:
            rendered['subject'] = template.subject_template.format(**data)
        
        # Render body
        rendered['body'] = template.body_template.format(**data)
        
        return rendered
    
    def _send_email(self, rendered: Dict[str, str], recipients: List[str]) -> Dict[str, Any]:
        """Send email notification."""
        try:
            # For demo purposes, simulate email sending
            logger.info(f"Email sent to {recipients}: {rendered.get('subject', 'No Subject')}")
            
            return {
                'success': True,
                'channel': 'email',
                'recipients': recipients,
                'subject': rendered.get('subject'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e),
                'channel': 'email',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _send_slack(self, rendered: Dict[str, str]) -> Dict[str, Any]:
        """Send Slack notification."""
        try:
            # For demo purposes, simulate Slack sending
            logger.info(f"Slack message sent: {rendered['body'][:100]}...")
            
            return {
                'success': True,
                'channel': 'slack',
                'message_preview': rendered['body'][:100],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return {
                'success': False,
                'error': str(e),
                'channel': 'slack',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _send_webhook(self, rendered: Dict[str, str], webhook_url: str = None) -> Dict[str, Any]:
        """Send webhook notification."""
        try:
            webhook_url = webhook_url or self.config['webhook']['url']
            
            # For demo purposes, simulate webhook sending
            logger.info(f"Webhook sent to {webhook_url}")
            
            return {
                'success': True,
                'channel': 'webhook',
                'webhook_url': webhook_url,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            return {
                'success': False,
                'error': str(e),
                'channel': 'webhook',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _get_default_email_recipients(self) -> List[str]:
        """Get default email recipients."""
        return [
            'oncall@engineeringlogintelligence.com',
            'alerts@engineeringlogintelligence.com'
        ]


class AlertCorrelationEngine:
    """Handles alert correlation and deduplication."""
    
    def __init__(self):
        self.active_alerts = {}  # correlation_id -> alert
        self.correlation_window_minutes = 10
    
    def correlate_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate alert with existing alerts."""
        correlation_id = alert_data.get('correlation_id')
        
        if not correlation_id:
            return {
                'action': 'create_new',
                'reason': 'No correlation ID provided',
                'correlation_id': None
            }
        
        # Check for existing alerts within correlation window
        existing_alert = self.active_alerts.get(correlation_id)
        
        if existing_alert:
            time_diff = datetime.now(timezone.utc) - existing_alert['created_at']
            if time_diff.total_seconds() / 60 <= self.correlation_window_minutes:
                return {
                    'action': 'update_existing',
                    'reason': 'Alert correlated with existing alert',
                    'existing_alert_id': existing_alert['alert_id'],
                    'correlation_id': correlation_id
                }
        
        # Create new alert
        self.active_alerts[correlation_id] = {
            'alert_id': alert_data.get('alert_id'),
            'created_at': datetime.now(timezone.utc),
            'severity': alert_data.get('severity'),
            'category': alert_data.get('category')
        }
        
        return {
            'action': 'create_new',
            'reason': 'New alert created',
            'correlation_id': correlation_id
        }
    
    def cleanup_old_alerts(self):
        """Clean up old alerts from correlation cache."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=self.correlation_window_minutes * 2)
        
        to_remove = []
        for correlation_id, alert_data in self.active_alerts.items():
            if alert_data['created_at'] < cutoff_time:
                to_remove.append(correlation_id)
        
        for correlation_id in to_remove:
            del self.active_alerts[correlation_id]


class AlertingSystem:
    """Main alerting system."""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.correlation_engine = AlertCorrelationEngine()
        self.alert_rules = self._initialize_alert_rules()
    
    def _initialize_alert_rules(self) -> List[AlertRule]:
        """Initialize alert rules."""
        return [
            AlertRule(
                id='high_error_rate',
                name='High Error Rate',
                description='Alert when error rate exceeds 10%',
                condition="error_rate > 0.1",
                severity='high',
                category='performance',
                cooldown_minutes=15,
                notification_channels=['email', 'slack']
            ),
            
            AlertRule(
                id='database_connection_failure',
                name='Database Connection Failure',
                description='Alert when database connections fail',
                condition="error_type == 'database_connection_failure'",
                severity='critical',
                category='system',
                cooldown_minutes=5,
                notification_channels=['email', 'slack', 'webhook']
            ),
            
            AlertRule(
                id='security_incident',
                name='Security Incident',
                description='Alert on potential security incidents',
                condition="category == 'security' AND severity == 'critical'",
                severity='critical',
                category='security',
                cooldown_minutes=0,
                notification_channels=['email', 'slack', 'webhook']
            ),
            
            AlertRule(
                id='slow_response_time',
                name='Slow Response Time',
                description='Alert when response times are slow',
                condition="response_time_ms > 5000",
                severity='medium',
                category='performance',
                cooldown_minutes=30,
                notification_channels=['email']
            )
        ]
    
    def process_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an alert through the alerting system."""
        try:
            # Correlate alert
            correlation_result = self.correlation_engine.correlate_alert(alert_data)
            
            # Generate alert ID if not provided
            if 'alert_id' not in alert_data:
                alert_data['alert_id'] = str(uuid.uuid4())
            
            # Add timestamp
            alert_data['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            # Determine notification channels based on severity and category
            notification_channels = self._determine_notification_channels(alert_data)
            
            # Send notifications
            notification_results = []
            for channel in notification_channels:
                template_name = self._get_template_name(alert_data, channel)
                result = self.notification_service.send_notification(
                    template_name, 
                    alert_data, 
                    self._get_channel_recipients(channel)
                )
                notification_results.append(result)
            
            # Clean up old correlations
            self.correlation_engine.cleanup_old_alerts()
            
            return {
                'success': True,
                'alert_id': alert_data['alert_id'],
                'correlation_result': correlation_result,
                'notifications_sent': notification_results,
                'timestamp': alert_data['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _determine_notification_channels(self, alert_data: Dict[str, Any]) -> List[str]:
        """Determine notification channels based on alert characteristics."""
        severity = alert_data.get('severity', 'medium')
        category = alert_data.get('category', 'system')
        
        if severity == 'critical' or category == 'security':
            return ['email', 'slack', 'webhook']
        elif severity == 'high':
            return ['email', 'slack']
        elif severity == 'medium':
            return ['email']
        else:
            return ['email']
    
    def _get_template_name(self, alert_data: Dict[str, Any], channel: str) -> str:
        """Get appropriate template name for alert and channel."""
        severity = alert_data.get('severity', 'medium')
        
        if severity == 'critical' and channel == 'email':
            return 'critical_alert_email'
        elif severity in ['high', 'critical'] and channel == 'slack':
            return 'high_alert_slack'
        else:
            return 'critical_alert_email'  # Default template
    
    def _get_channel_recipients(self, channel: str) -> List[str]:
        """Get recipients for notification channel."""
        if channel == 'email':
            return self.notification_service._get_default_email_recipients()
        return []


def handler(event, context):
    """Main Vercel function handler for alerting."""
    try:
        # Parse request
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        body = event.get('body', '{}')
        
        # Initialize alerting system
        alerting_system = AlertingSystem()
        
        # Route requests
        if method == 'GET':
            if path == '/api/alerting':
                return get_alerts(event, context)
            elif path == '/api/alerting/rules':
                return get_alert_rules(event, context)
            elif path == '/api/alerting/templates':
                return get_notification_templates(event, context)
        
        elif method == 'POST':
            if path == '/api/alerting/send':
                return send_alert(event, context)
            elif path == '/api/alerting/test':
                return test_alert(event, context)
            elif path == '/api/alerting/bulk':
                return send_bulk_alerts(event, context)
        
        elif method == 'PUT':
            if path == '/api/alerting/rules':
                return update_alert_rules(event, context)
        
        # Default response
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'error': 'Endpoint not found',
                'available_endpoints': [
                    'GET /api/alerting',
                    'POST /api/alerting/send',
                    'GET /api/alerting/rules',
                    'GET /api/alerting/templates'
                ]
            })
        }
        
    except Exception as e:
        logger.error(f"Error in alerting handler: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def send_alert(event, context):
    """Send an alert."""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Validate required fields
        required_fields = ['title', 'description', 'severity', 'category']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Process alert
        alerting_system = AlertingSystem()
        result = alerting_system.process_alert(body)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Alert processed successfully',
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error sending alert: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to send alert'})
        }


def test_alert(event, context):
    """Test alert system with sample data."""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Default test alert if none provided
        test_alert_data = {
            'title': 'Test Alert - System Check',
            'description': 'This is a test alert to verify the alerting system is working correctly',
            'severity': 'medium',
            'category': 'system',
            'source': 'test',
            'correlation_id': f'test-{uuid.uuid4().hex[:8]}'
        }
        
        # Override with provided data
        test_alert_data.update(body)
        
        # Process test alert
        alerting_system = AlertingSystem()
        result = alerting_system.process_alert(test_alert_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Test alert sent successfully',
                'test_alert': test_alert_data,
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error testing alert: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to test alert'})
        }


def get_alerts(event, context):
    """Get alerts with optional filtering."""
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        
        # Mock alerts data
        alerts = [
            {
                'id': 1,
                'alert_id': 'alert-001',
                'title': 'Database Connection Failure',
                'description': 'Multiple database connection timeouts detected',
                'severity': 'critical',
                'category': 'system',
                'source': 'monitoring',
                'status': 'open',
                'correlation_id': 'corr-001',
                'triggered_at': (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                'created_at': (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 2,
                'alert_id': 'alert-002',
                'title': 'High Error Rate',
                'description': 'Application error rate increased to 12%',
                'severity': 'high',
                'category': 'performance',
                'source': 'monitoring',
                'status': 'acknowledged',
                'correlation_id': 'corr-002',
                'triggered_at': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                'acknowledged_at': (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                'created_at': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        if query_params.get('severity'):
            alerts = [a for a in alerts if a['severity'] == query_params['severity']]
        
        if query_params.get('status'):
            alerts = [a for a in alerts if a['status'] == query_params['status']]
        
        if query_params.get('category'):
            alerts = [a for a in alerts if a['category'] == query_params['category']]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'alerts': alerts,
                'total': len(alerts),
                'filters_applied': query_params
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to get alerts'})
        }


def get_alert_rules(event, context):
    """Get alert rules."""
    try:
        alerting_system = AlertingSystem()
        
        rules = []
        for rule in alerting_system.alert_rules:
            rules.append({
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'condition': rule.condition,
                'severity': rule.severity,
                'category': rule.category,
                'enabled': rule.enabled,
                'cooldown_minutes': rule.cooldown_minutes,
                'notification_channels': rule.notification_channels
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'alert_rules': rules,
                'total': len(rules)
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting alert rules: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to get alert rules'})
        }


def get_notification_templates(event, context):
    """Get notification templates."""
    try:
        notification_service = NotificationService()
        
        templates = []
        for name, template in notification_service.templates.items():
            templates.append({
                'name': template.name,
                'channel': template.channel,
                'subject_template': template.subject_template,
                'body_template': template.body_template[:200] + '...' if len(template.body_template) > 200 else template.body_template,
                'variables': template.variables
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'templates': templates,
                'total': len(templates)
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting notification templates: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to get notification templates'})
        }


def send_bulk_alerts(event, context):
    """Send multiple alerts in bulk."""
    try:
        body = json.loads(event.get('body', '{}'))
        
        alerts = body.get('alerts', [])
        if not alerts:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No alerts provided'})
            }
        
        alerting_system = AlertingSystem()
        results = []
        
        for alert_data in alerts:
            result = alerting_system.process_alert(alert_data)
            results.append(result)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Processed {len(alerts)} alerts',
                'results': results,
                'summary': {
                    'total': len(alerts),
                    'successful': len([r for r in results if r.get('success', False)]),
                    'failed': len([r for r in results if not r.get('success', False)])
                }
            })
        }
        
    except Exception as e:
        logger.error(f"Error sending bulk alerts: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to send bulk alerts'})
        }


def update_alert_rules(event, context):
    """Update alert rules."""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Mock update
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Alert rules updated successfully',
                'updated_rules': body.get('rules', [])
            })
        }
        
    except Exception as e:
        logger.error(f"Error updating alert rules: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to update alert rules'})
        }
