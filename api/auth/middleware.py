"""
Authentication middleware for Vercel Functions.
Handles request authentication and authorization.
"""

from typing import Optional, Dict, Any, Callable
from functools import wraps
import structlog

from ..models.user import User
from .jwt_handler import get_jwt_handler
from ..utils.monitoring import create_error_response

logger = structlog.get_logger(__name__)


def require_auth(required_permissions: Optional[list] = None, required_role: Optional[str] = None):
    """
    Decorator to require authentication for a Vercel Function.
    
    Args:
        required_permissions: List of required permissions
        required_role: Required user role
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                # Extract token from request
                auth_header = request.headers.get("Authorization")
                if not auth_header:
                    logger.warning("No authorization header provided")
                    return create_error_response(
                        "Authentication required",
                        "AUTH_REQUIRED",
                        401
                    )
                
                jwt_handler = get_jwt_handler()
                token = jwt_handler.extract_token_from_header(auth_header)
                
                if not token:
                    logger.warning("Invalid authorization header format")
                    return create_error_response(
                        "Invalid authorization header",
                        "INVALID_AUTH_HEADER",
                        401
                    )
                
                # Get user from token
                user = jwt_handler.get_user_from_token(token)
                if not user:
                    logger.warning("Invalid or expired token")
                    return create_error_response(
                        "Invalid or expired token",
                        "INVALID_TOKEN",
                        401
                    )
                
                # Check permissions
                if required_permissions:
                    if not jwt_handler.validate_permissions(user, required_permissions):
                        logger.warning(
                            "Insufficient permissions",
                            user_id=user.id,
                            required_permissions=required_permissions
                        )
                        return create_error_response(
                            "Insufficient permissions",
                            "INSUFFICIENT_PERMISSIONS",
                            403
                        )
                
                # Check role
                if required_role:
                    if not jwt_handler.validate_role(user, required_role):
                        logger.warning(
                            "Insufficient role",
                            user_id=user.id,
                            required_role=required_role
                        )
                        return create_error_response(
                            "Insufficient role",
                            "INSUFFICIENT_ROLE",
                            403
                        )
                
                # Add user to request context
                request.user = user
                
                logger.info(
                    "Authentication successful",
                    user_id=user.id,
                    username=user.username,
                    role=user.role
                )
                
                return func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error("Authentication error", error=str(e))
                return create_error_response(
                    "Authentication error",
                    "AUTH_ERROR",
                    500
                )
        
        return wrapper
    return decorator


def optional_auth(func: Callable) -> Callable:
    """
    Decorator for optional authentication.
    Adds user to request if token is valid, but doesn't require it.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            # Try to extract and validate token
            auth_header = request.headers.get("Authorization")
            if auth_header:
                jwt_handler = get_jwt_handler()
                token = jwt_handler.extract_token_from_header(auth_header)
                
                if token:
                    user = jwt_handler.get_user_from_token(token)
                    if user:
                        request.user = user
                        logger.info("Optional authentication successful", user_id=user.id)
                    else:
                        request.user = None
                        logger.info("Optional authentication failed - invalid token")
                else:
                    request.user = None
                    logger.info("Optional authentication failed - invalid header")
            else:
                request.user = None
                logger.info("No authorization header for optional auth")
            
            return func(request, *args, **kwargs)
            
        except Exception as e:
            logger.error("Optional authentication error", error=str(e))
            request.user = None
            return func(request, *args, **kwargs)
    
    return wrapper


def get_current_user(request) -> Optional[User]:
    """Get the current authenticated user from request."""
    return getattr(request, 'user', None)


def is_authenticated(request) -> bool:
    """Check if the request is authenticated."""
    return get_current_user(request) is not None


def has_permission(request, permission: str) -> bool:
    """Check if the current user has a specific permission."""
    user = get_current_user(request)
    if not user:
        return False
    
    jwt_handler = get_jwt_handler()
    return jwt_handler.validate_permissions(user, [permission])


def has_role(request, role: str) -> bool:
    """Check if the current user has a specific role."""
    user = get_current_user(request)
    if not user:
        return False
    
    jwt_handler = get_jwt_handler()
    return jwt_handler.validate_role(user, role)


def is_admin(request) -> bool:
    """Check if the current user is an admin."""
    return has_role(request, "admin")


def can_manage_users(request) -> bool:
    """Check if the current user can manage other users."""
    return has_permission(request, "manage_users")


def can_manage_system(request) -> bool:
    """Check if the current user can manage system settings."""
    return has_permission(request, "manage_system")


def require_api_key(func: Callable) -> Callable:
    """
    Decorator to require API key authentication.
    Alternative to JWT for API access.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            # Extract API key from header
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                logger.warning("No API key provided")
                return create_error_response(
                    "API key required",
                    "API_KEY_REQUIRED",
                    401
                )
            
            # Validate API key
            from ..services.user_service import UserService
            user_service = UserService()
            user = user_service.get_user_by_api_key(api_key)
            
            if not user or not user.is_active:
                logger.warning("Invalid or inactive API key")
                return create_error_response(
                    "Invalid API key",
                    "INVALID_API_KEY",
                    401
                )
            
            # Add user to request context
            request.user = user
            
            logger.info("API key authentication successful", user_id=user.id)
            return func(request, *args, **kwargs)
            
        except Exception as e:
            logger.error("API key authentication error", error=str(e))
            return create_error_response(
                "API key authentication error",
                "API_KEY_AUTH_ERROR",
                500
            )
    
    return wrapper


def rate_limit(max_requests: int = 100, window_minutes: int = 60):
    """
    Decorator for rate limiting.
    Note: This is a simple in-memory implementation.
    For production, use Redis or a proper rate limiting service.
    """
    # Simple in-memory rate limiting (not suitable for production)
    request_counts = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                # Get client identifier
                client_ip = request.headers.get("X-Forwarded-For", "unknown")
                if "," in client_ip:
                    client_ip = client_ip.split(",")[0].strip()
                
                # Get user ID if authenticated
                user = get_current_user(request)
                if user:
                    client_id = f"user_{user.id}"
                else:
                    client_id = f"ip_{client_ip}"
                
                # Check rate limit
                now = datetime.now()
                window_start = now - timedelta(minutes=window_minutes)
                
                # Clean old entries
                if client_id in request_counts:
                    request_counts[client_id] = [
                        req_time for req_time in request_counts[client_id]
                        if req_time > window_start
                    ]
                else:
                    request_counts[client_id] = []
                
                # Check if limit exceeded
                if len(request_counts[client_id]) >= max_requests:
                    logger.warning(
                        "Rate limit exceeded",
                        client_id=client_id,
                        request_count=len(request_counts[client_id]),
                        max_requests=max_requests
                    )
                    return create_error_response(
                        "Rate limit exceeded",
                        "RATE_LIMIT_EXCEEDED",
                        429
                    )
                
                # Add current request
                request_counts[client_id].append(now)
                
                return func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error("Rate limiting error", error=str(e))
                # Don't block on rate limiting errors
                return func(request, *args, **kwargs)
        
        return wrapper
    return decorator
