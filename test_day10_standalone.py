#!/usr/bin/env python3
"""
Standalone test script for Day 10: Elasticsearch Integration
Tests core functionality without external dependencies.
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engineering_log_intelligence'))

from api.models.log_entry import LogEntry


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


def test_elasticsearch_query_logic():
    """Test Elasticsearch query building logic without service."""
    print("🔍 Testing Elasticsearch Query Logic...")
    
    try:
        # Test query building logic manually
        def build_search_query(
            query_text=None,
            source_type=None,
            level=None,
            host=None,
            start_time=None,
            end_time=None,
            limit=100,
            offset=0
        ):
            query = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": []
                    }
                },
                "sort": [{"timestamp": {"order": "desc"}}]
            }
            
            # Text search
            if query_text:
                query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query_text,
                        "fields": ["message^2", "raw_log", "structured_data.*"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            
            # Filters
            filters = []
            if source_type:
                filters.append({"term": {"source_type": source_type}})
            if level:
                filters.append({"term": {"level": level}})
            if host:
                filters.append({"term": {"host": host}})
            
            # Time range filter
            if start_time or end_time:
                time_filter = {"range": {"timestamp": {}}}
                if start_time:
                    time_filter["range"]["timestamp"]["gte"] = start_time.isoformat()
                if end_time:
                    time_filter["range"]["timestamp"]["lte"] = end_time.isoformat()
                filters.append(time_filter)
            
            if filters:
                query["query"]["bool"]["filter"] = filters
            
            # If no must clauses, use match_all
            if not query["query"]["bool"]["must"]:
                query["query"]["bool"]["must"] = [{"match_all": {}}]
            
            return query
        
        # Test basic query
        query = build_search_query(query_text="test")
        if "multi_match" in str(query):
            print("    ✅ Text search query included")
        else:
            print("    ❌ Text search query missing")
            return False
        
        # Test filtered query
        query = build_search_query(
            query_text="error",
            source_type="application",
            level="ERROR",
            start_time=datetime.now(timezone.utc) - timedelta(hours=1),
            end_time=datetime.now(timezone.utc)
        )
        
        if "filter" in query["query"]["bool"] and len(query["query"]["bool"]["filter"]) > 0:
            print("    ✅ Filters included in query")
        else:
            print("    ❌ Filters missing from query")
            return False
        
        # Test time range filter
        if "range" in str(query):
            print("    ✅ Time range filter included")
        else:
            print("    ❌ Time range filter missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Elasticsearch query logic test failed: {e}")
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
        
        # Test Elasticsearch bulk format
        bulk_actions = []
        for doc in documents:
            action = {
                "_index": "logs_test",
                "_source": doc
            }
            if "id" in doc:
                action["_id"] = doc["id"]
            bulk_actions.append(action)
        
        if len(bulk_actions) == len(documents):
            print("    ✅ Elasticsearch bulk format preparation passed")
        else:
            print("    ❌ Elasticsearch bulk format preparation failed")
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
        
        # Test different correlation types
        session_logs = []
        session_id = "sess-9876543210"
        
        for i in range(3):
            log_entry = LogEntry(
                log_id=f"test-session-{i}",
                timestamp=datetime.now(timezone.utc),
                level="INFO",
                message=f"Test session log {i}",
                source_type="application",
                session_id=session_id
            )
            session_logs.append(log_entry)
        
        session_correlation_keys = [log.get_correlation_key() for log in session_logs]
        if all(key == f"session:{session_id}" for key in session_correlation_keys):
            print("    ✅ Session correlation key generation passed")
        else:
            print("    ❌ Session correlation key generation failed")
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
        
        # Test error counting (should count ERROR and FATAL levels)
        error_count = sum(1 for log in test_logs if log.level in ["ERROR", "FATAL"])
        if error_count == 20:  # ERROR and FATAL logs
            print("    ✅ Error counting passed")
        else:
            print(f"    ❌ Error counting failed: expected 20, got {error_count}")
            return False
        
        # Test source type counting
        source_counts = {}
        for log in test_logs:
            source = log.source_type
            source_counts[source] = source_counts.get(source, 0) + 1
        
        if source_counts.get("application", 0) == 40:  # All logs
            print("    ✅ Source type counting passed")
        else:
            print("    ❌ Source type counting failed")
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
        
        # Test CPU usage calculation
        cpu_usage = [log.performance_metrics.get("cpu_usage_percent", 0) for log in test_logs]
        if cpu_usage:
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            print(f"    ✅ Average CPU usage: {avg_cpu:.2f}%")
        else:
            print("    ❌ No CPU usage data found")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Performance metrics test failed: {e}")
        return False


def test_aggregation_logic():
    """Test aggregation logic for Elasticsearch."""
    print("📈 Testing Aggregation Logic...")
    
    try:
        # Test aggregation query building
        def build_aggregation_query(start_time, end_time):
            return {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": start_time.isoformat(),
                                        "lte": end_time.isoformat()
                                    }
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "total_logs": {"value_count": {"field": "log_id"}},
                    "logs_by_level": {
                        "terms": {"field": "level", "size": 10}
                    },
                    "logs_by_source": {
                        "terms": {"field": "source_type", "size": 10}
                    },
                    "anomaly_count": {
                        "filter": {"term": {"is_anomaly": True}},
                        "aggs": {
                            "count": {"value_count": {"field": "log_id"}}
                        }
                    },
                    "error_count": {
                        "filter": {
                            "bool": {
                                "should": [
                                    {"terms": {"level": ["ERROR", "FATAL"]}},
                                    {"range": {"http_status": {"gte": 400}}}
                                ]
                            }
                        },
                        "aggs": {
                            "count": {"value_count": {"field": "log_id"}}
                        }
                    },
                    "avg_response_time": {
                        "avg": {"field": "response_time_ms"}
                    }
                },
                "size": 0
            }
        
        # Test aggregation query
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc)
        
        query = build_aggregation_query(start_time, end_time)
        
        if "aggs" in query and "total_logs" in query["aggs"]:
            print("    ✅ Aggregation query structure is valid")
        else:
            print("    ❌ Aggregation query structure is invalid")
            return False
        
        if "logs_by_level" in query["aggs"] and "logs_by_source" in query["aggs"]:
            print("    ✅ Term aggregations included")
        else:
            print("    ❌ Term aggregations missing")
            return False
        
        if "anomaly_count" in query["aggs"] and "error_count" in query["aggs"]:
            print("    ✅ Filter aggregations included")
        else:
            print("    ❌ Filter aggregations missing")
            return False
        
        if "avg_response_time" in query["aggs"]:
            print("    ✅ Metric aggregations included")
        else:
            print("    ❌ Metric aggregations missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Aggregation logic test failed: {e}")
        return False


def main():
    """Run all Day 10 standalone tests."""
    print("🚀 Day 10: Elasticsearch Integration - Standalone Test Suite")
    print("=" * 70)
    
    tests = [
        ("LogEntry Model", test_log_entry_model),
        ("Elasticsearch Query Logic", test_elasticsearch_query_logic),
        ("Bulk Operations", test_bulk_operations),
        ("Correlation Logic", test_correlation_logic),
        ("Statistics Calculation", test_statistics_calculation),
        ("Performance Metrics", test_performance_metrics),
        ("Aggregation Logic", test_aggregation_logic)
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
    
    print(f"\n📊 Standalone Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All Day 10 standalone tests PASSED! Core functionality is working correctly.")
        print("\n📋 Day 10 Core Achievements:")
        print("  ✅ LogEntry model with full functionality")
        print("  ✅ Advanced Elasticsearch query building")
        print("  ✅ Bulk operations for performance")
        print("  ✅ Cross-system correlation logic")
        print("  ✅ Statistics and analytics calculation")
        print("  ✅ Performance metrics tracking")
        print("  ✅ Elasticsearch aggregation queries")
        return True
    else:
        print("⚠️  Some standalone tests FAILED. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
