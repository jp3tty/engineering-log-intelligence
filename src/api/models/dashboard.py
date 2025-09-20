"""
Dashboard model for the Engineering Log Intelligence System.
Handles dashboard configurations and widgets.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import json
import uuid


@dataclass
class Dashboard:
    """Represents a dashboard configuration."""
    
    # Primary key
    id: Optional[int] = None
    
    # Dashboard identification
    dashboard_id: str = ""
    name: str = ""
    description: str = ""
    
    # Dashboard configuration
    layout: Dict[str, Any] = None
    widgets: List[Dict[str, Any]] = None
    filters: Dict[str, Any] = None
    
    # Access control
    owner_id: Optional[int] = None  # user_id
    is_public: bool = False
    shared_with: List[int] = None  # user_ids
    
    # Dashboard settings
    refresh_interval: int = 30  # seconds
    auto_refresh: bool = True
    theme: str = "default"
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if not self.dashboard_id:
            self.dashboard_id = str(uuid.uuid4())
        if self.layout is None:
            self.layout = {"rows": 4, "cols": 6}
        if self.widgets is None:
            self.widgets = []
        if self.filters is None:
            self.filters = {}
        if self.shared_with is None:
            self.shared_with = []
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def add_widget(self, widget: Dict[str, Any]) -> None:
        """Add a widget to the dashboard."""
        if 'id' not in widget:
            widget['id'] = str(uuid.uuid4())
        self.widgets.append(widget)
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_widget(self, widget_id: str) -> None:
        """Remove a widget from the dashboard."""
        self.widgets = [w for w in self.widgets if w.get('id') != widget_id]
        self.updated_at = datetime.now(timezone.utc)
    
    def update_widget(self, widget_id: str, updates: Dict[str, Any]) -> None:
        """Update a widget in the dashboard."""
        for widget in self.widgets:
            if widget.get('id') == widget_id:
                widget.update(updates)
                self.updated_at = datetime.now(timezone.utc)
                break
    
    def share_with_user(self, user_id: int) -> None:
        """Share the dashboard with a user."""
        if user_id not in self.shared_with:
            self.shared_with.append(user_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def unshare_with_user(self, user_id: int) -> None:
        """Stop sharing the dashboard with a user."""
        if user_id in self.shared_with:
            self.shared_with.remove(user_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def can_access(self, user_id: int) -> bool:
        """Check if a user can access this dashboard."""
        return (
            self.is_public or
            self.owner_id == user_id or
            user_id in self.shared_with
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dashboard to a dictionary."""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        for field in ['created_at', 'updated_at']:
            if data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dashboard':
        """Create a Dashboard from a dictionary."""
        # Convert ISO strings back to datetime objects
        for field in ['created_at', 'updated_at']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    data[field] = None
        
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate the dashboard and return any validation errors."""
        errors = []
        
        # Required fields
        if not self.dashboard_id:
            errors.append("dashboard_id is required")
        if not self.name:
            errors.append("name is required")
        
        # Refresh interval validation
        if self.refresh_interval < 5:
            errors.append("refresh_interval must be at least 5 seconds")
        
        # Theme validation
        valid_themes = ['default', 'dark', 'light', 'high-contrast']
        if self.theme not in valid_themes:
            errors.append(f"theme must be one of {valid_themes}")
        
        return errors
    
    def get_database_insert_query(self) -> tuple:
        """Get the SQL INSERT query and parameters for this dashboard."""
        query = """
        INSERT INTO dashboards (
            dashboard_id, name, description, layout, widgets, filters,
            owner_id, is_public, shared_with, refresh_interval, auto_refresh,
            theme, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        params = (
            self.dashboard_id, self.name, self.description, json.dumps(self.layout),
            json.dumps(self.widgets), json.dumps(self.filters), self.owner_id,
            self.is_public, json.dumps(self.shared_with), self.refresh_interval,
            self.auto_refresh, self.theme, self.created_at, self.updated_at
        )
        
        return query, params
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> 'Dashboard':
        """Create a Dashboard from a database row."""
        layout = json.loads(row.get('layout', '{}')) if row.get('layout') else {}
        widgets = json.loads(row.get('widgets', '[]')) if row.get('widgets') else []
        filters = json.loads(row.get('filters', '{}')) if row.get('filters') else {}
        shared_with = json.loads(row.get('shared_with', '[]')) if row.get('shared_with') else []
        
        return cls(
            id=row.get('id'),
            dashboard_id=row.get('dashboard_id', ''),
            name=row.get('name', ''),
            description=row.get('description', ''),
            layout=layout,
            widgets=widgets,
            filters=filters,
            owner_id=row.get('owner_id'),
            is_public=row.get('is_public', False),
            shared_with=shared_with,
            refresh_interval=row.get('refresh_interval', 30),
            auto_refresh=row.get('auto_refresh', True),
            theme=row.get('theme', 'default'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
