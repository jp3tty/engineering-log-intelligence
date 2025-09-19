"""
Authentication endpoints for the Engineering Log Intelligence System.
Handles user login, logout, and token management.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any
import structlog

from ..models.user import User
from ..services.user_service import UserService
from ..auth.jwt_handler import get_jwt_handler
from ..utils.monitoring import create_success_response, create_error_response, monitor_function

logger = structlog.get_logger(__name__)


@monitor_function("auth_login")
def handler(request) -> Dict[str, Any]:
    """
    Handle user login and return JWT tokens.
    
    Expected request body:
    {
        "username": "string",
        "password": "string"
    }
    """
    try:
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            logger.warning("Missing username or password")
            return create_error_response(
                "Username and password are required",
                "MISSING_CREDENTIALS",
                400
            )
        
        # Authenticate user
        user_service = UserService()
        user = user_service.authenticate_user(username, password)
        
        if not user:
            logger.warning("Authentication failed", username=username)
            return create_error_response(
                "Invalid username or password",
                "INVALID_CREDENTIALS",
                401
            )
        
        if not user.is_active:
            logger.warning("Inactive user attempted login", user_id=user.id, username=username)
            return create_error_response(
                "Account is inactive",
                "ACCOUNT_INACTIVE",
                401
            )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        user_service.update_user(user)
        
        # Create JWT tokens
        jwt_handler = get_jwt_handler()
        tokens = jwt_handler.create_token_pair(user)
        
        # Prepare response data
        response_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "permissions": user.permissions,
                "is_verified": user.is_verified,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "tokens": tokens
        }
        
        logger.info("User login successful", user_id=user.id, username=username)
        return create_success_response(response_data)
        
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in request body")
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except Exception as e:
        logger.error("Login error", error=str(e))
        return create_error_response(
            "Login failed",
            "LOGIN_ERROR",
            500
        )


@monitor_function("auth_logout")
def logout_handler(request) -> Dict[str, Any]:
    """
    Handle user logout.
    Note: JWT tokens are stateless, so this is mainly for logging.
    """
    try:
        # Get user from token if provided
        auth_header = request.headers.get("Authorization")
        user = None
        
        if auth_header:
            jwt_handler = get_jwt_handler()
            token = jwt_handler.extract_token_from_header(auth_header)
            if token:
                user = jwt_handler.get_user_from_token(token)
        
        if user:
            logger.info("User logout", user_id=user.id, username=user.username)
        else:
            logger.info("Anonymous logout")
        
        return create_success_response({"message": "Logout successful"})
        
    except Exception as e:
        logger.error("Logout error", error=str(e))
        return create_error_response(
            "Logout failed",
            "LOGOUT_ERROR",
            500
        )


@monitor_function("auth_refresh")
def refresh_handler(request) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    Expected request body:
    {
        "refresh_token": "string"
    }
    """
    try:
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            logger.warning("No refresh token provided")
            return create_error_response(
                "Refresh token is required",
                "MISSING_REFRESH_TOKEN",
                400
            )
        
        # Refresh the token
        jwt_handler = get_jwt_handler()
        tokens = jwt_handler.refresh_access_token(refresh_token)
        
        if not tokens:
            logger.warning("Invalid refresh token")
            return create_error_response(
                "Invalid or expired refresh token",
                "INVALID_REFRESH_TOKEN",
                401
            )
        
        logger.info("Token refresh successful")
        return create_success_response({"tokens": tokens})
        
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in request body")
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        return create_error_response(
            "Token refresh failed",
            "REFRESH_ERROR",
            500
        )


@monitor_function("auth_me")
def me_handler(request) -> Dict[str, Any]:
    """
    Get current user information.
    Requires authentication.
    """
    try:
        # Get user from token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning("No authorization header")
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
        
        user = jwt_handler.get_user_from_token(token)
        if not user:
            logger.warning("Invalid or expired token")
            return create_error_response(
                "Invalid or expired token",
                "INVALID_TOKEN",
                401
            )
        
        # Prepare user data
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "permissions": user.permissions,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        logger.info("User info retrieved", user_id=user.id, username=user.username)
        return create_success_response({"user": user_data})
        
    except Exception as e:
        logger.error("Get user info error", error=str(e))
        return create_error_response(
            "Failed to get user information",
            "USER_INFO_ERROR",
            500
        )


@monitor_function("auth_register")
def register_handler(request) -> Dict[str, Any]:
    """
    Register a new user.
    
    Expected request body:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "first_name": "string",
        "last_name": "string"
    }
    """
    try:
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if not all([username, email, password]):
            logger.warning("Missing required fields for registration")
            return create_error_response(
                "Username, email, and password are required",
                "MISSING_REQUIRED_FIELDS",
                400
            )
        
        # Create new user
        user_service = UserService()
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role="user"  # Default role
        )
        
        # Set password
        user.set_password(password)
        
        # Create user in database
        created_user = user_service.create_user(user)
        
        if not created_user:
            logger.warning("Failed to create user", username=username, email=email)
            return create_error_response(
                "Failed to create user",
                "USER_CREATION_FAILED",
                500
            )
        
        # Create JWT tokens
        jwt_handler = get_jwt_handler()
        tokens = jwt_handler.create_token_pair(created_user)
        
        # Prepare response data
        response_data = {
            "user": {
                "id": created_user.id,
                "username": created_user.username,
                "email": created_user.email,
                "first_name": created_user.first_name,
                "last_name": created_user.last_name,
                "role": created_user.role,
                "permissions": created_user.permissions,
                "is_verified": created_user.is_verified
            },
            "tokens": tokens
        }
        
        logger.info("User registration successful", user_id=created_user.id, username=username)
        return create_success_response(response_data, 201)
        
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in request body")
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except ValueError as e:
        logger.warning("Validation error", error=str(e))
        return create_error_response(
            str(e),
            "VALIDATION_ERROR",
            400
        )
    except Exception as e:
        logger.error("Registration error", error=str(e))
        return create_error_response(
            "Registration failed",
            "REGISTRATION_ERROR",
            500
        )
