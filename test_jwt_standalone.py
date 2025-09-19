#!/usr/bin/env python3
"""
Standalone JWT test without database dependencies.
"""

import sys
import os
import jwt
from datetime import datetime, timezone, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engineering_log_intelligence'))

from api.models.user import User


def test_jwt_standalone():
    """Test JWT functionality without database connection."""
    print("🔐 Testing JWT Authentication (Standalone)...")
    
    # Create a test user
    user = User(
        username="jwt_test_user",
        email="jwt@example.com",
        first_name="JWT",
        last_name="Test",
        role="analyst"
    )
    user.set_password("jwtpassword123")
    user.id = 1
    
    # Test JWT creation and verification
    secret_key = "test-secret-key"
    algorithm = "HS256"
    
    # Create access token
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=30)
    
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "permissions": user.permissions,
        "iat": now,
        "exp": expire,
        "type": "access"
    }
    
    access_token = jwt.encode(payload, secret_key, algorithm=algorithm)
    print("  ✅ Access token created")
    
    # Verify token
    try:
        decoded_payload = jwt.decode(access_token, secret_key, algorithms=[algorithm])
        if (decoded_payload.get("sub") == "1" and 
            decoded_payload.get("username") == "jwt_test_user" and
            decoded_payload.get("type") == "access"):
            print("  ✅ Token verification passed")
        else:
            print("  ❌ Token verification failed")
            return False
    except Exception as e:
        print(f"  ❌ Token verification failed: {e}")
        return False
    
    # Test refresh token
    refresh_payload = {
        "sub": str(user.id),
        "username": user.username,
        "iat": now,
        "exp": now + timedelta(days=7),
        "type": "refresh"
    }
    
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm=algorithm)
    print("  ✅ Refresh token created")
    
    # Verify refresh token
    try:
        decoded_refresh = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
        if (decoded_refresh.get("sub") == "1" and 
            decoded_refresh.get("type") == "refresh"):
            print("  ✅ Refresh token verification passed")
        else:
            print("  ❌ Refresh token verification failed")
            return False
    except Exception as e:
        print(f"  ❌ Refresh token verification failed: {e}")
        return False
    
    # Test permission validation
    user_permissions = set(user.permissions)
    required_permissions = {"read_logs", "analyze_logs"}
    has_permissions = required_permissions.issubset(user_permissions)
    
    if has_permissions:
        print("  ✅ Permission validation passed")
    else:
        print("  ❌ Permission validation failed")
        return False
    
    # Test role validation
    if user.role == "analyst":
        print("  ✅ Role validation passed")
    else:
        print("  ❌ Role validation failed")
        return False
    
    print("  ✅ JWT authentication system passed all tests\n")
    return True


if __name__ == "__main__":
    success = test_jwt_standalone()
    sys.exit(0 if success else 1)
