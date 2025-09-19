"""
JWT authentication handler for the Engineering Log Intelligence System.
Handles JWT token creation, validation, and user authentication.
"""

import os
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import structlog

from ..models.user import User
from ..services.user_service import UserService

logger = structlog.get_logger(__name__)


class JWTHandler:
    """Handles JWT token operations."""
    
    def __init__(self):
        """Initialize the JWT handler."""
        self.secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        if self.secret_key == "dev-secret-key":
            logger.warning("Using default JWT secret key - not secure for production")
        
        logger.info("JWT handler initialized", algorithm=self.algorithm)
    
    def create_access_token(self, user: User) -> str:
        """Create an access token for a user."""
        try:
            now = datetime.now(timezone.utc)
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
            
            payload = {
                "sub": str(user.id),  # Subject (user ID)
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "permissions": user.permissions,
                "iat": now,  # Issued at
                "exp": expire,  # Expiration time
                "type": "access"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(
                "Access token created",
                user_id=user.id,
                username=user.username,
                expires_at=expire.isoformat()
            )
            
            return token
            
        except Exception as e:
            logger.error("Failed to create access token", error=str(e), user_id=user.id)
            raise
    
    def create_refresh_token(self, user: User) -> str:
        """Create a refresh token for a user."""
        try:
            now = datetime.now(timezone.utc)
            expire = now + timedelta(days=self.refresh_token_expire_days)
            
            payload = {
                "sub": str(user.id),
                "username": user.username,
                "iat": now,
                "exp": expire,
                "type": "refresh"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(
                "Refresh token created",
                user_id=user.id,
                username=user.username,
                expires_at=expire.isoformat()
            )
            
            return token
            
        except Exception as e:
            logger.error("Failed to create refresh token", error=str(e), user_id=user.id)
            raise
    
    def create_token_pair(self, user: User) -> Dict[str, str]:
        """Create both access and refresh tokens."""
        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token expired", token_type=payload.get("type"))
                return None
            
            logger.info("Token verified", user_id=payload.get("sub"), type=payload.get("type"))
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token signature expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", error=str(e))
            return None
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh an access token using a refresh token."""
        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                logger.warning("Invalid refresh token")
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("No user ID in refresh token")
                return None
            
            # Get user from database
            user_service = UserService()
            user = user_service.get_user_by_id(int(user_id))
            if not user or not user.is_active:
                logger.warning("User not found or inactive", user_id=user_id)
                return None
            
            # Create new token pair
            return self.create_token_pair(user)
            
        except Exception as e:
            logger.error("Failed to refresh access token", error=str(e))
            return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from a valid token."""
        try:
            payload = self.verify_token(token)
            if not payload or payload.get("type") != "access":
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user_service = UserService()
            user = user_service.get_user_by_id(int(user_id))
            
            if user and user.is_active:
                return user
            else:
                logger.warning("User not found or inactive", user_id=user_id)
                return None
                
        except Exception as e:
            logger.error("Failed to get user from token", error=str(e))
            return None
    
    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """Extract token from Authorization header."""
        try:
            if not authorization_header:
                return None
            
            # Expected format: "Bearer <token>"
            parts = authorization_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                logger.warning("Invalid authorization header format")
                return None
            
            return parts[1]
            
        except Exception as e:
            logger.error("Failed to extract token from header", error=str(e))
            return None
    
    def validate_permissions(self, user: User, required_permissions: list) -> bool:
        """Validate if user has required permissions."""
        try:
            if not required_permissions:
                return True
            
            user_permissions = set(user.permissions)
            required_permissions_set = set(required_permissions)
            
            has_permissions = required_permissions_set.issubset(user_permissions)
            
            if not has_permissions:
                logger.warning(
                    "Insufficient permissions",
                    user_id=user.id,
                    username=user.username,
                    user_permissions=user_permissions,
                    required_permissions=required_permissions
                )
            
            return has_permissions
            
        except Exception as e:
            logger.error("Failed to validate permissions", error=str(e))
            return False
    
    def validate_role(self, user: User, required_role: str) -> bool:
        """Validate if user has required role."""
        try:
            has_role = user.role == required_role
            
            if not has_role:
                logger.warning(
                    "Insufficient role",
                    user_id=user.id,
                    username=user.username,
                    user_role=user.role,
                    required_role=required_role
                )
            
            return has_role
            
        except Exception as e:
            logger.error("Failed to validate role", error=str(e))
            return False
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get information about a token without verification."""
        try:
            # Decode without verification to get payload
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check if token is expired
            exp = payload.get("exp")
            is_expired = False
            if exp:
                exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
                is_expired = exp_time < datetime.now(timezone.utc)
            
            return {
                "user_id": payload.get("sub"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "permissions": payload.get("permissions", []),
                "type": payload.get("type"),
                "issued_at": payload.get("iat"),
                "expires_at": payload.get("exp"),
                "is_expired": is_expired
            }
            
        except Exception as e:
            logger.error("Failed to get token info", error=str(e))
            return None


# Global JWT handler instance
jwt_handler = JWTHandler()


def get_jwt_handler() -> JWTHandler:
    """Get the global JWT handler instance."""
    return jwt_handler
