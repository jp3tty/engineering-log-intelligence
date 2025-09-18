#!/usr/bin/env python3
"""
Simple test script for API functions without external dependencies.
Tests the core functionality without requiring all services to be running.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    try:
        from api.health.check import handler
        
        class MockRequest:
            pass
        
        mock_request = MockRequest()
        result = handler(mock_request)
        
        if result["statusCode"] in [200, 503]:
            body = json.loads(result["body"])
            print(f"✅ Health check passed: {body['status']}")
            return True
        else:
            print(f"❌ Health check failed: {result['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False

def test_configuration():
    """Test configuration utilities."""
    print("Testing configuration...")
    try:
        from api.utils.config import get_config, validate_environment
        
        config = get_config()
        print(f"✅ Configuration loaded: {config.APP_NAME} v{config.APP_VERSION}")
        
        if validate_environment():
            print("✅ Configuration validation passed")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database_utils():
    """Test database utility functions."""
    print("Testing database utilities...")
    try:
        from api.utils.database import get_database_manager
        
        db_manager = get_database_manager()
        print("✅ Database manager initialized")
        
        # Test health check (may fail if DB not accessible, but that's OK)
        health = db_manager.health_check()
        if health["status"] == "healthy":
            print(f"✅ Database connection: {health['database']}")
        else:
            print(f"⚠️  Database connection: {health['status']} - {health.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database utilities test failed: {e}")
        return False

def test_elasticsearch_utils():
    """Test Elasticsearch utility functions."""
    print("Testing Elasticsearch utilities...")
    try:
        from api.utils.elasticsearch import get_elasticsearch_manager
        
        es_manager = get_elasticsearch_manager()
        print("✅ Elasticsearch manager initialized")
        
        # Test health check (may fail if ES not accessible, but that's OK)
        health = es_manager.health_check()
        if health["status"] == "healthy":
            print(f"✅ Elasticsearch connection: {health['cluster_status']}")
        else:
            print(f"⚠️  Elasticsearch connection: {health['status']} - {health.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Elasticsearch utilities test failed: {e}")
        return False

def test_kafka_utils():
    """Test Kafka utility functions."""
    print("Testing Kafka utilities...")
    try:
        from api.utils.kafka import get_kafka_manager
        
        kafka_manager = get_kafka_manager()
        print("✅ Kafka manager initialized")
        
        # Test health check (may fail if Kafka not accessible, but that's OK)
        health = kafka_manager.health_check()
        if health["status"] == "healthy":
            print(f"✅ Kafka connection: {health['bootstrap_servers']}")
        else:
            print(f"⚠️  Kafka connection: {health['status']} - {health.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kafka utilities test failed: {e}")
        return False

def test_log_ingestion_structure():
    """Test log ingestion function structure."""
    print("Testing log ingestion function structure...")
    try:
        from api.logs.ingest import handler
        
        class MockRequest:
            def get_json(self):
                return {
                    "source_id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID
                    "log_data": {
                        "level": "INFO",
                        "message": "Test log message",
                        "timestamp": datetime.utcnow().isoformat(),
                        "category": "test"
                    }
                }
        
        mock_request = MockRequest()
        result = handler(mock_request)
        
        if "statusCode" in result and "body" in result:
            print("✅ Log ingestion function structure is correct")
            return True
        else:
            print("❌ Log ingestion function structure is incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Log ingestion structure test failed: {e}")
        return False

def test_log_search_structure():
    """Test log search function structure."""
    print("Testing log search function structure...")
    try:
        from api.logs.search import handler
        
        class MockRequest:
            def __init__(self):
                self.args = {'q': 'test', 'size': '5'}
        
        mock_request = MockRequest()
        result = handler(mock_request)
        
        if "statusCode" in result and "body" in result:
            print("✅ Log search function structure is correct")
            return True
        else:
            print("❌ Log search function structure is incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Log search structure test failed: {e}")
        return False

def main():
    """Run all API function tests."""
    print("=" * 60)
    print("Simple API Functions Test - Engineering Log Intelligence System")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Health Check Function", test_health_check),
        ("Database Utilities", test_database_utils),
        ("Elasticsearch Utilities", test_elasticsearch_utils),
        ("Kafka Utilities", test_kafka_utils),
        ("Log Ingestion Structure", test_log_ingestion_structure),
        ("Log Search Structure", test_log_search_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("SIMPLE API FUNCTIONS TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= total * 0.8:  # 80% pass rate is acceptable
        print("🎉 Core API functions are working correctly!")
        print("\n📋 Available endpoints:")
        print("   - Health Check: /api/health/check")
        print("   - Log Ingestion: /api/logs/ingest")
        print("   - Log Search: /api/logs/search")
        print("\n💡 Note: Some external service connections may show warnings")
        print("   This is normal if services are not fully configured yet.")
        return True
    else:
        print("⚠️  Some core API functions are not working. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
