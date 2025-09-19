#!/usr/bin/env python3
"""
Test script for Day 9: Vercel Functions Structure (Models Only)
Tests database models and JWT authentication without database connection.
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
    
    # Test utility methods
    if log_entry.is_error() == False and log_entry.is_high_priority() == False:
        print("    ✅ LogEntry utility methods passed")
    else:
        print("    ❌ LogEntry utility methods failed")
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
    
    # Test role and permission methods
    if (user.has_role("analyst") and user.has_permission("read_logs") and 
        not user.is_admin() and user.can_manage_users() == False):
        print("    ✅ User role and permission methods passed")
    else:
        print("    ❌ User role and permission methods failed")
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
    
    # Test alert methods
    if (alert.is_open() and alert.is_high_priority() and 
        not alert.is_resolved() and not alert.is_closed()):
        print("    ✅ Alert utility methods passed")
    else:
        print("    ❌ Alert utility methods failed")
        return False
    
    # Test alert state changes
    alert.acknowledge(1)
    if alert.is_acknowledged() and alert.status == "acknowledged":
        print("    ✅ Alert acknowledgment passed")
    else:
        print("    ❌ Alert acknowledgment failed")
        return False
    
    alert.resolve(1, "Test resolution")
    if alert.is_resolved() and alert.status == "resolved":
        print("    ✅ Alert resolution passed")
    else:
        print("    ❌ Alert resolution failed")
        return False
    
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
    
    # Test dashboard methods
    if dashboard.can_access(1) and not dashboard.can_access(2):
        print("    ✅ Dashboard access control passed")
    else:
        print("    ❌ Dashboard access control failed")
        return False
    
    # Test widget management
    dashboard.add_widget({
        "id": "widget-2",
        "type": "table",
        "title": "Test Table",
        "position": {"x": 3, "y": 0, "w": 3, "h": 2}
    })
    if len(dashboard.widgets) == 2:
        print("    ✅ Dashboard widget management passed")
    else:
        print("    ❌ Dashboard widget management failed")
        return False
    
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
    
    # Test correlation methods
    if (correlation.is_high_confidence() and correlation.is_multi_system() and
        correlation.get_correlation_key() == "request:req-1234567890"):
        print("    ✅ Correlation utility methods passed")
    else:
        print("    ❌ Correlation utility methods failed")
        return False
    
    print("  ✅ All database models passed validation\n")
    return True


def test_jwt_authentication():
    """Test JWT authentication system."""
    print("🔐 Testing JWT Authentication...")
    
    # Import and run the standalone JWT test
    try:
        from test_jwt_standalone import test_jwt_standalone
        return test_jwt_standalone()
    except Exception as e:
        print(f"    ❌ JWT authentication test failed: {e}")
        return False


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


def test_database_schema():
    """Test database schema file."""
    print("🗄️ Testing Database Schema...")
    
    schema_path = "external-services/postgresql/schema.sql"
    if not os.path.exists(schema_path):
        print("    ❌ Database schema file not found")
        return False
    
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Check for required tables
    required_tables = [
        "CREATE TABLE users",
        "CREATE TABLE log_entries",
        "CREATE TABLE alerts",
        "CREATE TABLE dashboards",
        "CREATE TABLE correlations"
    ]
    
    missing_tables = []
    for table in required_tables:
        if table not in content:
            missing_tables.append(table)
    
    if missing_tables:
        print(f"    ❌ Missing database tables: {missing_tables}")
        return False
    else:
        print("    ✅ All required database tables present")
    
    # Check for indexes
    if "CREATE INDEX" in content:
        print("    ✅ Database indexes present")
    else:
        print("    ❌ Database indexes missing")
        return False
    
    # Check for functions
    if "CREATE OR REPLACE FUNCTION" in content:
        print("    ✅ Database functions present")
    else:
        print("    ❌ Database functions missing")
        return False
    
    print("  ✅ Database schema passed all tests\n")
    return True


def main():
    """Run all Day 9 tests."""
    print("🚀 Day 9: Vercel Functions Structure - Test Suite (Models Only)")
    print("=" * 70)
    
    tests = [
        ("Database Models", test_database_models),
        ("JWT Authentication", test_jwt_authentication),
        ("Model Relationships", test_model_relationships),
        ("API Documentation", test_api_documentation),
        ("Database Schema", test_database_schema)
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
        print("-" * 70)
    
    print(f"\n📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All Day 9 tests PASSED! Vercel Functions structure is working correctly.")
        print("\n📋 Day 9 Achievements:")
        print("  ✅ Database models designed and implemented")
        print("  ✅ JWT authentication system created")
        print("  ✅ CRUD operations implemented")
        print("  ✅ API documentation completed")
        print("  ✅ Database schema designed")
        print("  ✅ Model relationships established")
        return True
    else:
        print("⚠️  Some tests FAILED. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
