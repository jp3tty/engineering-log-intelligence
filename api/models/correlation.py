"""
Correlation model for the Engineering Log Intelligence System.
Handles log correlation and pattern matching.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import json
import uuid


@dataclass
class Correlation:
    """Represents a correlation between log entries."""
    
    # Primary key
    id: Optional[int] = None
    
    # Correlation identification
    correlation_id: str = ""
    correlation_type: str = ""  # request, session, ip, timestamp, pattern
    
    # Related log entries
    log_entry_ids: List[int] = None
    source_systems: List[str] = None  # splunk, sap, application
    
    # Correlation data
    correlation_key: str = ""  # request_id, session_id, ip_address, etc.
    correlation_value: str = ""  # actual value
    confidence_score: float = 0.0  # 0.0 to 1.0
    
    # Pattern matching
    pattern_type: Optional[str] = None
    pattern_data: Dict[str, Any] = None
    
    # Timing
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Metadata
    metadata: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())
        if self.log_entry_ids is None:
            self.log_entry_ids = []
        if self.source_systems is None:
            self.source_systems = []
        if self.pattern_data is None:
            self.pattern_data = {}
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def add_log_entry(self, log_entry_id: int, source_system: str) -> None:
        """Add a log entry to the correlation."""
        if log_entry_id not in self.log_entry_ids:
            self.log_entry_ids.append(log_entry_id)
            if source_system not in self.source_systems:
                self.source_systems.append(source_system)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_log_entry(self, log_entry_id: int) -> None:
        """Remove a log entry from the correlation."""
        if log_entry_id in self.log_entry_ids:
            self.log_entry_ids.remove(log_entry_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def update_confidence(self, score: float) -> None:
        """Update the confidence score."""
        self.confidence_score = max(0.0, min(1.0, score))
        self.updated_at = datetime.now(timezone.utc)
    
    def is_high_confidence(self) -> bool:
        """Check if the correlation has high confidence."""
        return self.confidence_score >= 0.8
    
    def is_multi_system(self) -> bool:
        """Check if the correlation spans multiple systems."""
        return len(self.source_systems) > 1
    
    def get_duration_minutes(self) -> Optional[int]:
        """Get the correlation duration in minutes."""
        if self.first_seen and self.last_seen:
            return int((self.last_seen - self.first_seen).total_seconds() / 60)
        return None
    
    def get_age_minutes(self) -> int:
        """Get the age of the correlation in minutes."""
        if self.first_seen:
            return int((datetime.now(timezone.utc) - self.first_seen).total_seconds() / 60)
        return 0
    
    def get_correlation_key(self) -> str:
        """Get a key for this correlation."""
        return f"{self.correlation_type}:{self.correlation_value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the correlation to a dictionary."""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        for field in ['first_seen', 'last_seen', 'created_at', 'updated_at']:
            if data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Correlation':
        """Create a Correlation from a dictionary."""
        # Convert ISO strings back to datetime objects
        for field in ['first_seen', 'last_seen', 'created_at', 'updated_at']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    data[field] = None
        
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate the correlation and return any validation errors."""
        errors = []
        
        # Required fields
        if not self.correlation_id:
            errors.append("correlation_id is required")
        if not self.correlation_type:
            errors.append("correlation_type is required")
        if not self.correlation_key:
            errors.append("correlation_key is required")
        if not self.correlation_value:
            errors.append("correlation_value is required")
        
        # Correlation type validation
        valid_types = ['request', 'session', 'ip', 'timestamp', 'pattern']
        if self.correlation_type not in valid_types:
            errors.append(f"correlation_type must be one of {valid_types}")
        
        # Confidence score validation
        if not 0.0 <= self.confidence_score <= 1.0:
            errors.append("confidence_score must be between 0.0 and 1.0")
        
        # Log entries validation
        if not self.log_entry_ids:
            errors.append("at least one log entry is required")
        
        return errors
    
    def get_database_insert_query(self) -> tuple:
        """Get the SQL INSERT query and parameters for this correlation."""
        query = """
        INSERT INTO correlations (
            correlation_id, correlation_type, log_entry_ids, source_systems,
            correlation_key, correlation_value, confidence_score, pattern_type,
            pattern_data, first_seen, last_seen, duration_seconds, metadata,
            created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        params = (
            self.correlation_id, self.correlation_type, json.dumps(self.log_entry_ids),
            json.dumps(self.source_systems), self.correlation_key, self.correlation_value,
            self.confidence_score, self.pattern_type, json.dumps(self.pattern_data),
            self.first_seen, self.last_seen, self.duration_seconds, json.dumps(self.metadata),
            self.created_at, self.updated_at
        )
        
        return query, params
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> 'Correlation':
        """Create a Correlation from a database row."""
        log_entry_ids = json.loads(row.get('log_entry_ids', '[]')) if row.get('log_entry_ids') else []
        source_systems = json.loads(row.get('source_systems', '[]')) if row.get('source_systems') else []
        pattern_data = json.loads(row.get('pattern_data', '{}')) if row.get('pattern_data') else {}
        metadata = json.loads(row.get('metadata', '{}')) if row.get('metadata') else {}
        
        return cls(
            id=row.get('id'),
            correlation_id=row.get('correlation_id', ''),
            correlation_type=row.get('correlation_type', ''),
            log_entry_ids=log_entry_ids,
            source_systems=source_systems,
            correlation_key=row.get('correlation_key', ''),
            correlation_value=row.get('correlation_value', ''),
            confidence_score=row.get('confidence_score', 0.0),
            pattern_type=row.get('pattern_type'),
            pattern_data=pattern_data,
            first_seen=row.get('first_seen'),
            last_seen=row.get('last_seen'),
            duration_seconds=row.get('duration_seconds'),
            metadata=metadata,
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
