"""
Alerting system for Engineering Log Intelligence System.
Handles alert generation, notification, and escalation.
"""

import os
import json
import time
import smtplib
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass
from enum import Enum

class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class Alert:
    """Alert data structure."""
    id: str
    level: AlertLevel
    service: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    escalation_count: int = 0
    metadata: Dict[str, Any] = None

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = self._load_alert_rules()
        self.notification_config = self._load_notification_config()
        self.alert_cooldowns = {}  # Service -> last alert time
        
    def _load_alert_rules(self) -> Dict[str, Any]:
        """Load alert rules configuration."""
        return {
            "response_time": {
                "warning": 1.0,  # seconds
                "critical": 5.0,  # seconds
                "emergency": 10.0  # seconds
            },
            "error_rate": {
                "warning": 5.0,  # percentage
                "critical": 10.0,  # percentage
                "emergency": 20.0  # percentage
            },
            "memory_usage": {
                "warning": 80.0,  # percentage
                "critical": 90.0,  # percentage
                "emergency": 95.0  # percentage
            },
            "disk_usage": {
                "warning": 80.0,  # percentage
                "critical": 90.0,  # percentage
                "emergency": 95.0  # percentage
            },
            "service_down": {
                "critical": True
            }
        }
    
    def _load_notification_config(self) -> Dict[str, Any]:
        """Load notification configuration."""
        return {
            "email": {
                "enabled": bool(os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true"),
                "smtp_server": os.getenv("ALERT_SMTP_SERVER", ""),
                "smtp_port": int(os.getenv("ALERT_SMTP_PORT", "587")),
                "username": os.getenv("ALERT_EMAIL_USERNAME", ""),
                "password": os.getenv("ALERT_EMAIL_PASSWORD", ""),
                "from_email": os.getenv("ALERT_FROM_EMAIL", ""),
                "to_emails": os.getenv("ALERT_TO_EMAILS", "").split(",") if os.getenv("ALERT_TO_EMAILS") else []
            },
            "slack": {
                "enabled": bool(os.getenv("ALERT_SLACK_ENABLED", "false").lower() == "true"),
                "webhook_url": os.getenv("ALERT_SLACK_WEBHOOK", ""),
                "channel": os.getenv("ALERT_SLACK_CHANNEL", "#alerts")
            },
            "webhook": {
                "enabled": bool(os.getenv("ALERT_WEBHOOK_ENABLED", "false").lower() == "true"),
                "url": os.getenv("ALERT_WEBHOOK_URL", "")
            }
        }
    
    def create_alert(self, level: AlertLevel, service: str, message: str, metadata: Dict[str, Any] = None) -> Alert:
        """Create a new alert."""
        alert_id = f"{service}_{int(time.time())}_{level.value}"
        
        alert = Alert(
            id=alert_id,
            level=level,
            service=service,
            message=message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Check cooldown to avoid spam
        if self._should_send_alert(service, level):
            self.alerts.append(alert)
            self._send_notifications(alert)
            self.alert_cooldowns[service] = time.time()
        
        return alert
    
    def _should_send_alert(self, service: str, level: AlertLevel) -> bool:
        """Check if alert should be sent based on cooldown rules."""
        if level == AlertLevel.EMERGENCY:
            return True  # Always send emergency alerts
        
        last_alert_time = self.alert_cooldowns.get(service, 0)
        cooldown_period = 300  # 5 minutes for non-emergency alerts
        
        return time.time() - last_alert_time > cooldown_period
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert."""
        # Email notification
        if self.notification_config["email"]["enabled"]:
            self._send_email_alert(alert)
        
        # Slack notification
        if self.notification_config["slack"]["enabled"]:
            self._send_slack_alert(alert)
        
        # Webhook notification
        if self.notification_config["webhook"]["enabled"]:
            self._send_webhook_alert(alert)
    
    def _send_email_alert(self, alert: Alert):
        """Send email notification."""
        try:
            config = self.notification_config["email"]
            
            msg = MimeMultipart()
            msg['From'] = config["from_email"]
            msg['To'] = ", ".join(config["to_emails"])
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.service} Alert"
            
            body = f"""
            Alert Details:
            =============
            Service: {alert.service}
            Level: {alert.level.value.upper()}
            Message: {alert.message}
            Timestamp: {alert.timestamp.isoformat()}
            
            Metadata:
            {json.dumps(alert.metadata, indent=2) if alert.metadata else "None"}
            
            This is an automated alert from the Engineering Log Intelligence System.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, alert: Alert):
        """Send Slack notification."""
        try:
            config = self.notification_config["slack"]
            
            # Determine color based on alert level
            color_map = {
                AlertLevel.INFO: "#36a64f",
                AlertLevel.WARNING: "#ff9500",
                AlertLevel.CRITICAL: "#ff0000",
                AlertLevel.EMERGENCY: "#8b0000"
            }
            
            payload = {
                "channel": config["channel"],
                "attachments": [{
                    "color": color_map.get(alert.level, "#36a64f"),
                    "title": f"{alert.service} Alert - {alert.level.value.upper()}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Service", "value": alert.service, "short": True},
                        {"title": "Level", "value": alert.level.value.upper(), "short": True},
                        {"title": "Timestamp", "value": alert.timestamp.isoformat(), "short": False}
                    ],
                    "footer": "Engineering Log Intelligence System",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            response = requests.post(config["webhook_url"], json=payload, timeout=10)
            if response.status_code != 200:
                print(f"Failed to send Slack alert: {response.status_code}")
                
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def _send_webhook_alert(self, alert: Alert):
        """Send webhook notification."""
        try:
            config = self.notification_config["webhook"]
            
            payload = {
                "alert_id": alert.id,
                "level": alert.level.value,
                "service": alert.service,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata
            }
            
            response = requests.post(config["url"], json=payload, timeout=10)
            if response.status_code not in [200, 201]:
                print(f"Failed to send webhook alert: {response.status_code}")
                
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_alerts_by_service(self, service: str) -> List[Alert]:
        """Get alerts for a specific service."""
        return [alert for alert in self.alerts if alert.service == service]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts by severity level."""
        return [alert for alert in self.alerts if alert.level == level]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        resolved_alerts = total_alerts - active_alerts
        
        level_counts = {}
        for level in AlertLevel:
            level_counts[level.value] = len(self.get_alerts_by_level(level))
        
        service_counts = {}
        for alert in self.alerts:
            service_counts[alert.service] = service_counts.get(alert.service, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "level_breakdown": level_counts,
            "service_breakdown": service_counts,
            "resolution_rate": (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0
        }
    
    def check_service_health(self, service_data: Dict[str, Any]) -> List[Alert]:
        """Check service health and generate alerts if needed."""
        alerts = []
        service_name = service_data.get("service", "unknown")
        
        # Check response time
        response_time = service_data.get("response_time", 0)
        if response_time > self.alert_rules["response_time"]["emergency"]:
            alerts.append(self.create_alert(
                AlertLevel.EMERGENCY,
                service_name,
                f"Response time critical: {response_time:.2f}s",
                {"response_time": response_time}
            ))
        elif response_time > self.alert_rules["response_time"]["critical"]:
            alerts.append(self.create_alert(
                AlertLevel.CRITICAL,
                service_name,
                f"Response time high: {response_time:.2f}s",
                {"response_time": response_time}
            ))
        elif response_time > self.alert_rules["response_time"]["warning"]:
            alerts.append(self.create_alert(
                AlertLevel.WARNING,
                service_name,
                f"Response time elevated: {response_time:.2f}s",
                {"response_time": response_time}
            ))
        
        # Check error rate
        error_rate = service_data.get("error_rate", 0)
        if error_rate > self.alert_rules["error_rate"]["emergency"]:
            alerts.append(self.create_alert(
                AlertLevel.EMERGENCY,
                service_name,
                f"Error rate critical: {error_rate:.2f}%",
                {"error_rate": error_rate}
            ))
        elif error_rate > self.alert_rules["error_rate"]["critical"]:
            alerts.append(self.create_alert(
                AlertLevel.CRITICAL,
                service_name,
                f"Error rate high: {error_rate:.2f}%",
                {"error_rate": error_rate}
            ))
        elif error_rate > self.alert_rules["error_rate"]["warning"]:
            alerts.append(self.create_alert(
                AlertLevel.WARNING,
                service_name,
                f"Error rate elevated: {error_rate:.2f}%",
                {"error_rate": error_rate}
            ))
        
        # Check service status
        if service_data.get("status") == "unhealthy":
            alerts.append(self.create_alert(
                AlertLevel.CRITICAL,
                service_name,
                "Service is unhealthy",
                {"status": service_data.get("status")}
            ))
        
        return alerts


def handler(request) -> Dict[str, Any]:
    """
    Alerting handler for Vercel Functions.
    Manages alert creation, resolution, and notifications.
    """
    try:
        alert_manager = AlertManager()
        
        # Parse request
        method = request.get("httpMethod", "GET")
        body = request.get("body", "{}")
        query_params = request.get("queryStringParameters", {}) or {}
        
        if isinstance(body, str):
            body_data = json.loads(body)
        else:
            body_data = body
        
        # Route based on method and parameters
        if method == "POST" and query_params.get("action") == "create":
            # Create new alert
            level = AlertLevel(body_data.get("level", "info"))
            service = body_data.get("service", "unknown")
            message = body_data.get("message", "")
            metadata = body_data.get("metadata", {})
            
            alert = alert_manager.create_alert(level, service, message, metadata)
            
            return {
                "statusCode": 201,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "status": "success",
                    "alert_id": alert.id,
                    "message": "Alert created successfully"
                })
            }
        
        elif method == "POST" and query_params.get("action") == "resolve":
            # Resolve alert
            alert_id = body_data.get("alert_id")
            
            if alert_manager.resolve_alert(alert_id):
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({
                        "status": "success",
                        "message": "Alert resolved successfully"
                    })
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({
                        "status": "error",
                        "message": "Alert not found"
                    })
                }
        
        elif method == "GET" and query_params.get("action") == "active":
            # Get active alerts
            alerts = alert_manager.get_active_alerts()
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "alerts": [
                        {
                            "id": alert.id,
                            "level": alert.level.value,
                            "service": alert.service,
                            "message": alert.message,
                            "timestamp": alert.timestamp.isoformat(),
                            "metadata": alert.metadata
                        }
                        for alert in alerts
                    ]
                })
            }
        
        elif method == "GET" and query_params.get("action") == "stats":
            # Get alert statistics
            stats = alert_manager.get_alert_statistics()
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(stats)
            }
        
        else:
            # Default: return alert configuration
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "alert_rules": alert_manager.alert_rules,
                    "notification_config": {
                        "email_enabled": alert_manager.notification_config["email"]["enabled"],
                        "slack_enabled": alert_manager.notification_config["slack"]["enabled"],
                        "webhook_enabled": alert_manager.notification_config["webhook"]["enabled"]
                    }
                })
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": "Alerting system error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
