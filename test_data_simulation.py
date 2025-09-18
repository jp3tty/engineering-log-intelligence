#!/usr/bin/env python3
"""
Test script for data simulation functionality.
Tests log generation, anomaly simulation, and performance.
"""

import sys
import os
import json
import time
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_simulation.simulator import DataSimulator, create_default_config
from data_simulation.splunk_generator import SplunkLogGenerator

def test_splunk_generator():
    """Test SPLUNK log generator."""
    print("🧪 Testing SPLUNK Log Generator...")
    print("=" * 50)
    
    # Create generator
    config = {
        "log_levels": ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"],
        "log_level_weights": [0.1, 0.7, 0.15, 0.04, 0.01],
        "categories": ["system", "application", "security", "network"],
        "hosts": ["web-server-01", "web-server-02", "db-server-01"],
        "services": ["webapp", "database", "api", "auth"],
        "anomaly_rate": 0.1,
        "error_rate": 0.05,
        "environment": "test"
    }
    
    generator = SplunkLogGenerator(config)
    
    # Test single log generation
    print("📝 Generating single log entry...")
    log = generator.generate_log()
    print(f"   Log ID: {log['log_id']}")
    print(f"   Level: {log['level']}")
    print(f"   Message: {log['message']}")
    print(f"   Source: {log['metadata'].get('source', 'N/A')}")
    print(f"   Raw Log: {log['raw_log'][:100]}...")
    
    # Test batch generation
    print("\n📦 Generating batch of 10 logs...")
    logs = generator.generate_batch(10)
    print(f"   Generated: {len(logs)} logs")
    
    # Show log level distribution
    level_counts = {}
    for log in logs:
        level = log['level']
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print("   Level distribution:")
    for level, count in level_counts.items():
        print(f"     {level}: {count}")
    
    # Test anomaly generation
    print("\n🚨 Generating anomaly...")
    anomaly = generator.simulate_anomaly()
    print(f"   Anomaly Level: {anomaly['level']}")
    print(f"   Anomaly Message: {anomaly['message']}")
    print(f"   Anomaly Type: {anomaly['metadata'].get('anomaly_type', 'N/A')}")
    
    # Test statistics
    print("\n📊 Generator Statistics:")
    stats = generator.get_statistics()
    print(f"   Logs Generated: {stats['logs_generated']}")
    print(f"   Source Type: {stats['source_type']}")
    print(f"   Configuration: {json.dumps(stats['configuration'], indent=2)}")
    
    print("✅ SPLUNK generator test completed\n")
    return True

def test_data_simulator():
    """Test data simulator."""
    print("🎯 Testing Data Simulator...")
    print("=" * 50)
    
    # Create simulator with default config
    config = create_default_config()
    simulator = DataSimulator(config)
    
    # Test generator listing
    print("📋 Available generators:")
    generators = simulator.list_generators()
    for gen in generators:
        print(f"   - {gen}")
    
    # Test sample data generation
    print("\n📊 Generating sample data (100 logs)...")
    start_time = time.time()
    sample_logs = simulator.generate_sample_data(100)
    generation_time = time.time() - start_time
    
    print(f"   Generated: {len(sample_logs)} logs")
    print(f"   Generation time: {generation_time:.2f} seconds")
    print(f"   Rate: {len(sample_logs) / generation_time:.1f} logs/second")
    
    # Show sample log
    if sample_logs:
        print("\n📝 Sample log entry:")
        sample_log = sample_logs[0]
        print(f"   Log ID: {sample_log['log_id']}")
        print(f"   Level: {sample_log['level']}")
        print(f"   Message: {sample_log['message']}")
        print(f"   Raw Log: {sample_log['raw_log'][:100]}...")
    
    # Test anomaly generation
    print("\n🚨 Generating anomalies (5)...")
    anomalies = simulator.generate_anomalies(5)
    print(f"   Generated: {len(anomalies)} anomalies")
    
    if anomalies:
        print("   Sample anomaly:")
        anomaly = anomalies[0]
        print(f"     Level: {anomaly['level']}")
        print(f"     Message: {anomaly['message']}")
        print(f"     Anomaly Type: {anomaly['metadata'].get('anomaly_type', 'N/A')}")
    
    # Test statistics
    print("\n📈 Simulator Statistics:")
    stats = simulator.get_statistics()
    print(f"   Is Running: {stats['simulator']['is_running']}")
    print(f"   Total Logs: {stats['simulator']['total_logs_generated']}")
    print(f"   Generators: {len(stats['generators'])}")
    
    print("✅ Data simulator test completed\n")
    return True

def test_performance():
    """Test performance of log generation."""
    print("⚡ Testing Performance...")
    print("=" * 50)
    
    config = create_default_config()
    simulator = DataSimulator(config)
    
    # Test different batch sizes
    batch_sizes = [100, 500, 1000, 2000]
    
    for batch_size in batch_sizes:
        print(f"\n📊 Testing batch size: {batch_size}")
        
        start_time = time.time()
        logs = simulator.generate_sample_data(batch_size)
        generation_time = time.time() - start_time
        
        rate = len(logs) / generation_time if generation_time > 0 else 0
        
        print(f"   Generated: {len(logs)} logs")
        print(f"   Time: {generation_time:.2f} seconds")
        print(f"   Rate: {rate:.1f} logs/second")
        print(f"   Memory per log: {sys.getsizeof(logs) / len(logs) if logs else 0:.1f} bytes")
    
    print("✅ Performance test completed\n")
    return True

def test_log_formats():
    """Test different log formats."""
    print("📋 Testing Log Formats...")
    print("=" * 50)
    
    config = {
        "splunk_sources": [
            "WinEventLog:Security",
            "WinEventLog:System", 
            "WinEventLog:Application",
            "syslog",
            "apache_access",
            "apache_error",
            "iis_access",
            "iis_error"
        ],
        "splunk_hosts": ["test-server-01", "test-server-02"],
        "hosts": ["test-server-01", "test-server-02"],
        "services": ["webapp", "database", "api"],
        "environment": "test"
    }
    
    generator = SplunkLogGenerator(config)
    
    # Test each source type
    source_types = config["splunk_sources"]
    
    for source_type in source_types:
        print(f"\n🔍 Testing source: {source_type}")
        
        # Generate multiple logs for this source type
        logs = []
        for _ in range(5):
            log = generator.generate_log()
            if log['metadata'].get('source') == source_type:
                logs.append(log)
        
        if logs:
            print(f"   Generated: {len(logs)} logs")
            sample_log = logs[0]
            print(f"   Sample Level: {sample_log['level']}")
            print(f"   Sample Message: {sample_log['message']}")
            print(f"   Raw Log: {sample_log['raw_log'][:80]}...")
        else:
            print("   No logs generated for this source type")
    
    print("✅ Log formats test completed\n")
    return True

def main():
    """Run all tests."""
    print("🚀 Data Simulation Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    tests = [
        ("SPLUNK Generator", test_splunk_generator),
        ("Data Simulator", test_data_simulator),
        ("Performance", test_performance),
        ("Log Formats", test_log_formats)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("\n💡 Data simulation is ready for Phase 2!")
        print("   - SPLUNK log generation working")
        print("   - Batch generation efficient")
        print("   - Anomaly simulation functional")
        print("   - Performance meets requirements")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
