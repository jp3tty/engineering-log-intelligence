"""
Incident response system for Engineering Log Intelligence System.
Handles incident creation, management, and resolution workflows.
"""

import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class IncidentStatus(Enum):
    """Incident status levels."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentSeverity(Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class Incident:
    """Incident data structure."""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    service: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    tags: List[str] = None
    timeline: List[Dict[str, Any]] = None
    impact: Dict[str, Any] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    metadata: Dict[str, Any] = None

class IncidentManager:
    """Manages incidents and response workflows."""
    
    def __init__(self):
        self.incidents = []
        self.response_playbooks = self._load_response_playbooks()
        self.escalation_rules = self._load_escalation_rules()
        
    def _load_response_playbooks(self) -> Dict[str, Any]:
        """Load incident response playbooks."""
        return {
            "database_down": {
                "title": "Database Service Down",
                "severity": IncidentSeverity.CRITICAL,
                "steps": [
                    "Check database connectivity",
                    "Verify database service status",
                    "Check resource usage (CPU, memory, disk)",
                    "Review recent database logs",
                    "Check for backup availability",
                    "Implement failover if available",
                    "Notify stakeholders"
                ],
                "estimated_resolution": "30 minutes"
            },
            "elasticsearch_down": {
                "title": "Elasticsearch Service Down",
                "severity": IncidentSeverity.HIGH,
                "steps": [
                    "Check Elasticsearch cluster health",
                    "Verify node status and shard allocation",
                    "Check disk space and memory usage",
                    "Review Elasticsearch logs",
                    "Check index corruption",
                    "Restart service if needed",
                    "Rebuild indexes if necessary"
                ],
                "estimated_resolution": "45 minutes"
            },
            "kafka_down": {
                "title": "Kafka Service Down",
                "severity": IncidentSeverity.HIGH,
                "steps": [
                    "Check Kafka cluster health",
                    "Verify broker status",
                    "Check topic and partition status",
                    "Review Kafka logs",
                    "Check network connectivity",
                    "Restart brokers if needed",
                    "Verify message delivery"
                ],
                "estimated_resolution": "20 minutes"
            },
            "vercel_functions_down": {
                "title": "Vercel Functions Down",
                "severity": IncidentSeverity.CRITICAL,
                "steps": [
                    "Check Vercel deployment status",
                    "Review function logs",
                    "Check environment variables",
                    "Verify external service connectivity",
                    "Check function timeout settings",
                    "Redeploy if necessary",
                    "Test function endpoints"
                ],
                "estimated_resolution": "15 minutes"
            },
            "performance_degradation": {
                "title": "Performance Degradation",
                "severity": IncidentSeverity.MEDIUM,
                "steps": [
                    "Identify affected services",
                    "Check response times and error rates",
                    "Review resource usage",
                    "Check for recent deployments",
                    "Analyze traffic patterns",
                    "Implement scaling if needed",
                    "Monitor improvements"
                ],
                "estimated_resolution": "60 minutes"
            }
        }
    
    def _load_escalation_rules(self) -> Dict[str, Any]:
        """Load escalation rules."""
        return {
            "time_based": {
                "critical": 15,  # minutes
                "high": 30,      # minutes
                "medium": 60,    # minutes
                "low": 120       # minutes
            },
            "severity_escalation": {
                "critical": ["oncall_primary", "oncall_secondary", "management"],
                "high": ["oncall_primary", "oncall_secondary"],
                "medium": ["oncall_primary"],
                "low": ["oncall_primary"]
            }
        }
    
    def create_incident(self, title: str, description: str, severity: IncidentSeverity, 
                       service: str, tags: List[str] = None, metadata: Dict[str, Any] = None) -> Incident:
        """Create a new incident."""
        incident_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            service=service,
            created_at=current_time,
            updated_at=current_time,
            tags=tags or [],
            timeline=[{
                "timestamp": current_time.isoformat(),
                "action": "incident_created",
                "description": f"Incident created: {title}",
                "user": "system"
            }],
            impact={},
            metadata=metadata or {}
        )
        
        self.incidents.append(incident)
        
        # Auto-assign based on severity
        self._auto_assign_incident(incident)
        
        # Start escalation timer
        self._start_escalation_timer(incident)
        
        return incident
    
    def _auto_assign_incident(self, incident: Incident):
        """Auto-assign incident based on severity."""
        assignment_rules = {
            IncidentSeverity.EMERGENCY: "oncall_primary",
            IncidentSeverity.CRITICAL: "oncall_primary",
            IncidentSeverity.HIGH: "oncall_primary",
            IncidentSeverity.MEDIUM: "oncall_primary",
            IncidentSeverity.LOW: "oncall_primary"
        }
        
        incident.assigned_to = assignment_rules.get(incident.severity, "oncall_primary")
        
        # Add to timeline
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "auto_assigned",
            "description": f"Auto-assigned to {incident.assigned_to}",
            "user": "system"
        })
    
    def _start_escalation_timer(self, incident: Incident):
        """Start escalation timer for incident."""
        # This would typically use a background job system
        # For now, we'll just log the escalation start
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "escalation_started",
            "description": f"Escalation timer started for {incident.severity.value} severity",
            "user": "system"
        })
    
    def update_incident_status(self, incident_id: str, status: IncidentStatus, 
                             user: str, notes: str = None) -> bool:
        """Update incident status."""
        for incident in self.incidents:
            if incident.id == incident_id:
                old_status = incident.status
                incident.status = status
                incident.updated_at = datetime.utcnow()
                
                # Add to timeline
                incident.timeline.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "status_updated",
                    "description": f"Status changed from {old_status.value} to {status.value}",
                    "user": user,
                    "notes": notes
                })
                
                # Handle resolution
                if status == IncidentStatus.RESOLVED:
                    incident.resolved_at = datetime.utcnow()
                
                return True
        return False
    
    def add_timeline_entry(self, incident_id: str, action: str, description: str, 
                          user: str, metadata: Dict[str, Any] = None) -> bool:
        """Add entry to incident timeline."""
        for incident in self.incidents:
            if incident.id == incident_id:
                incident.timeline.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": action,
                    "description": description,
                    "user": user,
                    "metadata": metadata or {}
                })
                incident.updated_at = datetime.utcnow()
                return True
        return False
    
    def assign_incident(self, incident_id: str, assigned_to: str, user: str) -> bool:
        """Assign incident to a user."""
        for incident in self.incidents:
            if incident.id == incident_id:
                old_assignee = incident.assigned_to
                incident.assigned_to = assigned_to
                incident.updated_at = datetime.utcnow()
                
                # Add to timeline
                incident.timeline.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "assigned",
                    "description": f"Assigned from {old_assignee} to {assigned_to}",
                    "user": user
                })
                return True
        return False
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID."""
        for incident in self.incidents:
            if incident.id == incident_id:
                return incident
        return None
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all active incidents."""
        active_statuses = [
            IncidentStatus.OPEN,
            IncidentStatus.INVESTIGATING,
            IncidentStatus.IDENTIFIED,
            IncidentStatus.MONITORING
        ]
        return [incident for incident in self.incidents if incident.status in active_statuses]
    
    def get_incidents_by_service(self, service: str) -> List[Incident]:
        """Get incidents for a specific service."""
        return [incident for incident in self.incidents if incident.service == service]
    
    def get_incidents_by_severity(self, severity: IncidentSeverity) -> List[Incident]:
        """Get incidents by severity level."""
        return [incident for incident in self.incidents if incident.severity == severity]
    
    def get_incident_statistics(self) -> Dict[str, Any]:
        """Get incident statistics."""
        total_incidents = len(self.incidents)
        active_incidents = len(self.get_active_incidents())
        resolved_incidents = total_incidents - active_incidents
        
        severity_counts = {}
        for severity in IncidentSeverity:
            severity_counts[severity.value] = len(self.get_incidents_by_severity(severity))
        
        status_counts = {}
        for status in IncidentStatus:
            status_counts[status.value] = len([i for i in self.incidents if i.status == status])
        
        service_counts = {}
        for incident in self.incidents:
            service_counts[incident.service] = service_counts.get(incident.service, 0) + 1
        
        # Calculate average resolution time
        resolved_incidents_with_time = [
            i for i in self.incidents 
            if i.resolved_at and i.status == IncidentStatus.RESOLVED
        ]
        
        avg_resolution_time = 0
        if resolved_incidents_with_time:
            total_time = sum([
                (i.resolved_at - i.created_at).total_seconds() / 60  # minutes
                for i in resolved_incidents_with_time
            ])
            avg_resolution_time = total_time / len(resolved_incidents_with_time)
        
        return {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "resolved_incidents": resolved_incidents,
            "severity_breakdown": severity_counts,
            "status_breakdown": status_counts,
            "service_breakdown": service_counts,
            "average_resolution_time_minutes": round(avg_resolution_time, 2),
            "resolution_rate": (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 0
        }
    
    def get_response_playbook(self, incident_type: str) -> Optional[Dict[str, Any]]:
        """Get response playbook for incident type."""
        return self.response_playbooks.get(incident_type)
    
    def escalate_incident(self, incident_id: str, user: str, reason: str) -> bool:
        """Escalate an incident."""
        incident = self.get_incident(incident_id)
        if not incident:
            return False
        
        # Add escalation to timeline
        self.add_timeline_entry(
            incident_id,
            "escalated",
            f"Incident escalated: {reason}",
            user
        )
        
        # Update severity if needed
        if incident.severity == IncidentSeverity.LOW:
            incident.severity = IncidentSeverity.MEDIUM
        elif incident.severity == IncidentSeverity.MEDIUM:
            incident.severity = IncidentSeverity.HIGH
        elif incident.severity == IncidentSeverity.HIGH:
            incident.severity = IncidentSeverity.CRITICAL
        
        return True


def handler(request) -> Dict[str, Any]:
    """
    Incident response handler for Vercel Functions.
    Manages incident creation, updates, and resolution workflows.
    """
    try:
        incident_manager = IncidentManager()
        
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
            # Create new incident
            title = body_data.get("title", "")
            description = body_data.get("description", "")
            severity = IncidentSeverity(body_data.get("severity", "low"))
            service = body_data.get("service", "unknown")
            tags = body_data.get("tags", [])
            metadata = body_data.get("metadata", {})
            
            incident = incident_manager.create_incident(
                title, description, severity, service, tags, metadata
            )
            
            return {
                "statusCode": 201,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "status": "success",
                    "incident_id": incident.id,
                    "message": "Incident created successfully"
                })
            }
        
        elif method == "POST" and query_params.get("action") == "update_status":
            # Update incident status
            incident_id = body_data.get("incident_id")
            status = IncidentStatus(body_data.get("status"))
            user = body_data.get("user", "system")
            notes = body_data.get("notes")
            
            if incident_manager.update_incident_status(incident_id, status, user, notes):
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({
                        "status": "success",
                        "message": "Incident status updated successfully"
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
                        "message": "Incident not found"
                    })
                }
        
        elif method == "GET" and query_params.get("action") == "active":
            # Get active incidents
            incidents = incident_manager.get_active_incidents()
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "incidents": [
                        {
                            "id": incident.id,
                            "title": incident.title,
                            "severity": incident.severity.value,
                            "status": incident.status.value,
                            "service": incident.service,
                            "created_at": incident.created_at.isoformat(),
                            "assigned_to": incident.assigned_to,
                            "tags": incident.tags
                        }
                        for incident in incidents
                    ]
                })
            }
        
        elif method == "GET" and query_params.get("action") == "stats":
            # Get incident statistics
            stats = incident_manager.get_incident_statistics()
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(stats)
            }
        
        else:
            # Default: return incident configuration
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "response_playbooks": list(incident_manager.response_playbooks.keys()),
                    "escalation_rules": incident_manager.escalation_rules
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
                "error": "Incident response system error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
