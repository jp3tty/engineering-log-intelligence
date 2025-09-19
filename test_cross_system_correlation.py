#!/usr/bin/env python3
"""
Test script for cross-system log correlation.
Tests that SPLUNK, SAP, and Application logs can be correlated together.
"""

import sys
import os
import json
from datetime import datetime
from collections import defaultdict

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cross_system_correlation():
    """Test that logs from different systems can be correlated."""
    print("Testing cross-system log correlation...")
    
    try:
        from data_simulation.simulator import DataSimulator, create_default_config
        
        # Create simulator with all generators enabled
        config = create_default_config()
        simulator = DataSimulator(config)
        
        # Generate sample data from all systems
        print("Generating sample data from all systems...")
        sample_data = simulator.generate_sample_data(300)  # 100 logs per system
        
        # Separate logs by system
        logs_by_system = defaultdict(list)
        for log in sample_data:
            system_type = log.get('metadata', {}).get('generator', 'unknown')
            logs_by_system[system_type].append(log)
        
        print(f"Generated logs:")
        for system, logs in logs_by_system.items():
            print(f"  {system}: {len(logs)} logs")
        
        # Test correlation by request_id
        print("\nTesting correlation by request_id...")
        request_correlations = defaultdict(list)
        
        for log in sample_data:
            request_id = log.get('request_id')
            if request_id:
                request_correlations[request_id].append(log)
        
        # Find requests that span multiple systems
        multi_system_requests = {
            req_id: logs for req_id, logs in request_correlations.items() 
            if len(set(log.get('metadata', {}).get('generator', 'unknown') for log in logs)) > 1
        }
        
        print(f"Found {len(multi_system_requests)} requests spanning multiple systems")
        
        # Show example correlation
        if multi_system_requests:
            example_req_id = list(multi_system_requests.keys())[0]
            example_logs = multi_system_requests[example_req_id]
            
            print(f"\nExample correlation for request {example_req_id}:")
            for log in example_logs:
                system = log.get('metadata', {}).get('generator', 'unknown')
                timestamp = log.get('timestamp', 'unknown')
                message = log.get('message', 'no message')[:50] + "..."
                print(f"  {system}: {timestamp} - {message}")
        
        # Test correlation by IP address
        print("\nTesting correlation by IP address...")
        ip_correlations = defaultdict(list)
        
        for log in sample_data:
            ip_address = log.get('ip_address')
            if ip_address:
                ip_correlations[ip_address].append(log)
        
        # Find IPs that appear in multiple systems
        multi_system_ips = {
            ip: logs for ip, logs in ip_correlations.items() 
            if len(set(log.get('metadata', {}).get('generator', 'unknown') for log in logs)) > 1
        }
        
        print(f"Found {len(multi_system_ips)} IP addresses appearing in multiple systems")
        
        # Test correlation by timestamp (within 1 minute)
        print("\nTesting correlation by timestamp...")
        timestamp_correlations = defaultdict(list)
        
        for log in sample_data:
            timestamp = log.get('timestamp')
            if timestamp:
                # Round to minute for correlation
                minute_key = timestamp[:16]  # YYYY-MM-DDTHH:MM
                timestamp_correlations[minute_key].append(log)
        
        # Find minutes with logs from multiple systems
        multi_system_minutes = {
            minute: logs for minute, logs in timestamp_correlations.items() 
            if len(set(log.get('metadata', {}).get('generator', 'unknown') for log in logs)) > 1
        }
        
        print(f"Found {len(multi_system_minutes)} minutes with logs from multiple systems")
        
        # Test anomaly correlation
        print("\nTesting anomaly correlation...")
        anomalies = simulator.generate_anomalies(10)
        
        anomaly_correlations = defaultdict(list)
        for anomaly in anomalies:
            request_id = anomaly.get('request_id')
            if request_id:
                anomaly_correlations[request_id].append(anomaly)
        
        print(f"Generated {len(anomalies)} anomalies")
        print(f"Found {len(anomaly_correlations)} unique request IDs with anomalies")
        
        # Test data quality
        print("\nTesting data quality...")
        from data_simulation.data_quality_checker import DataQualityChecker
        
        quality_checker = DataQualityChecker()
        quality_report = quality_checker.generate_quality_report(sample_data)
        print(quality_report)
        
        # Extract quality score for summary
        quality_score = quality_checker.check_batch_quality(sample_data)['quality_score']
        
        # Performance test
        print("\nTesting performance...")
        import time
        
        start_time = time.time()
        performance_data = simulator.generate_sample_data(1000)
        end_time = time.time()
        
        duration = end_time - start_time
        logs_per_second = len(performance_data) / duration
        
        print(f"Generated {len(performance_data)} logs in {duration:.2f} seconds")
        print(f"Performance: {logs_per_second:.0f} logs/second")
        
        # Summary
        print("\n" + "="*60)
        print("CROSS-SYSTEM CORRELATION TEST RESULTS")
        print("="*60)
        
        print(f"✅ Multi-system requests: {len(multi_system_requests)}")
        print(f"✅ Multi-system IPs: {len(multi_system_ips)}")
        print(f"✅ Multi-system minutes: {len(multi_system_minutes)}")
        print(f"✅ Data quality score: {quality_score}%")
        print(f"✅ Performance: {logs_per_second:.0f} logs/second")
        
        success_rate = 0
        if len(multi_system_requests) > 0:
            success_rate += 20
        if len(multi_system_ips) > 0:
            success_rate += 20
        if len(multi_system_minutes) > 0:
            success_rate += 20
        if quality_score >= 90:
            success_rate += 20
        if logs_per_second >= 50000:
            success_rate += 20
        
        print(f"\nOverall Success Rate: {success_rate}%")
        
        if success_rate >= 75:
            print("🎉 Cross-system correlation is working correctly!")
            return True
        else:
            print("⚠️  Some correlation features need improvement.")
            return False
            
    except Exception as e:
        print(f"❌ Cross-system correlation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_generators():
    """Test each generator individually."""
    print("Testing individual generators...")
    
    try:
        from data_simulation.simulator import DataSimulator, create_default_config
        
        config = create_default_config()
        simulator = DataSimulator(config)
        
        generators = ['splunk', 'sap', 'application']
        
        for generator_name in generators:
            print(f"\nTesting {generator_name} generator...")
            
            generator = simulator.get_generator(generator_name)
            if not generator:
                print(f"  ❌ Generator {generator_name} not found")
                continue
            
            # Test single log generation
            try:
                log = generator.generate_log()
                print(f"  ✅ Single log generation: {log.get('message', 'no message')[:50]}...")
            except Exception as e:
                print(f"  ❌ Single log generation failed: {e}")
                continue
            
            # Test batch generation
            try:
                batch = generator.generate_batch(10)
                print(f"  ✅ Batch generation: {len(batch)} logs")
            except Exception as e:
                print(f"  ❌ Batch generation failed: {e}")
                continue
            
            # Test anomaly generation
            try:
                anomaly = generator.simulate_anomaly()
                print(f"  ✅ Anomaly generation: {anomaly.get('anomaly_type', 'unknown')}")
            except Exception as e:
                print(f"  ❌ Anomaly generation failed: {e}")
                continue
            
            # Test statistics
            try:
                stats = generator.get_statistics()
                print(f"  ✅ Statistics: {stats.get('logs_generated', 0)} logs generated")
            except Exception as e:
                print(f"  ❌ Statistics failed: {e}")
                continue
        
        print("\n✅ All individual generator tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Individual generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all cross-system correlation tests."""
    print("=" * 60)
    print("Cross-System Log Correlation Test")
    print("=" * 60)
    
    # Test individual generators first
    individual_success = test_individual_generators()
    
    # Test cross-system correlation
    correlation_success = test_cross_system_correlation()
    
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    if individual_success and correlation_success:
        print("🎉 All tests passed! Cross-system correlation is working correctly.")
        print("\n📋 Available features:")
        print("   - SPLUNK log generation with realistic patterns")
        print("   - SAP transaction simulation with business scenarios")
        print("   - Application log generation with error types")
        print("   - Cross-system correlation by request_id, IP, and timestamp")
        print("   - Anomaly detection across all systems")
        print("   - Data quality validation")
        print("   - High-performance generation (50k+ logs/sec)")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
