#!/usr/bin/env python3
"""
Test script for Vercel Functions API endpoints.
Tests the API functions without requiring Vercel to be running.
"""

import sys
import os
import json
import requests
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
        
        if result["statusCode"] == 200:
            body = json.loads(result["body"])
            print(f"✅ Health check passed: {body['status']}")
            return True
        else:
            print(f"❌ Health check failed: {result['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False

def test_log_ingestion():
    """Test the log ingestion endpoint."""
    print("Testing log ingestion endpoint...")
    try:
        from api.logs.ingest import handler
        
        class MockRequest:
            def get_json(self):
                return {
                    "source_id": "test-source-123",
                    "log_data": {
                        "level": "INFO",
                        "message": "Test log message",
                        "timestamp": datetime.utcnow().isoformat(),
                        "category": "test",
                        "tags": ["test", "api"],
                        "metadata": {"test": True}
                    }
                }
        
        mock_request = MockRequest()
        result = handler(mock_request)
        
        if result["statusCode"] == 200:
            body = json.loads(result["body"])
            print(f"✅ Log ingestion passed: {body['message']}")
            return True
        else:
            print(f"❌ Log ingestion failed: {result['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Log ingestion test failed: {e}")
        return False

def test_log_search():
    """Test the log search endpoint."""
    print("Testing log search endpoint...")
    try:
        from api.logs.search import handler
        
        class MockRequest:
            def __init__(self):
                self.args = {
                    'q': 'test',
                    'level': 'INFO',
                    'size': '5'
                }
        
        mock_request = MockRequest()
        result = handler(mock_request)
        
        if result["statusCode"] == 200:
            body = json.loads(result["body"])
            print(f"✅ Log search passed: {len(body['results'])} results")
            return True
        else:
            print(f"❌ Log search failed: {result['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Log search test failed: {e}")
        return False

def test_database_connection():
    """Test database connection utilities."""
    print("Testing database connection...")
    try:
        from api.utils.database import health_check
        
        result = health_check()
        if result["status"] == "healthy":
            print(f"✅ Database connection passed: {result['database']}")
            return True
        else:
            print(f"❌ Database connection failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_elasticsearch_connection():
    """Test Elasticsearch connection utilities."""
    print("Testing Elasticsearch connection...")
    try:
        from api.utils.elasticsearch import health_check
        
        result = health_check()
        if result["status"] == "healthy":
            print(f"✅ Elasticsearch connection passed: {result['cluster_status']}")
            return True
        else:
            print(f"❌ Elasticsearch connection failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Elasticsearch connection test failed: {e}")
        return False

def test_kafka_connection():
    """Test Kafka connection utilities."""
    print("Testing Kafka connection...")
    try:
        from api.utils.kafka import health_check
        
        result = health_check()
        if result["status"] == "healthy":
            print(f"✅ Kafka connection passed: {result['bootstrap_servers']}")
            return True
        else:
            print(f"❌ Kafka connection failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Kafka connection test failed: {e}")
        return False

def test_configuration():
    """Test configuration utilities."""
    print("Testing configuration...")
    try:
        from api.utils.config import validate_environment
        
        if validate_environment():
            print("✅ Configuration validation passed")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all API function tests."""
    print("=" * 60)
    print("API Functions Test - Engineering Log Intelligence System")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Elasticsearch Connection", test_elasticsearch_connection),
        ("Kafka Connection", test_kafka_connection),
        ("Health Check Function", test_health_check),
        ("Log Ingestion Function", test_log_ingestion),
        ("Log Search Function", test_log_search)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("API FUNCTIONS TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API functions are working correctly!")
        print("\n📋 Available endpoints:")
        print("   - Health Check: /api/health/check")
        print("   - Log Ingestion: /api/logs/ingest")
        print("   - Log Search: /api/logs/search")
        return True
    else:
        print("⚠️  Some API functions are not working. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
