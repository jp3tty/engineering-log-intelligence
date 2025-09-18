#!/usr/bin/env python3
"""
Test Vercel Functions locally without starting Vercel dev server.
This tests the function handlers directly.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_health_check():
    """Test health check function."""
    print("🏥 Testing Health Check Function...")
    try:
        from api.health.check import handler
        
        # Mock request object
        class MockRequest:
            def __init__(self):
                self.method = "GET"
                self.path = "/api/health/check"
                self.headers = {}
                self.args = {}
        
        request = MockRequest()
        result = handler(request)
        
        # Check response structure
        assert "statusCode" in result, "Missing statusCode in response"
        assert "body" in result, "Missing body in response"
        # Health check may return 503 if external services are unavailable
        assert result["statusCode"] in [200, 503], f"Expected 200 or 503, got {result['statusCode']}"
        
        # Parse response body
        body = json.loads(result["body"])
        assert "status" in body, "Missing status in response body"
        assert "service" in body, "Missing service in response body"
        
        print("✅ Health check function working correctly")
        print(f"   Response: {body}")
        return True
        
    except Exception as e:
        print(f"❌ Health check function failed: {e}")
        return False

def test_log_ingest():
    """Test log ingestion function."""
    print("\n📝 Testing Log Ingestion Function...")
    try:
        from api.logs.ingest import handler
        
        # Mock request object
        class MockRequest:
            def __init__(self):
                self.method = "POST"
                self.path = "/api/logs/ingest"
                self.headers = {"Content-Type": "application/json"}
                self.args = {}
            
            def get_json(self):
                return {
                    "source_id": "550e8400-e29b-41d4-a716-446655440000",
                    "log_data": {
                        "level": "INFO",
                        "message": "Test log message for Vercel function",
                        "timestamp": datetime.utcnow().isoformat(),
                        "category": "test"
                    }
                }
        
        request = MockRequest()
        result = handler(request)
        
        # Check response structure
        assert "statusCode" in result, "Missing statusCode in response"
        assert "body" in result, "Missing body in response"
        assert result["statusCode"] in [200, 201], f"Expected 200/201, got {result['statusCode']}"
        
        # Parse response body
        body = json.loads(result["body"])
        assert "message" in body, "Missing message in response body"
        
        print("✅ Log ingestion function working correctly")
        print(f"   Response: {body}")
        return True
        
    except Exception as e:
        print(f"❌ Log ingestion function failed: {e}")
        return False

def test_log_search():
    """Test log search function."""
    print("\n🔍 Testing Log Search Function...")
    try:
        from api.logs.search import handler
        
        # Mock request object
        class MockRequest:
            def __init__(self):
                self.method = "GET"
                self.path = "/api/logs/search"
                self.headers = {}
                self.args = {"query": "test", "limit": "10"}
        
        request = MockRequest()
        result = handler(request)
        
        # Check response structure
        assert "statusCode" in result, "Missing statusCode in response"
        assert "body" in result, "Missing body in response"
        assert result["statusCode"] == 200, f"Expected 200, got {result['statusCode']}"
        
        # Parse response body
        body = json.loads(result["body"])
        assert "results" in body, "Missing results in response body"
        assert "total" in body, "Missing total in response body"
        
        print("✅ Log search function working correctly")
        print(f"   Response: {body}")
        return True
        
    except Exception as e:
        print(f"❌ Log search function failed: {e}")
        return False

def main():
    """Run all Vercel function tests."""
    print("=" * 60)
    print("Vercel Functions Local Test - Engineering Log Intelligence")
    print("=" * 60)
    
    tests = [
        test_health_check,
        test_log_ingest,
        test_log_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print("VERCEL FUNCTIONS TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Vercel functions are working correctly!")
        print("\n📋 Available functions:")
        print("   - Health Check: /api/health/check")
        print("   - Log Ingestion: /api/logs/ingest")
        print("   - Log Search: /api/logs/search")
        print("\n💡 Functions are ready for Vercel deployment!")
    else:
        print(f"⚠️  {total - passed} function(s) need attention")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
