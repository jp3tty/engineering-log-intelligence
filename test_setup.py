#!/usr/bin/env python3
"""
Test script to verify the Engineering Log Intelligence System setup.
This script tests the basic functionality without requiring Vercel to be running.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    return True

def test_health_function():
    """Test the health check function."""
    print("\nTesting health check function...")
    
    try:
        # Import the health check function
        from api.health.check import handler
        
        # Create a mock request object
        class MockRequest:
            pass
        
        mock_request = MockRequest()
        
        # Call the handler
        result = handler(mock_request)
        
        # Check the result structure
        if isinstance(result, dict) and "statusCode" in result:
            print("✅ Health check function structure is correct")
            
            # Parse the body to check content
            body = json.loads(result["body"])
            if "status" in body and "timestamp" in body:
                print("✅ Health check response contains expected fields")
                print(f"   Status: {body['status']}")
                print(f"   Service: {body['service']}")
                print(f"   Version: {body['version']}")
                return True
            else:
                print("❌ Health check response missing expected fields")
                return False
        else:
            print("❌ Health check function returned unexpected structure")
            return False
            
    except Exception as e:
        print(f"❌ Health check function test failed: {e}")
        return False

def test_project_structure():
    """Test that the project structure is correct."""
    print("\nTesting project structure...")
    
    required_dirs = [
        "api",
        "api/auth",
        "api/logs", 
        "api/ml",
        "api/dashboard",
        "api/health",
        "frontend",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/views",
        "frontend/src/services",
        "frontend/src/utils",
        "external-services",
        "docs",
        "tests"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            all_exist = False
    
    return all_exist

def test_config_files():
    """Test that configuration files exist."""
    print("\nTesting configuration files...")
    
    required_files = [
        "requirements.txt",
        "vercel.json",
        ".gitignore",
        ".vercelignore",
        "README.md",
        "env.example"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("=" * 60)
    print("Engineering Log Intelligence System - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Configuration Files", test_config_files),
        ("Health Check Function", test_health_function)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
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
        print("🎉 All tests passed! Day 1 setup is complete.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
