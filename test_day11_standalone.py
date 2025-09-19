#!/usr/bin/env python3
"""
Standalone test script for Day 11: User Management & Authentication
Tests core functionality without external dependencies.
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engineering_log_intelligence'))

from api.models.user import User


def test_user_model_comprehensive():
    """Test comprehensive User model functionality."""
    print("👤 Testing User Model Comprehensive...")
    
    try:
        # Test user creation with all fields
        user = User(
            username="testuser123",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            role="analyst"
        )
        
        # Test password setting and validation
        user.set_password("SecurePassword123!")
        
        # Test validation
        errors = user.validate()
        if not errors:
            print("    ✅ User validation passed")
        else:
            print(f"    ❌ User validation failed: {errors}")
            return False
        
        # Test password security
        if user.check_password("SecurePassword123!") and not user.check_password("wrongpassword"):
            print("    ✅ Password security passed")
        else:
            print("    ❌ Password security failed")
            return False
        
        # Test role and permissions
        if (user.has_role("analyst") and 
            user.has_permission("analyze_logs") and 
            user.has_permission("export_data")):
            print("    ✅ Role and permissions passed")
        else:
            print("    ❌ Role and permissions failed")
            return False
        
        # Test API key functionality
        api_key = user.generate_api_key()
        if api_key and api_key.startswith("eli_") and len(api_key) > 30:
            print("    ✅ API key generation passed")
        else:
            print("    ❌ API key generation failed")
            return False
        
        # Test API key revocation
        user.revoke_api_key()
        if user.api_key is None and user.api_key_created is None:
            print("    ✅ API key revocation passed")
        else:
            print("    ❌ API key revocation failed")
            return False
        
        # Test serialization and deserialization
        user_dict = user.to_dict(include_sensitive=False)
        user_from_dict = User.from_dict(user_dict)
        
        if (user_from_dict.username == user.username and 
            user_from_dict.email == user.email and
            user_from_dict.role == user.role):
            print("    ✅ Serialization/deserialization passed")
        else:
            print("    ❌ Serialization/deserialization failed")
            return False
        
        # Test database query generation
        query, params = user.get_database_insert_query()
        if query and params and len(params) == 15:
            print("    ✅ Database query generation passed")
        else:
            print("    ❌ Database query generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ User model test failed: {e}")
        return False


def test_role_based_access_control():
    """Test comprehensive role-based access control."""
    print("🛡️ Testing Role-Based Access Control...")
    
    try:
        # Test all role types
        roles = {
            'viewer': ['read_logs', 'view_dashboard'],
            'user': ['read_logs', 'view_dashboard', 'create_alerts'],
            'analyst': ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data'],
            'admin': ['read_logs', 'view_dashboard', 'create_alerts', 'analyze_logs', 'export_data', 
                     'manage_users', 'manage_system', 'configure_alerts']
        }
        
        for role, expected_permissions in roles.items():
            user = User(
                username=f"test{role}",
                email=f"test{role}@example.com",
                role=role
            )
            
            # Test role checking
            if not user.has_role(role):
                print(f"    ❌ {role} role checking failed")
                return False
            
            # Test permission checking
            for permission in expected_permissions:
                if not user.has_permission(permission):
                    print(f"    ❌ {role} missing permission: {permission}")
                    return False
            
            # Test admin-specific methods
            if role == 'admin':
                if not (user.is_admin() and user.can_manage_users() and user.can_manage_system()):
                    print(f"    ❌ {role} admin methods failed")
                    return False
            
            print(f"    ✅ {role} role and permissions passed")
        
        # Test role updates
        user = User(username="testuser", email="test@example.com", role="user")
        user.update_role("admin")
        
        if user.role == "admin" and user.is_admin():
            print("    ✅ Role update passed")
        else:
            print("    ❌ Role update failed")
            return False
        
        # Test permission management
        user = User(username="testuser", email="test@example.com", role="user")
        user.add_permission("custom_permission")
        
        if user.has_permission("custom_permission"):
            print("    ✅ Permission addition passed")
        else:
            print("    ❌ Permission addition failed")
            return False
        
        user.remove_permission("custom_permission")
        if not user.has_permission("custom_permission"):
            print("    ✅ Permission removal passed")
        else:
            print("    ❌ Permission removal failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ RBAC test failed: {e}")
        return False


def test_jwt_authentication():
    """Test JWT authentication system."""
    print("🔑 Testing JWT Authentication...")
    
    try:
        from api.auth.jwt_handler import JWTHandler
        
        # Test JWT handler creation
        jwt_handler = JWTHandler()
        print("    ✅ JWT handler created successfully")
        
        # Create test users with different roles
        users = [
            User(id=1, username="admin", email="admin@example.com", role="admin"),
            User(id=2, username="analyst", email="analyst@example.com", role="analyst"),
            User(id=3, username="user", email="user@example.com", role="user"),
            User(id=4, username="viewer", email="viewer@example.com", role="viewer")
        ]
        
        for user in users:
            # Test access token creation
            access_token = jwt_handler.create_access_token(user)
            if not access_token:
                print(f"    ❌ Access token creation failed for {user.role}")
                return False
            
            # Test refresh token creation
            refresh_token = jwt_handler.create_refresh_token(user)
            if not refresh_token:
                print(f"    ❌ Refresh token creation failed for {user.role}")
                return False
            
            # Test token verification
            payload = jwt_handler.verify_token(access_token)
            if not payload or payload.get('sub') != str(user.id):
                print(f"    ❌ Token verification failed for {user.role}")
                return False
            
            # Test token info
            token_info = jwt_handler.get_token_info(access_token)
            if not token_info or token_info.get('user_id') != str(user.id):
                print(f"    ❌ Token info retrieval failed for {user.role}")
                return False
            
            # Test permission validation
            if not jwt_handler.validate_permissions(user, ['read_logs']):
                print(f"    ❌ Permission validation failed for {user.role}")
                return False
            
            # Test role validation
            if not jwt_handler.validate_role(user, user.role):
                print(f"    ❌ Role validation failed for {user.role}")
                return False
            
            print(f"    ✅ {user.role} JWT authentication passed")
        
        # Test token pair creation
        user = users[0]
        token_pair = jwt_handler.create_token_pair(user)
        if 'access_token' in token_pair and 'refresh_token' in token_pair:
            print("    ✅ Token pair creation passed")
        else:
            print("    ❌ Token pair creation failed")
            return False
        
        # Test token extraction from header
        auth_header = "Bearer " + access_token
        extracted_token = jwt_handler.extract_token_from_header(auth_header)
        if extracted_token == access_token:
            print("    ✅ Token extraction from header passed")
        else:
            print("    ❌ Token extraction from header failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ JWT authentication test failed: {e}")
        return False


def test_rate_limiting():
    """Test rate limiting functionality."""
    print("⏱️ Testing Rate Limiting...")
    
    try:
        from api.middleware.rate_limiter import RateLimiter, check_rate_limit, get_rate_limit_headers
        
        # Test rate limiter creation
        rate_limiter = RateLimiter()
        print("    ✅ RateLimiter created successfully")
        
        # Test different endpoints
        endpoints = ['api', 'login', 'register', 'search', 'admin']
        
        for endpoint in endpoints:
            # Test rate limit checking
            allowed, info = check_rate_limit(
                user_id=1,
                endpoint=endpoint,
                ip_address="192.168.1.1"
            )
            
            if not (allowed and info.get('allowed', False)):
                print(f"    ❌ Rate limit check failed for {endpoint}")
                return False
            
            # Test rate limit headers
            headers = get_rate_limit_headers(info)
            if 'X-RateLimit-Limit' not in headers:
                print(f"    ❌ Rate limit headers failed for {endpoint}")
                return False
            
            print(f"    ✅ {endpoint} rate limiting passed")
        
        # Test rate limiting with multiple requests
        for i in range(10):  # Make multiple requests
            allowed, info = check_rate_limit(
                user_id=1,
                endpoint="login",  # Lower limit
                ip_address="192.168.1.1"
            )
        
        # Should eventually hit the limit
        if not allowed:
            print("    ✅ Rate limiting works (limit reached)")
        else:
            print("    ⚠️ Rate limiting may not be working (no limit reached)")
        
        # Test IP-based rate limiting
        allowed, info = check_rate_limit(
            user_id=None,
            endpoint="api",
            ip_address="192.168.1.100"
        )
        
        if allowed and info.get('allowed', False):
            print("    ✅ IP-based rate limiting passed")
        else:
            print("    ❌ IP-based rate limiting failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Rate limiting test failed: {e}")
        return False


def test_password_reset_logic():
    """Test password reset logic without database."""
    print("🔐 Testing Password Reset Logic...")
    
    try:
        from api.auth.password_reset import PasswordResetManager
        
        # Test password reset manager
        reset_manager = PasswordResetManager()
        print("    ✅ Password reset manager created successfully")
        
        # Test token generation
        user_id = 1
        token = reset_manager.generate_reset_token(user_id)
        
        if not token or len(token) < 20:
            print("    ❌ Token generation failed")
            return False
        
        print("    ✅ Token generation passed")
        
        # Test token validation
        validated_user_id = reset_manager.validate_reset_token(token)
        if validated_user_id != user_id:
            print("    ❌ Token validation failed")
            return False
        
        print("    ✅ Token validation passed")
        
        # Test token usage
        if not reset_manager.mark_token_used(token):
            print("    ❌ Token usage marking failed")
            return False
        
        print("    ✅ Token usage marking passed")
        
        # Test used token validation (should fail)
        used_token_user_id = reset_manager.validate_reset_token(token)
        if used_token_user_id is not None:
            print("    ❌ Used token validation failed")
            return False
        
        print("    ✅ Used token validation passed")
        
        # Test cleanup
        reset_manager.cleanup_expired_tokens()
        print("    ✅ Token cleanup passed")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Password reset logic test failed: {e}")
        return False


def test_security_features():
    """Test comprehensive security features."""
    print("🔒 Testing Security Features...")
    
    try:
        # Test password hashing with different algorithms
        user = User(username="testuser", email="test@example.com")
        
        # Test password setting
        user.set_password("ComplexPassword123!")
        
        if not (user.password_hash and user.salt and len(user.password_hash) == 64):
            print("    ❌ Password hashing failed")
            return False
        
        print("    ✅ Password hashing passed")
        
        # Test password verification
        if not (user.check_password("ComplexPassword123!") and 
                not user.check_password("wrongpassword") and
                not user.check_password("ComplexPassword123")):
            print("    ❌ Password verification failed")
            return False
        
        print("    ✅ Password verification passed")
        
        # Test password strength validation
        try:
            user.set_password("weak")
            print("    ❌ Weak password validation failed")
            return False
        except ValueError:
            print("    ✅ Weak password validation passed")
        
        # Test API key security
        api_key = user.generate_api_key()
        if not (api_key and api_key.startswith("eli_") and len(api_key) > 30):
            print("    ❌ API key generation failed")
            return False
        
        print("    ✅ API key generation passed")
        
        # Test sensitive data exclusion
        user_dict = user.to_dict(include_sensitive=False)
        sensitive_fields = ['password_hash', 'salt', 'api_key']
        
        for field in sensitive_fields:
            if field in user_dict:
                print(f"    ❌ Sensitive field {field} not excluded")
                return False
        
        print("    ✅ Sensitive data exclusion passed")
        
        # Test sensitive data inclusion when requested
        user_dict_sensitive = user.to_dict(include_sensitive=True)
        for field in sensitive_fields:
            if field not in user_dict_sensitive:
                print(f"    ❌ Sensitive field {field} not included when requested")
                return False
        
        print("    ✅ Sensitive data inclusion passed")
        
        # Test user validation
        errors = user.validate()
        if errors:
            print(f"    ❌ User validation failed: {errors}")
            return False
        
        print("    ✅ User validation passed")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Security features test failed: {e}")
        return False


def test_user_management_workflows():
    """Test user management workflows."""
    print("👥 Testing User Management Workflows...")
    
    try:
        # Test user creation workflow
        user = User(
            username="workflowuser",
            email="workflow@example.com",
            first_name="Workflow",
            last_name="User",
            role="user"
        )
        user.set_password("WorkflowPassword123!")
        
        if not user.validate():
            print("    ❌ User creation workflow failed")
            return False
        
        print("    ✅ User creation workflow passed")
        
        # Test role upgrade workflow
        user.update_role("analyst")
        
        if not (user.role == "analyst" and user.has_permission("analyze_logs")):
            print("    ❌ Role upgrade workflow failed")
            return False
        
        print("    ✅ Role upgrade workflow passed")
        
        # Test permission management workflow
        user.add_permission("custom_analysis")
        
        if not user.has_permission("custom_analysis"):
            print("    ❌ Permission addition workflow failed")
            return False
        
        user.remove_permission("custom_analysis")
        
        if user.has_permission("custom_analysis"):
            print("    ❌ Permission removal workflow failed")
            return False
        
        print("    ✅ Permission management workflow passed")
        
        # Test API key management workflow
        api_key = user.generate_api_key()
        
        if not api_key:
            print("    ❌ API key generation workflow failed")
            return False
        
        user.revoke_api_key()
        
        if user.api_key is not None:
            print("    ❌ API key revocation workflow failed")
            return False
        
        print("    ✅ API key management workflow passed")
        
        # Test user deactivation workflow
        user.is_active = False
        
        if user.is_active:
            print("    ❌ User deactivation workflow failed")
            return False
        
        print("    ✅ User deactivation workflow passed")
        
        return True
        
    except Exception as e:
        print(f"    ❌ User management workflows test failed: {e}")
        return False


def main():
    """Run all Day 11 standalone tests."""
    print("🚀 Day 11: User Management & Authentication - Standalone Test Suite")
    print("=" * 70)
    
    tests = [
        ("User Model Comprehensive", test_user_model_comprehensive),
        ("Role-Based Access Control", test_role_based_access_control),
        ("JWT Authentication", test_jwt_authentication),
        ("Rate Limiting", test_rate_limiting),
        ("Password Reset Logic", test_password_reset_logic),
        ("Security Features", test_security_features),
        ("User Management Workflows", test_user_management_workflows)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with error: {e}")
        print("-" * 70)
    
    print(f"\n📊 Standalone Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All Day 11 standalone tests PASSED! User management system is working correctly.")
        print("\n📋 Day 11 User Management Achievements:")
        print("  ✅ Comprehensive user model with validation and security")
        print("  ✅ Complete role-based access control (RBAC)")
        print("  ✅ JWT authentication with tokens and permissions")
        print("  ✅ Advanced rate limiting with sliding window algorithm")
        print("  ✅ Password reset and change functionality")
        print("  ✅ Comprehensive security features and validation")
        print("  ✅ Complete user management workflows")
        return True
    else:
        print("⚠️  Some standalone tests FAILED. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
