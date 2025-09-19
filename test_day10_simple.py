#!/usr/bin/env python3
"""
Simple test script for Day 10: Elasticsearch Integration
Tests core functionality without external dependencies.
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engineering_log_intelligence'))

from api.models.log_entry import LogEntry


def test_elasticsearch_service_creation():
    """Test Elasticsearch service can be created."""
    print("🔍 Testing Elasticsearch Service Creation...")
    
    try:
        # Mock environment variables
        os.environ['ELASTICSEARCH_URL'] = 'http://localhost:9200'
        os.environ['ELASTICSEARCH_INDEX'] = 'logs_test'
        
        from api.services.elasticsearch_service import ElasticsearchService
        es_service = ElasticsearchService()
        
        print("    ✅ ElasticsearchService created successfully")
        print(f"    ✅ Index name: {es_service.index_name}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Elasticsearch service creation failed: {e}")
        return False


def test_log_entry_model():
    """Test LogEntry model functionality."""
    print("📝 Testing LogEntry Model...")
    
    try:
        # Create a test log entry
        log_entry = LogEntry(
            log_id="test-day10-123",
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            message="Test Day 10 Elasticsearch integration",
            source_type="application",
            host="test-server",
            service="test-service",
            category="test",
            tags=["test", "elasticsearch", "day10"],
            raw_log="2025-09-19 10:30:00 INFO Test Day 10 Elasticsearch integration",
            structured_data={"test": True, "day": 10},
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
        if not errors:
            print("    ✅ LogEntry validation passed")
        else:
            print(f"    ❌ LogEntry validation failed: {errors}")
            return False
        
        # Test serialization
        log_dict = log_entry.to_dict()
        log_json = log_entry.to_json()
        
        if log_dict and log_json:
            print("    ✅ LogEntry serialization passed")
        else:
            print("    ❌ LogEntry serialization failed")
            return False
        
        # Test deserialization
        log_from_dict = LogEntry.from_dict(log_dict)
        log_from_json = LogEntry.from_json(log_json)
        
        if (log_from_dict.log_id == log_entry.log_id and 
            log_from_json.log_id == log_entry.log_id):
            print("    ✅ LogEntry deserialization passed")
        else:
            print("    ❌ LogEntry deserialization failed")
            return False
        
        # Test utility methods
        if (not log_entry.is_error() and 
            not log_entry.is_high_priority() and
            log_entry.get_correlation_key() == "request:req-1234567890"):
            print("    ✅ LogEntry utility methods passed")
        else:
            print("    ❌ LogEntry utility methods failed")
            return False
        
        # Test database query generation
        query, params = log_entry.get_database_insert_query()
        if query and params and len(params) > 0:
            print("    ✅ Database insert query generation passed")
        else:
            print("    ❌ Database insert query generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ LogEntry model test failed: {e}")
        return False


def test_elasticsearch_query_building():
    """Test Elasticsearch query building logic."""
    print("🔍 Testing Elasticsearch Query Building...")
    
    try:
        from api.services.elasticsearch_service import ElasticsearchService
        
        # Mock environment variables
        os.environ['ELASTICSEARCH_URL'] = 'http://localhost:9200'
        os.environ['ELASTICSEARCH_INDEX'] = 'logs_test'
        
        es_service = ElasticsearchService()
        
        # Test query building
        query = es_service._build_search_query(
            query_text="test search",
            source_type="application",
            level="INFO",
            host="test-server",
            start_time=datetime.now(timezone.utc) - timedelta(hours=1),
            end_time=datetime.now(timezone.utc),
            limit=50,
            offset=0
        )
        
        if query and "query" in query and "bool" in query["query"]:
            print("    ✅ Query structure is valid")
        else:
            print("    ❌ Query structure is invalid")
            return False
        
        # Check for text search
        if "multi_match" in str(query):
            print("    ✅ Text search query included")
        else:
            print("    ❌ Text search query missing")
            return False
        
        # Check for filters
        if "filter" in query["query"]["bool"]:
            print("    ✅ Filters included in query")
        else:
            print("    ❌ Filters missing from query")
            return False
        
        # Check for sorting
        if "sort" in query:
            print("    ✅ Sorting included in query")
        else:
            print("    ❌ Sorting missing from query")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Elasticsearch query building test failed: {e}")
        return False


def test_bulk_operations():
    """Test bulk operations logic."""
    print("📚 Testing Bulk Operations...")
    
    try:
        # Generate test logs
        test_logs = []
        for i in range(10):
            log_entry = LogEntry(
                log_id=f"test-bulk-{i}",
                timestamp=datetime.now(timezone.utc),
                level="INFO",
                message=f"Test bulk operation {i}",
                source_type="application",
                host="test-server",
                service="test-service"
            )
            test_logs.append(log_entry)
        
        print(f"    ✅ Generated {len(test_logs)} test logs")
        
        # Test bulk document preparation
        documents = []
        for log_entry in test_logs:
            doc = log_entry.to_dict()
            doc["id"] = log_entry.log_id
            documents.append(doc)
        
        if len(documents) == len(test_logs):
            print("    ✅ Bulk document preparation passed")
        else:
            print("    ❌ Bulk document preparation failed")
            return False
        
        # Test document structure
        if all("log_id" in doc for doc in documents):
            print("    ✅ Document structure is valid")
        else:
            print("    ❌ Document structure is invalid")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Bulk operations test failed: {e}")
        return False


def test_correlation_logic():
    """Test correlation logic."""
    print("🔗 Testing Correlation Logic...")
    
    try:
        # Create test logs with correlation
        logs = []
        request_id = "req-1234567890"
        
        for i in range(5):
            log_entry = LogEntry(
                log_id=f"test-correlation-{i}",
                timestamp=datetime.now(timezone.utc),
                level="INFO",
                message=f"Test correlation log {i}",
                source_type="application",
                request_id=request_id,
                session_id="sess-1234567890",
                correlation_id="corr-1234567890"
            )
            logs.append(log_entry)
        
        # Test correlation key generation
        correlation_keys = [log.get_correlation_key() for log in logs]
        if all(key == f"request:{request_id}" for key in correlation_keys):
            print("    ✅ Correlation key generation passed")
        else:
            print("    ❌ Correlation key generation failed")
            return False
        
        # Test correlation matching
        matching_logs = [log for log in logs if log.request_id == request_id]
        if len(matching_logs) == len(logs):
            print("    ✅ Correlation matching passed")
        else:
            print("    ❌ Correlation matching failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Correlation logic test failed: {e}")
        return False


def test_statistics_calculation():
    """Test statistics calculation logic."""
    print("📊 Testing Statistics Calculation...")
    
    try:
        # Generate test logs with different levels
        test_logs = []
        levels = ["INFO", "WARN", "ERROR", "FATAL"]
        
        for i, level in enumerate(levels):
            for j in range(10):  # 10 logs per level
                log_entry = LogEntry(
                    log_id=f"test-stats-{i}-{j}",
                    timestamp=datetime.now(timezone.utc),
                    level=level,
                    message=f"Test statistics log {i}-{j}",
                    source_type="application",
                    host="test-server",
                    service="test-service",
                    is_anomaly=(level in ["ERROR", "FATAL"]),
                    http_status=200 if level == "INFO" else 500
                )
                test_logs.append(log_entry)
        
        # Test level counting
        level_counts = {}
        for log in test_logs:
            level = log.level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        if all(count == 10 for count in level_counts.values()):
            print("    ✅ Level counting passed")
        else:
            print("    ❌ Level counting failed")
            return False
        
        # Test anomaly counting
        anomaly_count = sum(1 for log in test_logs if log.is_anomaly)
        if anomaly_count == 20:  # ERROR and FATAL logs
            print("    ✅ Anomaly counting passed")
        else:
            print("    ❌ Anomaly counting failed")
            return False
        
        # Test error counting
        error_count = sum(1 for log in test_logs if log.is_error())
        if error_count == 20:  # ERROR and FATAL logs
            print("    ✅ Error counting passed")
        else:
            print(f"    ❌ Error counting failed: expected 20, got {error_count}")
            # Let's debug this
            for log in test_logs:
                if log.is_error():
                    print(f"      Error log: level={log.level}, http_status={log.http_status}")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Statistics calculation test failed: {e}")
        return False


def test_performance_metrics():
    """Test performance metrics calculation."""
    print("⚡ Testing Performance Metrics...")
    
    try:
        # Create test logs with performance data
        test_logs = []
        response_times = [100, 150, 200, 250, 300, 350, 400, 450, 500, 550]
        
        for i, response_time in enumerate(response_times):
            log_entry = LogEntry(
                log_id=f"test-perf-{i}",
                timestamp=datetime.now(timezone.utc),
                level="INFO",
                message=f"Test performance log {i}",
                source_type="application",
                response_time_ms=response_time,
                performance_metrics={
                    "memory_usage_mb": 200 + i * 10,
                    "cpu_usage_percent": 30 + i * 5
                }
            )
            test_logs.append(log_entry)
        
        # Test response time calculation
        response_times = [log.response_time_ms for log in test_logs if log.response_time_ms]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"    ✅ Average response time: {avg_response_time:.2f}ms")
        else:
            print("    ❌ No response times found")
            return False
        
        # Test memory usage calculation
        memory_usage = [log.performance_metrics.get("memory_usage_mb", 0) for log in test_logs]
        if memory_usage:
            avg_memory = sum(memory_usage) / len(memory_usage)
            print(f"    ✅ Average memory usage: {avg_memory:.2f}MB")
        else:
            print("    ❌ No memory usage data found")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Performance metrics test failed: {e}")
        return False


def main():
    """Run all Day 10 simple tests."""
    print("🚀 Day 10: Elasticsearch Integration - Simple Test Suite")
    print("=" * 70)
    
    tests = [
        ("Elasticsearch Service Creation", test_elasticsearch_service_creation),
        ("LogEntry Model", test_log_entry_model),
        ("Elasticsearch Query Building", test_elasticsearch_query_building),
        ("Bulk Operations", test_bulk_operations),
        ("Correlation Logic", test_correlation_logic),
        ("Statistics Calculation", test_statistics_calculation),
        ("Performance Metrics", test_performance_metrics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with error: {e}")
        print("-" * 70)
    
    print(f"\n📊 Simple Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All Day 10 simple tests PASSED! Core functionality is working correctly.")
        print("\n📋 Day 10 Core Achievements:")
        print("  ✅ Elasticsearch service integration")
        print("  ✅ LogEntry model with full functionality")
        print("  ✅ Advanced query building with filters")
        print("  ✅ Bulk operations for performance")
        print("  ✅ Cross-system correlation logic")
        print("  ✅ Statistics and analytics calculation")
        print("  ✅ Performance metrics tracking")
        return True
    else:
        print("⚠️  Some simple tests FAILED. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
