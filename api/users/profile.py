"""
User profile management endpoint for the Engineering Log Intelligence System.
Handles user profile operations (get, update, delete).
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any
import structlog

from ..models.user import User
from ..services.user_service import UserService
from ..auth.middleware import authenticate_request
from ..utils.monitoring import create_success_response, create_error_response, monitor_function

logger = structlog.get_logger(__name__)


@monitor_function("user_profile_get")
def get_handler(request) -> Dict[str, Any]:
    """
    Get user profile information.
    
    Headers:
    - Authorization: Bearer <token>
    """
    try:
        # Authenticate request
        auth_result = authenticate_request(request)
        if not auth_result['success']:
            return create_error_response(
                auth_result['message'],
                auth_result['error_code'],
                auth_result['status_code']
            )
        
        user = auth_result['user']
        user_service = UserService()
        
        # Get fresh user data from database
        fresh_user = user_service.get_user_by_id(user.id)
        if not fresh_user:
            return create_error_response(
                "User not found",
                "USER_NOT_FOUND",
                404
            )
        
        # Prepare response (exclude sensitive data)
        user_data = fresh_user.to_dict(include_sensitive=False)
        
        response_data = {
            "user": user_data,
            "message": "Profile retrieved successfully"
        }
        
        logger.info("User profile retrieved", user_id=user.id, username=user.username)
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error("Get user profile error", error=str(e))
        return create_error_response(
            "Failed to retrieve profile",
            "PROFILE_ERROR",
            500
        )


@monitor_function("user_profile_update")
def update_handler(request) -> Dict[str, Any]:
    """
    Update user profile information.
    
    Headers:
    - Authorization: Bearer <token>
    
    Expected request body:
    {
        "first_name": "string",
        "last_name": "string",
        "email": "string"  // optional, requires password confirmation
    }
    """
    try:
        # Authenticate request
        auth_result = authenticate_request(request)
        if not auth_result['success']:
            return create_error_response(
                auth_result['message'],
                auth_result['error_code'],
                auth_result['status_code']
            )
        
        user = auth_result['user']
        
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        user_service = UserService()
        
        # Get fresh user data from database
        fresh_user = user_service.get_user_by_id(user.id)
        if not fresh_user:
            return create_error_response(
                "User not found",
                "USER_NOT_FOUND",
                404
            )
        
        # Update allowed fields
        updated = False
        
        if 'first_name' in data:
            fresh_user.first_name = data['first_name'].strip()
            updated = True
        
        if 'last_name' in data:
            fresh_user.last_name = data['last_name'].strip()
            updated = True
        
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != fresh_user.email:
                # Check if email is already taken
                existing_user = user_service.get_user_by_email(new_email)
                if existing_user and existing_user.id != fresh_user.id:
                    return create_error_response(
                        "Email already in use",
                        "EMAIL_EXISTS",
                        409
                    )
                fresh_user.email = new_email
                updated = True
        
        if not updated:
            return create_error_response(
                "No valid fields to update",
                "NO_UPDATES",
                400
            )
        
        # Update user in database
        updated_user = user_service.update_user(fresh_user)
        
        # Prepare response (exclude sensitive data)
        user_data = updated_user.to_dict(include_sensitive=False)
        
        response_data = {
            "user": user_data,
            "message": "Profile updated successfully"
        }
        
        logger.info("User profile updated", user_id=user.id, username=user.username)
        return create_success_response(response_data)
        
    except json.JSONDecodeError:
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except ValueError as e:
        return create_error_response(
            str(e),
            "UPDATE_FAILED",
            400
        )
    except Exception as e:
        logger.error("Update user profile error", error=str(e))
        return create_error_response(
            "Failed to update profile",
            "PROFILE_ERROR",
            500
        )


@monitor_function("user_profile_delete")
def delete_handler(request) -> Dict[str, Any]:
    """
    Delete user account (soft delete).
    
    Headers:
    - Authorization: Bearer <token>
    
    Expected request body:
    {
        "password": "string"  // required for confirmation
    }
    """
    try:
        # Authenticate request
        auth_result = authenticate_request(request)
        if not auth_result['success']:
            return create_error_response(
                auth_result['message'],
                auth_result['error_code'],
                auth_result['status_code']
            )
        
        user = auth_result['user']
        
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        # Require password confirmation
        if 'password' not in data:
            return create_error_response(
                "Password confirmation required",
                "PASSWORD_REQUIRED",
                400
            )
        
        user_service = UserService()
        
        # Get fresh user data from database
        fresh_user = user_service.get_user_by_id(user.id)
        if not fresh_user:
            return create_error_response(
                "User not found",
                "USER_NOT_FOUND",
                404
            )
        
        # Verify password
        if not fresh_user.check_password(data['password']):
            return create_error_response(
                "Invalid password",
                "INVALID_PASSWORD",
                401
            )
        
        # Soft delete user
        success = user_service.delete_user(fresh_user.id)
        if not success:
            return create_error_response(
                "Failed to delete account",
                "DELETE_FAILED",
                500
            )
        
        response_data = {
            "message": "Account deleted successfully"
        }
        
        logger.info("User account deleted", user_id=user.id, username=user.username)
        return create_success_response(response_data)
        
    except json.JSONDecodeError:
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except Exception as e:
        logger.error("Delete user profile error", error=str(e))
        return create_error_response(
            "Failed to delete account",
            "PROFILE_ERROR",
            500
        )
