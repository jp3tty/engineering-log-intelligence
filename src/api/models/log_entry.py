"""
Log entry model for the Engineering Log Intelligence System.
Represents log entries from SPLUNK, SAP, and Application sources.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import json
import uuid


@dataclass
class LogEntry:
    """Represents a log entry in the database."""
    
    # Primary key
    id: Optional[int] = None
    
    # Basic log information
    log_id: str = ""
    timestamp: datetime = None
    level: str = "INFO"
    message: str = ""
    source_type: str = ""  # splunk, sap, application
    
    # System information
    host: str = ""
    service: str = ""
    category: str = ""
    tags: List[str] = None
    
    # Raw log data
    raw_log: str = ""
    structured_data: Dict[str, Any] = None
    
    # Correlation fields
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Application-specific fields
    application_type: Optional[str] = None
    framework: Optional[str] = None
    http_method: Optional[str] = None
    http_status: Optional[int] = None
    endpoint: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    # SAP-specific fields
    transaction_code: Optional[str] = None
    sap_system: Optional[str] = None
    department: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    document_number: Optional[str] = None
    
    # SPLUNK-specific fields
    splunk_source: Optional[str] = None
    splunk_host: Optional[str] = None
    
    # Anomaly and error information
    is_anomaly: bool = False
    anomaly_type: Optional[str] = None
    error_details: Dict[str, Any] = None
    performance_metrics: Dict[str, Any] = None
    business_context: Dict[str, Any] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.tags is None:
            self.tags = []
        if self.structured_data is None:
            self.structured_data = {}
        if self.error_details is None:
            self.error_details = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.business_context is None:
            self.business_context = {}
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the log entry to a dictionary."""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        for field in ['timestamp', 'created_at', 'updated_at']:
            if data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create a LogEntry from a dictionary."""
        # Convert ISO strings back to datetime objects
        for field in ['timestamp', 'created_at', 'updated_at']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    data[field] = None
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert the log entry to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LogEntry':
        """Create a LogEntry from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def generate_log_id(self) -> str:
        """Generate a unique log ID if not already set."""
        if not self.log_id:
            timestamp = int(self.timestamp.timestamp() * 1000)
            self.log_id = f"{self.source_type}-{timestamp}-{uuid.uuid4().hex[:6]}"
        return self.log_id
    
    def is_error(self) -> bool:
        """Check if this log entry represents an error."""
        return self.level in ['ERROR', 'FATAL'] or (self.http_status and self.http_status >= 400)
    
    def is_high_priority(self) -> bool:
        """Check if this log entry is high priority."""
        return (
            self.level in ['FATAL', 'ERROR'] or
            self.is_anomaly or
            (self.http_status and self.http_status >= 500) or
            (self.anomaly_type and self.anomaly_type in ['security_incident', 'data_corruption'])
        ) or False
    
    def get_correlation_key(self) -> str:
        """Get a key for correlating related log entries."""
        if self.request_id:
            return f"request:{self.request_id}"
        elif self.session_id:
            return f"session:{self.session_id}"
        elif self.correlation_id:
            return f"correlation:{self.correlation_id}"
        elif self.ip_address:
            return f"ip:{self.ip_address}"
        else:
            return f"timestamp:{self.timestamp.isoformat()}"
    
    def get_summary(self) -> str:
        """Get a summary of the log entry for display."""
        if self.source_type == 'application':
            return f"{self.http_method} {self.endpoint} - {self.http_status} - {self.response_time_ms}ms"
        elif self.source_type == 'sap':
            return f"{self.transaction_code} - {self.department} - {self.amount} {self.currency}"
        elif self.source_type == 'splunk':
            return f"{self.splunk_source} - {self.message}"
        else:
            return f"{self.level} - {self.message}"
    
    def validate(self) -> List[str]:
        """Validate the log entry and return any validation errors."""
        errors = []
        
        # Required fields
        if not self.log_id:
            errors.append("log_id is required")
        if not self.timestamp:
            errors.append("timestamp is required")
        if not self.level:
            errors.append("level is required")
        if not self.message:
            errors.append("message is required")
        if not self.source_type:
            errors.append("source_type is required")
        
        # Level validation
        valid_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
        if self.level not in valid_levels:
            errors.append(f"level must be one of {valid_levels}")
        
        # Source type validation
        valid_sources = ['splunk', 'sap', 'application']
        if self.source_type not in valid_sources:
            errors.append(f"source_type must be one of {valid_sources}")
        
        # HTTP status validation
        if self.http_status is not None and (self.http_status < 100 or self.http_status >= 600):
            errors.append("http_status must be between 100 and 599")
        
        # Response time validation
        if self.response_time_ms is not None and self.response_time_ms < 0:
            errors.append("response_time_ms must be non-negative")
        
        return errors
    
    def get_database_insert_query(self) -> tuple:
        """Get the SQL INSERT query and parameters for this log entry."""
        query = """
        INSERT INTO log_entries (
            log_id, timestamp, level, message, source_type, host, service, category,
            tags, raw_log, structured_data, request_id, session_id, correlation_id,
            ip_address, application_type, framework, http_method, http_status,
            endpoint, response_time_ms, transaction_code, sap_system, department,
            amount, currency, document_number, splunk_source, splunk_host,
            is_anomaly, anomaly_type, error_details, performance_metrics,
            business_context, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        ) RETURNING id
        """
        
        params = (
            self.log_id, self.timestamp, self.level, self.message, self.source_type,
            self.host, self.service, self.category, json.dumps(self.tags),
            self.raw_log, json.dumps(self.structured_data), self.request_id,
            self.session_id, self.correlation_id, self.ip_address,
            self.application_type, self.framework, self.http_method, self.http_status,
            self.endpoint, self.response_time_ms, self.transaction_code,
            self.sap_system, self.department, self.amount, self.currency,
            self.document_number, self.splunk_source, self.splunk_host,
            self.is_anomaly, self.anomaly_type, json.dumps(self.error_details),
            json.dumps(self.performance_metrics), json.dumps(self.business_context),
            self.created_at, self.updated_at
        )
        
        return query, params
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> 'LogEntry':
        """Create a LogEntry from a database row."""
        # Parse JSON fields
        tags = json.loads(row.get('tags', '[]')) if row.get('tags') else []
        structured_data = json.loads(row.get('structured_data', '{}')) if row.get('structured_data') else {}
        error_details = json.loads(row.get('error_details', '{}')) if row.get('error_details') else {}
        performance_metrics = json.loads(row.get('performance_metrics', '{}')) if row.get('performance_metrics') else {}
        business_context = json.loads(row.get('business_context', '{}')) if row.get('business_context') else {}
        
        return cls(
            id=row.get('id'),
            log_id=row.get('log_id', ''),
            timestamp=row.get('timestamp'),
            level=row.get('level', 'INFO'),
            message=row.get('message', ''),
            source_type=row.get('source_type', ''),
            host=row.get('host', ''),
            service=row.get('service', ''),
            category=row.get('category', ''),
            tags=tags,
            raw_log=row.get('raw_log', ''),
            structured_data=structured_data,
            request_id=row.get('request_id'),
            session_id=row.get('session_id'),
            correlation_id=row.get('correlation_id'),
            ip_address=row.get('ip_address'),
            application_type=row.get('application_type'),
            framework=row.get('framework'),
            http_method=row.get('http_method'),
            http_status=row.get('http_status'),
            endpoint=row.get('endpoint'),
            response_time_ms=row.get('response_time_ms'),
            transaction_code=row.get('transaction_code'),
            sap_system=row.get('sap_system'),
            department=row.get('department'),
            amount=row.get('amount'),
            currency=row.get('currency'),
            document_number=row.get('document_number'),
            splunk_source=row.get('splunk_source'),
            splunk_host=row.get('splunk_host'),
            is_anomaly=row.get('is_anomaly', False),
            anomaly_type=row.get('anomaly_type'),
            error_details=error_details,
            performance_metrics=performance_metrics,
            business_context=business_context,
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
