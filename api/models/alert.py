"""
Alert model for the Engineering Log Intelligence System.
Handles system alerts and notifications.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import json
import uuid


@dataclass
class Alert:
    """Represents an alert in the system."""
    
    # Primary key
    id: Optional[int] = None
    
    # Alert identification
    alert_id: str = ""
    title: str = ""
    description: str = ""
    
    # Alert classification
    severity: str = "medium"  # low, medium, high, critical
    category: str = "system"  # system, security, performance, business
    source: str = ""  # splunk, sap, application, manual
    
    # Alert status
    status: str = "open"  # open, acknowledged, resolved, closed
    assigned_to: Optional[int] = None  # user_id
    
    # Alert data
    log_entries: List[int] = None  # log_entry_ids
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    # Timing
    triggered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Resolution
    resolution_notes: str = ""
    resolved_by: Optional[int] = None  # user_id
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if not self.alert_id:
            self.alert_id = str(uuid.uuid4())
        if self.log_entries is None:
            self.log_entries = []
        if self.metadata is None:
            self.metadata = {}
        if self.triggered_at is None:
            self.triggered_at = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def acknowledge(self, user_id: int) -> None:
        """Acknowledge the alert."""
        self.status = "acknowledged"
        self.assigned_to = user_id
        self.acknowledged_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def resolve(self, user_id: int, notes: str = "") -> None:
        """Resolve the alert."""
        self.status = "resolved"
        self.resolved_by = user_id
        self.resolved_at = datetime.now(timezone.utc)
        self.resolution_notes = notes
        self.updated_at = datetime.now(timezone.utc)
    
    def close(self) -> None:
        """Close the alert."""
        self.status = "closed"
        self.updated_at = datetime.now(timezone.utc)
    
    def reopen(self) -> None:
        """Reopen the alert."""
        self.status = "open"
        self.acknowledged_at = None
        self.resolved_at = None
        self.resolved_by = None
        self.resolution_notes = ""
        self.updated_at = datetime.now(timezone.utc)
    
    def add_log_entry(self, log_entry_id: int) -> None:
        """Add a log entry to the alert."""
        if log_entry_id not in self.log_entries:
            self.log_entries.append(log_entry_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_log_entry(self, log_entry_id: int) -> None:
        """Remove a log entry from the alert."""
        if log_entry_id in self.log_entries:
            self.log_entries.remove(log_entry_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def is_open(self) -> bool:
        """Check if the alert is open."""
        return self.status == "open"
    
    def is_acknowledged(self) -> bool:
        """Check if the alert is acknowledged."""
        return self.status == "acknowledged"
    
    def is_resolved(self) -> bool:
        """Check if the alert is resolved."""
        return self.status == "resolved"
    
    def is_closed(self) -> bool:
        """Check if the alert is closed."""
        return self.status == "closed"
    
    def is_critical(self) -> bool:
        """Check if the alert is critical severity."""
        return self.severity == "critical"
    
    def is_high_priority(self) -> bool:
        """Check if the alert is high priority."""
        return self.severity in ["high", "critical"]
    
    def get_age_minutes(self) -> int:
        """Get the age of the alert in minutes."""
        if self.triggered_at:
            return int((datetime.now(timezone.utc) - self.triggered_at).total_seconds() / 60)
        return 0
    
    def get_resolution_time_minutes(self) -> Optional[int]:
        """Get the resolution time in minutes."""
        if self.triggered_at and self.resolved_at:
            return int((self.resolved_at - self.triggered_at).total_seconds() / 60)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the alert to a dictionary."""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        for field in ['triggered_at', 'acknowledged_at', 'resolved_at', 'created_at', 'updated_at']:
            if data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create an Alert from a dictionary."""
        # Convert ISO strings back to datetime objects
        for field in ['triggered_at', 'acknowledged_at', 'resolved_at', 'created_at', 'updated_at']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    data[field] = None
        
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate the alert and return any validation errors."""
        errors = []
        
        # Required fields
        if not self.alert_id:
            errors.append("alert_id is required")
        if not self.title:
            errors.append("title is required")
        if not self.description:
            errors.append("description is required")
        
        # Severity validation
        valid_severities = ['low', 'medium', 'high', 'critical']
        if self.severity not in valid_severities:
            errors.append(f"severity must be one of {valid_severities}")
        
        # Category validation
        valid_categories = ['system', 'security', 'performance', 'business']
        if self.category not in valid_categories:
            errors.append(f"category must be one of {valid_categories}")
        
        # Status validation
        valid_statuses = ['open', 'acknowledged', 'resolved', 'closed']
        if self.status not in valid_statuses:
            errors.append(f"status must be one of {valid_statuses}")
        
        return errors
    
    def get_database_insert_query(self) -> tuple:
        """Get the SQL INSERT query and parameters for this alert."""
        query = """
        INSERT INTO alerts (
            alert_id, title, description, severity, category, source, status,
            assigned_to, log_entries, correlation_id, metadata, triggered_at,
            acknowledged_at, resolved_at, resolution_notes, resolved_by,
            created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        params = (
            self.alert_id, self.title, self.description, self.severity,
            self.category, self.source, self.status, self.assigned_to,
            json.dumps(self.log_entries), self.correlation_id, json.dumps(self.metadata),
            self.triggered_at, self.acknowledged_at, self.resolved_at,
            self.resolution_notes, self.resolved_by, self.created_at, self.updated_at
        )
        
        return query, params
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> 'Alert':
        """Create an Alert from a database row."""
        log_entries = json.loads(row.get('log_entries', '[]')) if row.get('log_entries') else []
        metadata = json.loads(row.get('metadata', '{}')) if row.get('metadata') else {}
        
        return cls(
            id=row.get('id'),
            alert_id=row.get('alert_id', ''),
            title=row.get('title', ''),
            description=row.get('description', ''),
            severity=row.get('severity', 'medium'),
            category=row.get('category', 'system'),
            source=row.get('source', ''),
            status=row.get('status', 'open'),
            assigned_to=row.get('assigned_to'),
            log_entries=log_entries,
            correlation_id=row.get('correlation_id'),
            metadata=metadata,
            triggered_at=row.get('triggered_at'),
            acknowledged_at=row.get('acknowledged_at'),
            resolved_at=row.get('resolved_at'),
            resolution_notes=row.get('resolution_notes', ''),
            resolved_by=row.get('resolved_by'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
