"""
Admin user management endpoint for the Engineering Log Intelligence System.
Handles admin operations for user management.
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


def _require_admin(user: User) -> bool:
    """Check if user has admin privileges."""
    return user.is_admin() and user.can_manage_users()


@monitor_function("admin_users_list")
def list_handler(request) -> Dict[str, Any]:
    """
    List all users (admin only).
    
    Headers:
    - Authorization: Bearer <token>
    
    Query parameters:
    - limit: Number of users to return (default: 100)
    - offset: Offset for pagination (default: 0)
    - active_only: Show only active users (default: true)
    - search: Search term for username/email/name
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
        
        # Check admin privileges
        if not _require_admin(user):
            return create_error_response(
                "Admin privileges required",
                "INSUFFICIENT_PRIVILEGES",
                403
            )
        
        # Get query parameters
        query_params = request.get('queryStringParameters') or {}
        limit = min(int(query_params.get('limit', 100)), 1000)
        offset = int(query_params.get('offset', 0))
        active_only = query_params.get('active_only', 'true').lower() == 'true'
        search = query_params.get('search', '').strip()
        
        user_service = UserService()
        
        # Get users
        if search:
            users = user_service.search_users(search, limit)
        else:
            users = user_service.get_all_users(limit, offset, active_only)
        
        # Prepare response (exclude sensitive data)
        users_data = [u.to_dict(include_sensitive=False) for u in users]
        
        # Get total count
        total_count = user_service.get_user_count(active_only)
        
        response_data = {
            "users": users_data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "active_only": active_only,
            "search": search
        }
        
        logger.info(
            "Users listed by admin",
            admin_user_id=user.id,
            count=len(users),
            search=search
        )
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error("Admin list users error", error=str(e))
        return create_error_response(
            "Failed to list users",
            "LIST_ERROR",
            500
        )


@monitor_function("admin_user_get")
def get_handler(request) -> Dict[str, Any]:
    """
    Get a specific user by ID (admin only).
    
    Headers:
    - Authorization: Bearer <token>
    
    Path parameters:
    - user_id: ID of the user to retrieve
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
        
        # Check admin privileges
        if not _require_admin(user):
            return create_error_response(
                "Admin privileges required",
                "INSUFFICIENT_PRIVILEGES",
                403
            )
        
        # Get user ID from path parameters
        path_params = request.get('pathParameters') or {}
        user_id = path_params.get('user_id')
        
        if not user_id:
            return create_error_response(
                "User ID required",
                "MISSING_USER_ID",
                400
            )
        
        try:
            user_id = int(user_id)
        except ValueError:
            return create_error_response(
                "Invalid user ID",
                "INVALID_USER_ID",
                400
            )
        
        user_service = UserService()
        target_user = user_service.get_user_by_id(user_id)
        
        if not target_user:
            return create_error_response(
                "User not found",
                "USER_NOT_FOUND",
                404
            )
        
        # Prepare response (exclude sensitive data)
        user_data = target_user.to_dict(include_sensitive=False)
        
        response_data = {
            "user": user_data,
            "message": "User retrieved successfully"
        }
        
        logger.info(
            "User retrieved by admin",
            admin_user_id=user.id,
            target_user_id=user_id
        )
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error("Admin get user error", error=str(e))
        return create_error_response(
            "Failed to retrieve user",
            "GET_ERROR",
            500
        )


@monitor_function("admin_user_update")
def update_handler(request) -> Dict[str, Any]:
    """
    Update a user (admin only).
    
    Headers:
    - Authorization: Bearer <token>
    
    Path parameters:
    - user_id: ID of the user to update
    
    Expected request body:
    {
        "first_name": "string",
        "last_name": "string",
        "email": "string",
        "role": "string",
        "is_active": boolean,
        "is_verified": boolean
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
        
        # Check admin privileges
        if not _require_admin(user):
            return create_error_response(
                "Admin privileges required",
                "INSUFFICIENT_PRIVILEGES",
                403
            )
        
        # Get user ID from path parameters
        path_params = request.get('pathParameters') or {}
        user_id = path_params.get('user_id')
        
        if not user_id:
            return create_error_response(
                "User ID required",
                "MISSING_USER_ID",
                400
            )
        
        try:
            user_id = int(user_id)
        except ValueError:
            return create_error_response(
                "Invalid user ID",
                "INVALID_USER_ID",
                400
            )
        
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        user_service = UserService()
        target_user = user_service.get_user_by_id(user_id)
        
        if not target_user:
            return create_error_response(
                "User not found",
                "USER_NOT_FOUND",
                404
            )
        
        # Update allowed fields
        updated = False
        
        if 'first_name' in data:
            target_user.first_name = data['first_name'].strip()
            updated = True
        
        if 'last_name' in data:
            target_user.last_name = data['last_name'].strip()
            updated = True
        
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != target_user.email:
                # Check if email is already taken
                existing_user = user_service.get_user_by_email(new_email)
                if existing_user and existing_user.id != target_user.id:
                    return create_error_response(
                        "Email already in use",
                        "EMAIL_EXISTS",
                        409
                    )
                target_user.email = new_email
                updated = True
        
        if 'role' in data:
            new_role = data['role'].strip().lower()
            valid_roles = ['user', 'admin', 'analyst', 'viewer']
            if new_role not in valid_roles:
                return create_error_response(
                    f"Invalid role. Must be one of: {', '.join(valid_roles)}",
                    "INVALID_ROLE",
                    400
                )
            target_user.update_role(new_role)
            updated = True
        
        if 'is_active' in data:
            target_user.is_active = bool(data['is_active'])
            updated = True
        
        if 'is_verified' in data:
            target_user.is_verified = bool(data['is_verified'])
            updated = True
        
        if not updated:
            return create_error_response(
                "No valid fields to update",
                "NO_UPDATES",
                400
            )
        
        # Update user in database
        updated_user = user_service.update_user(target_user)
        
        # Prepare response (exclude sensitive data)
        user_data = updated_user.to_dict(include_sensitive=False)
        
        response_data = {
            "user": user_data,
            "message": "User updated successfully"
        }
        
        logger.info(
            "User updated by admin",
            admin_user_id=user.id,
            target_user_id=user_id,
            updated_fields=list(data.keys())
        )
        
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
        logger.error("Admin update user error", error=str(e))
        return create_error_response(
            "Failed to update user",
            "UPDATE_ERROR",
            500
        )


@monitor_function("admin_user_delete")
def delete_handler(request) -> Dict[str, Any]:
    """
    Delete a user (admin only).
    
    Headers:
    - Authorization: Bearer <token>
    
    Path parameters:
    - user_id: ID of the user to delete
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
        
        # Check admin privileges
        if not _require_admin(user):
            return create_error_response(
                "Admin privileges required",
                "INSUFFICIENT_PRIVILEGES",
                403
            )
        
        # Get user ID from path parameters
        path_params = request.get('pathParameters') or {}
        user_id = path_params.get('user_id')
        
        if not user_id:
            return create_error_response(
                "User ID required",
                "MISSING_USER_ID",
                400
            )
        
        try:
            user_id = int(user_id)
        except ValueError:
            return create_error_response(
                "Invalid user ID",
                "INVALID_USER_ID",
                400
            )
        
        # Prevent admin from deleting themselves
        if user_id == user.id:
            return create_error_response(
                "Cannot delete your own account",
                "CANNOT_DELETE_SELF",
                400
            )
        
        user_service = UserService()
        target_user = user_service.get_user_by_id(user_id)
        
        if not target_user:
            return create_error_response(
                "User not found",
                "USER_NOT_FOUND",
                404
            )
        
        # Soft delete user
        success = user_service.delete_user(user_id)
        if not success:
            return create_error_response(
                "Failed to delete user",
                "DELETE_FAILED",
                500
            )
        
        response_data = {
            "message": "User deleted successfully"
        }
        
        logger.info(
            "User deleted by admin",
            admin_user_id=user.id,
            target_user_id=user_id,
            target_username=target_user.username
        )
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error("Admin delete user error", error=str(e))
        return create_error_response(
            "Failed to delete user",
            "DELETE_ERROR",
            500
        )
