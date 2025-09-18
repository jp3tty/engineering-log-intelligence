#!/usr/bin/env python3
"""
Test Vercel Functions via HTTP requests.
This simulates how the functions would be called in production.
"""

import requests
import json
import time
import subprocess
import signal
import os
import sys
from datetime import datetime

def start_vercel_dev():
    """Start Vercel dev server in background."""
    print("🚀 Starting Vercel dev server...")
    
    # Start Vercel dev server
    process = subprocess.Popen(
        ["vercel", "dev", "--port", "3001", "--yes"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence"
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(15)
    
    return process

def stop_vercel_dev(process):
    """Stop Vercel dev server."""
    print("🛑 Stopping Vercel dev server...")
    process.terminate()
    process.wait()

def test_health_endpoint():
    """Test health check endpoint via HTTP."""
    print("🏥 Testing Health Check Endpoint...")
    try:
        response = requests.get("http://localhost:3001/api/health/check", timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 503]:
            body = response.json()
            print(f"   Response: {json.dumps(body, indent=2)}")
            print("✅ Health check endpoint working")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_log_ingest_endpoint():
    """Test log ingestion endpoint via HTTP."""
    print("\n📝 Testing Log Ingestion Endpoint...")
    try:
        payload = {
            "source_id": "550e8400-e29b-41d4-a716-446655440000",
            "log_data": {
                "level": "INFO",
                "message": "Test log message via HTTP",
                "timestamp": datetime.utcnow().isoformat(),
                "category": "test"
            }
        }
        
        response = requests.post(
            "http://localhost:3001/api/logs/ingest",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            body = response.json()
            print(f"   Response: {json.dumps(body, indent=2)}")
            print("✅ Log ingestion endpoint working")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_log_search_endpoint():
    """Test log search endpoint via HTTP."""
    print("\n🔍 Testing Log Search Endpoint...")
    try:
        response = requests.get(
            "http://localhost:3001/api/logs/search?q=test&size=5",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            body = response.json()
            print(f"   Response: {json.dumps(body, indent=2)}")
            print("✅ Log search endpoint working")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Run all HTTP tests."""
    print("=" * 60)
    print("Vercel Functions HTTP Test - Engineering Log Intelligence")
    print("=" * 60)
    
    # Start Vercel dev server
    process = start_vercel_dev()
    
    try:
        tests = [
            test_health_endpoint,
            test_log_ingest_endpoint,
            test_log_search_endpoint
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 60)
        print("HTTP TEST RESULTS")
        print("=" * 60)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All HTTP endpoints are working correctly!")
            print("\n📋 Available endpoints:")
            print("   - Health Check: GET /api/health/check")
            print("   - Log Ingestion: POST /api/logs/ingest")
            print("   - Log Search: GET /api/logs/search")
            print("\n💡 Vercel Functions are ready for production!")
        else:
            print(f"⚠️  {total - passed} endpoint(s) need attention")
            return 1
            
    finally:
        # Stop Vercel dev server
        stop_vercel_dev(process)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
