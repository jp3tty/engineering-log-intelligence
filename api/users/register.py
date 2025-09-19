"""
User registration endpoint for the Engineering Log Intelligence System.
Handles new user registration with validation and security.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any
import structlog

from ..models.user import User
from ..services.user_service import UserService
from ..utils.monitoring import create_success_response, create_error_response, monitor_function

logger = structlog.get_logger(__name__)


@monitor_function("user_register")
def handler(request) -> Dict[str, Any]:
    """
    Handle user registration requests.
    
    Expected request body:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "first_name": "string",
        "last_name": "string",
        "role": "user"  // optional, defaults to "user"
    }
    """
    try:
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                "MISSING_FIELDS",
                400
            )
        
        # Extract user data
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', 'user').strip().lower()
        
        # Validate role
        valid_roles = ['user', 'analyst', 'viewer']
        if role not in valid_roles:
            return create_error_response(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}",
                "INVALID_ROLE",
                400
            )
        
        # Create user object
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # Set password (this will hash it)
        user.set_password(password)
        
        # Validate user data
        errors = user.validate()
        if errors:
            return create_error_response(
                f"Validation failed: {', '.join(errors)}",
                "VALIDATION_FAILED",
                400
            )
        
        # Create user in database
        user_service = UserService()
        try:
            created_user = user_service.create_user(user)
            
            # Prepare response (exclude sensitive data)
            user_data = created_user.to_dict(include_sensitive=False)
            
            response_data = {
                "user": user_data,
                "message": "User registered successfully",
                "api_key": created_user.api_key  # Include API key for immediate use
            }
            
            logger.info(
                "User registered successfully",
                user_id=created_user.id,
                username=created_user.username,
                role=created_user.role
            )
            
            return create_success_response(response_data)
            
        except ValueError as e:
            # Handle business logic errors (e.g., username/email already exists)
            return create_error_response(
                str(e),
                "REGISTRATION_FAILED",
                409  # Conflict
            )
        
    except json.JSONDecodeError:
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except Exception as e:
        logger.error("User registration error", error=str(e))
        return create_error_response(
            "User registration failed",
            "REGISTRATION_ERROR",
            500
        )
