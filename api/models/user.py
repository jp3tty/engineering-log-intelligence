"""
User model for the Engineering Log Intelligence System.
Handles user authentication and authorization.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import hashlib
import secrets
import uuid


@dataclass
class User:
    """Represents a user in the system."""
    
    # Primary key
    id: Optional[int] = None
    
    # Basic user information
    username: str = ""
    email: str = ""
    password_hash: str = ""
    salt: str = ""
    
    # User profile
    first_name: str = ""
    last_name: str = ""
    role: str = "user"  # user, admin, analyst, viewer
    
    # Account status
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    
    # Permissions
    permissions: List[str] = None
    
    # API access
    api_key: Optional[str] = None
    api_key_created: Optional[datetime] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.permissions is None:
            self.permissions = self._get_default_permissions()
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
        if not self.salt:
            self.salt = secrets.token_hex(32)
        if not self.api_key:
            self.api_key = self.generate_api_key()
    
    def _get_default_permissions(self) -> List[str]:
        """Get default permissions based on role."""
        role_permissions = {
            'viewer': ['read_logs', 'view_dashboard'],
            'user': ['read_logs', 'view_dashboard', 'create_alerts'],
            'analyst': ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data'],
            'admin': ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data', 
                     'manage_users', 'manage_system', 'configure_alerts']
        }
        return role_permissions.get(self.role, ['read_logs'])
    
    def set_password(self, password: str) -> None:
        """Set the user's password with proper hashing."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Generate a new salt
        self.salt = secrets.token_hex(32)
        
        # Hash the password with salt
        self.password_hash = self._hash_password(password, self.salt)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password is correct."""
        if not self.password_hash or not self.salt:
            return False
        
        hashed_password = self._hash_password(password, self.salt)
        return hashed_password == self.password_hash
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with salt using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()
    
    def generate_api_key(self) -> str:
        """Generate a new API key for the user."""
        self.api_key = f"eli_{secrets.token_urlsafe(32)}"
        self.api_key_created = datetime.now(timezone.utc)
        return self.api_key
    
    def revoke_api_key(self) -> None:
        """Revoke the user's API key."""
        self.api_key = None
        self.api_key_created = None
    
    def has_permission(self, permission: str) -> bool:
        """Check if the user has a specific permission."""
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """Check if the user has a specific role."""
        return self.role == role
    
    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        return self.role == 'admin'
    
    def can_manage_users(self) -> bool:
        """Check if the user can manage other users."""
        return 'manage_users' in self.permissions
    
    def can_manage_system(self) -> bool:
        """Check if the user can manage system settings."""
        return 'manage_system' in self.permissions
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert the user to a dictionary."""
        data = asdict(self)
        
        # Remove sensitive information unless requested
        if not include_sensitive:
            data.pop('password_hash', None)
            data.pop('salt', None)
            data.pop('api_key', None)
        
        # Convert datetime objects to ISO strings
        for field in ['last_login', 'api_key_created', 'created_at', 'updated_at']:
            if data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User from a dictionary."""
        # Convert ISO strings back to datetime objects
        for field in ['last_login', 'api_key_created', 'created_at', 'updated_at']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    data[field] = None
        
        return cls(**data)
    
    def get_display_name(self) -> str:
        """Get the user's display name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    def get_initial_permissions(self) -> List[str]:
        """Get the initial permissions for a new user."""
        return self._get_default_permissions()
    
    def add_permission(self, permission: str) -> None:
        """Add a permission to the user."""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the user."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def update_role(self, new_role: str) -> None:
        """Update the user's role and permissions."""
        self.role = new_role
        self.permissions = self._get_default_permissions()
    
    def validate(self) -> List[str]:
        """Validate the user and return any validation errors."""
        errors = []
        
        # Required fields
        if not self.username:
            errors.append("username is required")
        if not self.email:
            errors.append("email is required")
        if not self.password_hash and not self.id:  # Allow existing users without password
            errors.append("password is required for new users")
        
        # Username validation
        if self.username and len(self.username) < 3:
            errors.append("username must be at least 3 characters long")
        if self.username and not self.username.replace('_', '').replace('-', '').isalnum():
            errors.append("username can only contain letters, numbers, hyphens, and underscores")
        
        # Email validation
        if self.email and '@' not in self.email:
            errors.append("email must be a valid email address")
        
        # Role validation
        valid_roles = ['user', 'admin', 'analyst', 'viewer']
        if self.role not in valid_roles:
            errors.append(f"role must be one of {valid_roles}")
        
        return errors
    
    def get_database_insert_query(self) -> tuple:
        """Get the SQL INSERT query and parameters for this user."""
        query = """
        INSERT INTO users (
            username, email, password_hash, salt, first_name, last_name, role,
            is_active, is_verified, last_login, permissions, api_key,
            api_key_created, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        import json
        params = (
            self.username, self.email, self.password_hash, self.salt,
            self.first_name, self.last_name, self.role, self.is_active,
            self.is_verified, self.last_login, json.dumps(self.permissions),
            self.api_key, self.api_key_created, self.created_at, self.updated_at
        )
        
        return query, params
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> 'User':
        """Create a User from a database row."""
        import json
        
        permissions = json.loads(row.get('permissions', '[]')) if row.get('permissions') else []
        
        return cls(
            id=row.get('id'),
            username=row.get('username', ''),
            email=row.get('email', ''),
            password_hash=row.get('password_hash', ''),
            salt=row.get('salt', ''),
            first_name=row.get('first_name', ''),
            last_name=row.get('last_name', ''),
            role=row.get('role', 'user'),
            is_active=row.get('is_active', True),
            is_verified=row.get('is_verified', False),
            last_login=row.get('last_login'),
            permissions=permissions,
            api_key=row.get('api_key'),
            api_key_created=row.get('api_key_created'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
