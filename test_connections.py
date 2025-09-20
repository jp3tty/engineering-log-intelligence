#!/usr/bin/env python3
"""
Connection Test Script
Tests all production service connections
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
import requests
import json

def test_postgresql():
    """Test PostgreSQL connection"""
    print("🐘 Testing PostgreSQL...")
    
    try:
        # Get database URL from environment or use the one we know
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:YLACAwkFgEaAtTPjyFyvDsMGOjCOAsEu@maglev.proxy.rlwy.net:17716/railway')
        
        # Parse the URL
        parsed = urlparse(db_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        # Test connection
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        
        print(f"   ✅ PostgreSQL connected successfully!")
        print(f"   📊 Database version: {version[0]}")
        
        # Close connection
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ PostgreSQL connection failed: {e}")
        return False

def test_elasticsearch():
    """Test Elasticsearch connection"""
    print("🔍 Testing Elasticsearch...")
    
    try:
        # Get Elasticsearch URL from environment
        es_url = os.getenv('ELASTICSEARCH_URL')
        es_port = os.getenv('ELASTICSEARCH_PORT', '443')
        es_index = os.getenv('ELASTICSEARCH_INDEX', 'engineering_logs')
        
        if not es_url:
            print("   ⚠️  ELASTICSEARCH_URL not set - skipping test")
            return False
        
        # Construct full URL
        if not es_url.startswith('http'):
            es_url = f"https://{es_url}"
        
        # Test connection
        response = requests.get(f"{es_url}:{es_port}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Elasticsearch connected successfully!")
            print(f"   📊 Cluster name: {data.get('cluster_name', 'Unknown')}")
            print(f"   📊 Version: {data.get('version', {}).get('number', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Elasticsearch connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Elasticsearch connection failed: {e}")
        return False

def test_kafka():
    """Test Kafka connection"""
    print("📡 Testing Kafka...")
    
    try:
        # Get Kafka details from environment
        bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        api_key = os.getenv('KAFKA_API_KEY')
        api_secret = os.getenv('KAFKA_API_SECRET')
        
        if not bootstrap_servers or not api_key or not api_secret:
            print("   ⚠️  Kafka environment variables not set - skipping test")
            return False
        
        # For Confluent Cloud, we need to test the REST API
        # Extract cluster ID from bootstrap servers
        cluster_id = bootstrap_servers.split('.')[0].replace('pkc-', 'lkc-')
        
        # Test connection via REST API
        auth_url = f"https://api.confluent.cloud/v2/clusters/{cluster_id}"
        headers = {
            'Authorization': f'Basic {api_key}:{api_secret}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(auth_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Kafka connected successfully!")
            print(f"   📊 Cluster ID: {data.get('id', 'Unknown')}")
            print(f"   📊 Cluster name: {data.get('display_name', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Kafka connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Kafka connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Production Service Connection Test")
    print("====================================")
    print("")
    
    # Test results
    results = {
        'postgresql': test_postgresql(),
        'elasticsearch': test_elasticsearch(),
        'kafka': test_kafka()
    }
    
    print("")
    print("📊 Test Results Summary")
    print("=======================")
    
    for service, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {service.upper()}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    if all_passed:
        print("")
        print("🎉 All services connected successfully!")
        print("   Your production environment is ready!")
    else:
        print("")
        print("⚠️  Some services failed to connect.")
        print("   Check the error messages above and verify your configuration.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
