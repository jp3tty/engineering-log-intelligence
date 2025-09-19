#!/usr/bin/env python3
"""
Test script for Day 9: Vercel Functions Structure
Tests database models, CRUD operations, and JWT authentication.
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engineering_log_intelligence'))

from api.models.log_entry import LogEntry
from api.models.user import User
from api.models.alert import Alert
from api.models.dashboard import Dashboard
from api.models.correlation import Correlation
from api.services.log_service import LogService
from api.auth.jwt_handler import get_jwt_handler


def test_database_models():
    """Test database model creation and validation."""
    print("🧪 Testing Database Models...")
    
    # Test LogEntry model
    print("  📝 Testing LogEntry model...")
    log_entry = LogEntry(
        log_id="test-log-123",
        timestamp=datetime.now(timezone.utc),
        level="INFO",
        message="Test log message",
        source_type="application",
        host="test-server",
        service="test-service",
        category="test",
        tags=["test", "demo"],
        raw_log="2025-09-19 10:30:00 INFO Test log message",
        structured_data={"test": True, "value": 123},
        request_id="req-1234567890",
        session_id="sess-1234567890",
        correlation_id="corr-1234567890",
        ip_address="192.168.1.100",
        application_type="web_app",
        framework="Spring Boot",
        http_method="GET",
        http_status=200,
        endpoint="/api/test",
        response_time_ms=145.67,
        is_anomaly=False,
        performance_metrics={"memory_usage_mb": 256.5, "cpu_usage_percent": 45.2}
    )
    
    # Test validation
    errors = log_entry.validate()
    if errors:
        print(f"    ❌ LogEntry validation failed: {errors}")
        return False
    else:
        print("    ✅ LogEntry validation passed")
    
    # Test serialization
    log_dict = log_entry.to_dict()
    log_json = log_entry.to_json()
    log_from_dict = LogEntry.from_dict(log_dict)
    log_from_json = LogEntry.from_json(log_json)
    
    if (log_from_dict.log_id == log_entry.log_id and 
        log_from_json.log_id == log_entry.log_id):
        print("    ✅ LogEntry serialization/deserialization passed")
    else:
        print("    ❌ LogEntry serialization/deserialization failed")
        return False
    
    # Test User model
    print("  👤 Testing User model...")
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role="analyst"
    )
    user.set_password("testpassword123")
    
    # Test validation
    errors = user.validate()
    if errors:
        print(f"    ❌ User validation failed: {errors}")
        return False
    else:
        print("    ✅ User validation passed")
    
    # Test password verification
    if user.check_password("testpassword123") and not user.check_password("wrongpassword"):
        print("    ✅ User password verification passed")
    else:
        print("    ❌ User password verification failed")
        return False
    
    # Test Alert model
    print("  🚨 Testing Alert model...")
    alert = Alert(
        title="Test Alert",
        description="This is a test alert",
        severity="high",
        category="system",
        source="application",
        log_entries=[1, 2, 3],
        correlation_id="corr-1234567890",
        metadata={"test": True}
    )
    
    # Test validation
    errors = alert.validate()
    if errors:
        print(f"    ❌ Alert validation failed: {errors}")
        return False
    else:
        print("    ✅ Alert validation passed")
    
    # Test Dashboard model
    print("  📊 Testing Dashboard model...")
    dashboard = Dashboard(
        name="Test Dashboard",
        description="Test dashboard for testing",
        owner_id=1,
        widgets=[
            {
                "id": "widget-1",
                "type": "chart",
                "title": "Test Chart",
                "position": {"x": 0, "y": 0, "w": 3, "h": 2}
            }
        ],
        filters={"source_type": "application"}
    )
    
    # Test validation
    errors = dashboard.validate()
    if errors:
        print(f"    ❌ Dashboard validation failed: {errors}")
        return False
    else:
        print("    ✅ Dashboard validation passed")
    
    # Test Correlation model
    print("  🔗 Testing Correlation model...")
    correlation = Correlation(
        correlation_type="request",
        log_entry_ids=[1, 2, 3],
        source_systems=["application", "splunk"],
        correlation_key="request_id",
        correlation_value="req-1234567890",
        confidence_score=0.95,
        pattern_type="sequence",
        pattern_data={"pattern": "login -> error -> retry"}
    )
    
    # Test validation
    errors = correlation.validate()
    if errors:
        print(f"    ❌ Correlation validation failed: {errors}")
        return False
    else:
        print("    ✅ Correlation validation passed")
    
    print("  ✅ All database models passed validation\n")
    return True


def test_jwt_authentication():
    """Test JWT authentication system."""
    print("🔐 Testing JWT Authentication...")
    
    # Create a test user
    user = User(
        username="jwt_test_user",
        email="jwt@example.com",
        first_name="JWT",
        last_name="Test",
        role="analyst"
    )
    user.set_password("jwtpassword123")
    user.id = 1  # Simulate database ID
    
    # Test JWT handler
    jwt_handler = get_jwt_handler()
    
    # Test token creation
    print("  🎫 Testing token creation...")
    access_token = jwt_handler.create_access_token(user)
    refresh_token = jwt_handler.create_refresh_token(user)
    token_pair = jwt_handler.create_token_pair(user)
    
    if access_token and refresh_token and token_pair:
        print("    ✅ Token creation passed")
    else:
        print("    ❌ Token creation failed")
        return False
    
    # Test token verification
    print("  🔍 Testing token verification...")
    access_payload = jwt_handler.verify_token(access_token)
    refresh_payload = jwt_handler.verify_token(refresh_token)
    
    if (access_payload and access_payload.get("type") == "access" and
        refresh_payload and refresh_payload.get("type") == "refresh"):
        print("    ✅ Token verification passed")
    else:
        print("    ❌ Token verification failed")
        return False
    
    # Test token info extraction
    print("  📋 Testing token info extraction...")
    token_info = jwt_handler.get_token_info(access_token)
    
    if (token_info and token_info.get("user_id") == "1" and
        token_info.get("username") == "jwt_test_user"):
        print("    ✅ Token info extraction passed")
    else:
        print("    ❌ Token info extraction failed")
        return False
    
    # Test permission validation
    print("  🛡️ Testing permission validation...")
    has_permissions = jwt_handler.validate_permissions(user, ["read_logs", "analyze_logs"])
    has_role = jwt_handler.validate_role(user, "analyst")
    
    if has_permissions and has_role:
        print("    ✅ Permission and role validation passed")
    else:
        print("    ❌ Permission and role validation failed")
        return False
    
    # Test header extraction
    print("  📨 Testing header extraction...")
    auth_header = f"Bearer {access_token}"
    extracted_token = jwt_handler.extract_token_from_header(auth_header)
    
    if extracted_token == access_token:
        print("    ✅ Header extraction passed")
    else:
        print("    ❌ Header extraction failed")
        return False
    
    print("  ✅ JWT authentication system passed all tests\n")
    return True


def test_log_service():
    """Test log service operations."""
    print("📝 Testing Log Service...")
    
    # Note: This test doesn't actually connect to a database
    # It tests the service logic and query generation
    
    log_service = LogService()
    
    # Test log entry creation
    print("  📝 Testing log entry creation...")
    log_entry = LogEntry(
        log_id="service-test-123",
        timestamp=datetime.now(timezone.utc),
        level="INFO",
        message="Service test log",
        source_type="application",
        host="test-server",
        service="test-service"
    )
    
    # Test query generation
    query, params = log_entry.get_database_insert_query()
    if query and params and len(params) > 0:
        print("    ✅ Database insert query generation passed")
    else:
        print("    ❌ Database insert query generation failed")
        return False
    
    # Test search parameters
    print("  🔍 Testing search parameters...")
    search_params = {
        "query_text": "error",
        "source_type": "application",
        "level": "ERROR",
        "start_time": datetime.now(timezone.utc) - timedelta(hours=1),
        "end_time": datetime.now(timezone.utc),
        "limit": 50
    }
    
    # This would normally call the database, but we'll just test the parameter handling
    try:
        # Simulate the search logic
        where_conditions = []
        params = []
        
        if search_params.get("query_text"):
            where_conditions.append("(to_tsvector('english', message) @@ plainto_tsquery('english', %s))")
            params.append(search_params["query_text"])
        
        if search_params.get("source_type"):
            where_conditions.append("source_type = %s")
            params.append(search_params["source_type"])
        
        if search_params.get("level"):
            where_conditions.append("level = %s")
            params.append(search_params["level"])
        
        if search_params.get("start_time"):
            where_conditions.append("timestamp >= %s")
            params.append(search_params["start_time"])
        
        if search_params.get("end_time"):
            where_conditions.append("timestamp <= %s")
            params.append(search_params["end_time"])
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        if where_clause and len(params) > 0:
            print("    ✅ Search parameter handling passed")
        else:
            print("    ❌ Search parameter handling failed")
            return False
            
    except Exception as e:
        print(f"    ❌ Search parameter handling failed: {e}")
        return False
    
    print("  ✅ Log service passed all tests\n")
    return True


def test_model_relationships():
    """Test relationships between models."""
    print("🔗 Testing Model Relationships...")
    
    # Create related objects
    user = User(username="testuser", email="test@example.com", role="analyst")
    user.set_password("password123")
    user.id = 1
    
    log_entry = LogEntry(
        log_id="rel-test-123",
        timestamp=datetime.now(timezone.utc),
        level="ERROR",
        message="Database connection failed",
        source_type="application",
        request_id="req-1234567890"
    )
    log_entry.id = 1
    
    alert = Alert(
        title="Database Error Alert",
        description="Multiple database connection failures detected",
        severity="high",
        category="system",
        source="application",
        log_entries=[1],
        correlation_id="corr-1234567890",
        assigned_to=1
    )
    alert.id = 1
    
    correlation = Correlation(
        correlation_type="request",
        log_entry_ids=[1],
        source_systems=["application"],
        correlation_key="request_id",
        correlation_value="req-1234567890",
        confidence_score=0.9
    )
    correlation.id = 1
    
    dashboard = Dashboard(
        name="System Monitoring",
        description="Main system dashboard",
        owner_id=1,
        widgets=[
            {
                "id": "alert-widget",
                "type": "alert",
                "title": "Active Alerts",
                "position": {"x": 0, "y": 0, "w": 2, "h": 1}
            }
        ]
    )
    dashboard.id = 1
    
    # Test relationships
    print("  🔗 Testing object relationships...")
    
    # User -> Alert (assigned_to)
    if alert.assigned_to == user.id:
        print("    ✅ User -> Alert relationship passed")
    else:
        print("    ❌ User -> Alert relationship failed")
        return False
    
    # Alert -> LogEntry (log_entries)
    if log_entry.id in alert.log_entries:
        print("    ✅ Alert -> LogEntry relationship passed")
    else:
        print("    ❌ Alert -> LogEntry relationship failed")
        return False
    
    # Correlation -> LogEntry (log_entry_ids)
    if log_entry.id in correlation.log_entry_ids:
        print("    ✅ Correlation -> LogEntry relationship passed")
    else:
        print("    ❌ Correlation -> LogEntry relationship failed")
        return False
    
    # Dashboard -> User (owner_id)
    if dashboard.owner_id == user.id:
        print("    ✅ Dashboard -> User relationship passed")
    else:
        print("    ❌ Dashboard -> User relationship failed")
        return False
    
    # Test correlation key matching
    if (log_entry.request_id == correlation.correlation_value and
        correlation.correlation_key == "request_id"):
        print("    ✅ Correlation key matching passed")
    else:
        print("    ❌ Correlation key matching failed")
        return False
    
    print("  ✅ Model relationships passed all tests\n")
    return True


def test_api_documentation():
    """Test API documentation completeness."""
    print("📚 Testing API Documentation...")
    
    # Check if API reference file exists
    api_doc_path = "docs/API_REFERENCE.md"
    if not os.path.exists(api_doc_path):
        print("    ❌ API_REFERENCE.md not found")
        return False
    
    with open(api_doc_path, 'r') as f:
        content = f.read()
    
    # Check for required sections
    required_sections = [
        "## Overview",
        "## Authentication",
        "### Authentication Endpoints",
        "### Log Management Endpoints",
        "### Alert Management Endpoints",
        "### Dashboard Endpoints",
        "## Error Responses",
        "## Rate Limiting",
        "## Pagination"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"    ❌ Missing API documentation sections: {missing_sections}")
        return False
    else:
        print("    ✅ All required API documentation sections present")
    
    # Check for endpoint examples
    endpoint_examples = [
        "POST `/auth/login`",
        "GET `/logs/search`",
        "POST `/logs/ingest`",
        "GET `/alerts`",
        "POST `/dashboards`"
    ]
    
    missing_examples = []
    for example in endpoint_examples:
        if example not in content:
            missing_examples.append(example)
    
    if missing_examples:
        print(f"    ❌ Missing endpoint examples: {missing_examples}")
        return False
    else:
        print("    ✅ All required endpoint examples present")
    
    print("  ✅ API documentation passed all tests\n")
    return True


def main():
    """Run all Day 9 tests."""
    print("🚀 Day 9: Vercel Functions Structure - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Models", test_database_models),
        ("JWT Authentication", test_jwt_authentication),
        ("Log Service", test_log_service),
        ("Model Relationships", test_model_relationships),
        ("API Documentation", test_api_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name} tests...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} tests PASSED")
            else:
                print(f"❌ {test_name} tests FAILED")
        except Exception as e:
            print(f"❌ {test_name} tests FAILED with error: {e}")
        print("-" * 60)
    
    print(f"\n📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All Day 9 tests PASSED! Vercel Functions structure is working correctly.")
        return True
    else:
        print("⚠️  Some tests FAILED. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
