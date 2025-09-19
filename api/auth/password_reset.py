"""
Password reset functionality for the Engineering Log Intelligence System.
Handles password reset requests and token validation.
"""

import json
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import structlog

from ..models.user import User
from ..services.user_service import UserService
from ..utils.monitoring import create_success_response, create_error_response, monitor_function

logger = structlog.get_logger(__name__)


class PasswordResetManager:
    """Manages password reset tokens and operations."""
    
    def __init__(self):
        """Initialize the password reset manager."""
        # In-memory storage for reset tokens (in production, use Redis or database)
        self.reset_tokens = {}  # {token: {user_id, expires_at, used}}
        self.token_expiry_hours = 1  # Tokens expire after 1 hour
        logger.info("Password reset manager initialized")
    
    def generate_reset_token(self, user_id: int) -> str:
        """Generate a password reset token for a user."""
        try:
            # Generate a secure random token
            token = secrets.token_urlsafe(32)
            
            # Set expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(hours=self.token_expiry_hours)
            
            # Store token
            self.reset_tokens[token] = {
                'user_id': user_id,
                'expires_at': expires_at,
                'used': False
            }
            
            logger.info("Password reset token generated", user_id=user_id, token=token[:10] + "...")
            return token
            
        except Exception as e:
            logger.error("Failed to generate reset token", error=str(e), user_id=user_id)
            raise
    
    def validate_reset_token(self, token: str) -> Optional[int]:
        """Validate a password reset token and return user ID."""
        try:
            if token not in self.reset_tokens:
                logger.warning("Invalid reset token", token=token[:10] + "...")
                return None
            
            token_data = self.reset_tokens[token]
            
            # Check if token is expired
            if datetime.now(timezone.utc) > token_data['expires_at']:
                logger.warning("Reset token expired", token=token[:10] + "...")
                del self.reset_tokens[token]
                return None
            
            # Check if token is already used
            if token_data['used']:
                logger.warning("Reset token already used", token=token[:10] + "...")
                return None
            
            return token_data['user_id']
            
        except Exception as e:
            logger.error("Failed to validate reset token", error=str(e))
            return None
    
    def mark_token_used(self, token: str) -> bool:
        """Mark a reset token as used."""
        try:
            if token in self.reset_tokens:
                self.reset_tokens[token]['used'] = True
                logger.info("Reset token marked as used", token=token[:10] + "...")
                return True
            return False
        except Exception as e:
            logger.error("Failed to mark token as used", error=str(e))
            return False
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens."""
        try:
            current_time = datetime.now(timezone.utc)
            expired_tokens = [
                token for token, data in self.reset_tokens.items()
                if current_time > data['expires_at']
            ]
            
            for token in expired_tokens:
                del self.reset_tokens[token]
            
            if expired_tokens:
                logger.info("Cleaned up expired tokens", count=len(expired_tokens))
                
        except Exception as e:
            logger.error("Failed to cleanup expired tokens", error=str(e))


# Global password reset manager
password_reset_manager = PasswordResetManager()


@monitor_function("password_reset_request")
def request_handler(request) -> Dict[str, Any]:
    """
    Handle password reset requests.
    
    Expected request body:
    {
        "email": "string"
    }
    """
    try:
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return create_error_response(
                "Email is required",
                "EMAIL_REQUIRED",
                400
            )
        
        # Validate email format
        if '@' not in email:
            return create_error_response(
                "Invalid email format",
                "INVALID_EMAIL",
                400
            )
        
        user_service = UserService()
        user = user_service.get_user_by_email(email)
        
        # Always return success to prevent email enumeration
        # But only generate token if user exists
        if user and user.is_active:
            try:
                # Generate reset token
                token = password_reset_manager.generate_reset_token(user.id)
                
                # In a real application, you would send an email here
                # For now, we'll just log the token (in production, remove this)
                logger.info(
                    "Password reset token generated",
                    user_id=user.id,
                    email=email,
                    token=token,
                    message="In production, send this token via email"
                )
                
                # Clean up expired tokens
                password_reset_manager.cleanup_expired_tokens()
                
            except Exception as e:
                logger.error("Failed to generate reset token", error=str(e), email=email)
                # Still return success to prevent enumeration
        
        response_data = {
            "message": "If the email exists, a password reset link has been sent",
            "email": email
        }
        
        return create_success_response(response_data)
        
    except json.JSONDecodeError:
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except Exception as e:
        logger.error("Password reset request error", error=str(e))
        return create_error_response(
            "Password reset request failed",
            "RESET_REQUEST_ERROR",
            500
        )


@monitor_function("password_reset_confirm")
def confirm_handler(request) -> Dict[str, Any]:
    """
    Handle password reset confirmation.
    
    Expected request body:
    {
        "token": "string",
        "new_password": "string"
    }
    """
    try:
        # Parse request body
        if hasattr(request, 'get_json'):
            data = request.get_json()
        else:
            data = json.loads(request.body) if hasattr(request, 'body') else {}
        
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not token:
            return create_error_response(
                "Reset token is required",
                "TOKEN_REQUIRED",
                400
            )
        
        if not new_password:
            return create_error_response(
                "New password is required",
                "PASSWORD_REQUIRED",
                400
            )
        
        # Validate password strength
        if len(new_password) < 8:
            return create_error_response(
                "Password must be at least 8 characters long",
                "WEAK_PASSWORD",
                400
            )
        
        # Validate reset token
        user_id = password_reset_manager.validate_reset_token(token)
        if not user_id:
            return create_error_response(
                "Invalid or expired reset token",
                "INVALID_TOKEN",
                400
            )
        
        # Get user and update password
        user_service = UserService()
        user = user_service.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            return create_error_response(
                "User not found or inactive",
                "USER_NOT_FOUND",
                404
            )
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        
        updated_user = user_service.update_user(user)
        
        # Mark token as used
        password_reset_manager.mark_token_used(token)
        
        response_data = {
            "message": "Password reset successfully",
            "user_id": updated_user.id
        }
        
        logger.info("Password reset completed", user_id=user_id, username=updated_user.username)
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
            "VALIDATION_FAILED",
            400
        )
    except Exception as e:
        logger.error("Password reset confirm error", error=str(e))
        return create_error_response(
            "Password reset confirmation failed",
            "RESET_CONFIRM_ERROR",
            500
        )


@monitor_function("password_change")
def change_handler(request) -> Dict[str, Any]:
    """
    Handle password change for authenticated users.
    
    Headers:
    - Authorization: Bearer <token>
    
    Expected request body:
    {
        "current_password": "string",
        "new_password": "string"
    }
    """
    try:
        # Authenticate request
        from ..auth.middleware import authenticate_request
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
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password:
            return create_error_response(
                "Current password is required",
                "CURRENT_PASSWORD_REQUIRED",
                400
            )
        
        if not new_password:
            return create_error_response(
                "New password is required",
                "NEW_PASSWORD_REQUIRED",
                400
            )
        
        # Validate password strength
        if len(new_password) < 8:
            return create_error_response(
                "New password must be at least 8 characters long",
                "WEAK_PASSWORD",
                400
            )
        
        # Verify current password
        if not user.check_password(current_password):
            return create_error_response(
                "Current password is incorrect",
                "INVALID_CURRENT_PASSWORD",
                401
            )
        
        # Update password
        user_service = UserService()
        success = user_service.update_user_password(user.id, new_password)
        
        if not success:
            return create_error_response(
                "Failed to update password",
                "PASSWORD_UPDATE_FAILED",
                500
            )
        
        response_data = {
            "message": "Password changed successfully"
        }
        
        logger.info("Password changed", user_id=user.id, username=user.username)
        return create_success_response(response_data)
        
    except json.JSONDecodeError:
        return create_error_response(
            "Invalid JSON in request body",
            "INVALID_JSON",
            400
        )
    except Exception as e:
        logger.error("Password change error", error=str(e))
        return create_error_response(
            "Password change failed",
            "PASSWORD_CHANGE_ERROR",
            500
        )
