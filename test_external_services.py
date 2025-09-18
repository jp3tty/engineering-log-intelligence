#!/usr/bin/env python3
"""
Test script to verify external services are running correctly.
This script tests the external services without requiring Vercel.
"""

import sys
import os
import json
import requests
import psycopg2
from datetime import datetime

def test_postgresql():
    """Test PostgreSQL connection."""
    print("Testing PostgreSQL connection...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="log_intelligence_dev",
            user="dev_user",
            password="dev_password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL connected: {version[:50]}...")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_elasticsearch():
    """Test Elasticsearch connection."""
    print("Testing Elasticsearch connection...")
    try:
        response = requests.get("http://localhost:9200/_cluster/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Elasticsearch connected: {health['status']} cluster")
            return True
        else:
            print(f"❌ Elasticsearch health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Elasticsearch connection failed: {e}")
        return False

def test_kafka():
    """Test Kafka connection."""
    print("Testing Kafka connection...")
    try:
        # Test Kafka by checking if the port is open and accessible
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 9092))
        sock.close()
        
        if result == 0:
            print("✅ Kafka port is accessible")
            return True
        else:
            print(f"❌ Kafka port connection failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        return False

def test_redis():
    """Test Redis connection."""
    print("Testing Redis connection...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connected successfully")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def main():
    """Run all external service tests."""
    print("=" * 60)
    print("External Services Test - Engineering Log Intelligence System")
    print("=" * 60)
    
    tests = [
        ("PostgreSQL", test_postgresql),
        ("Elasticsearch", test_elasticsearch),
        ("Kafka", test_kafka),
        ("Redis", test_redis)
    ]
    
    results = []
    for service_name, test_func in tests:
        print(f"\n{'='*20} {service_name} {'='*20}")
        result = test_func()
        results.append((service_name, result))
    
    print("\n" + "=" * 60)
    print("EXTERNAL SERVICES TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for service_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{service_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} services working")
    
    if passed == total:
        print("🎉 All external services are running correctly!")
        print("\n📋 You can now:")
        print("   - Connect to PostgreSQL: localhost:5432")
        print("   - Access Elasticsearch: http://localhost:9200")
        print("   - Use Kafka: localhost:9092")
        print("   - Use Redis: localhost:6379")
        return True
    else:
        print("⚠️  Some services are not running. Please check Docker containers:")
        print("   docker-compose -f docker-compose.dev.yml ps")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
