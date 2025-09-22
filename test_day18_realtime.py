"""
Day 18: Real-time Processing Test
================================

This script tests the real-time ML processing capabilities we built today.
It demonstrates how logs are processed in real-time and how alerts are generated.

For beginners: This script shows you how to test the real-time processing
system and see it in action.

Author: Engineering Log Intelligence Team
Date: September 22, 2025
"""

import json
import time
import requests
import asyncio
import logging
from datetime import datetime
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeTester:
    """
    Test class for real-time ML processing.
    
    This class helps us test the real-time processing system
    and verify that it's working correctly.
    """
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the tester.
        
        For beginners: This sets up the tester with the URL of our
        local development server.
        """
        self.base_url = base_url
        self.ml_analyze_url = f"{base_url}/api/ml/analyze"
        self.realtime_url = f"{base_url}/api/ml/real_time"
        
        logger.info(f"Real-time tester initialized with base URL: {base_url}")
    
    def test_ml_analysis(self):
        """
        Test the ML analysis endpoint.
        
        For beginners: This tests if our AI models can analyze logs correctly.
        """
        logger.info("Testing ML analysis endpoint...")
        
        # Test data - different types of logs
        test_logs = [
            {
                "log_id": "test_1",
                "message": "User authentication successful",
                "level": "INFO",
                "source_type": "application",
                "timestamp": datetime.now().isoformat()
            },
            {
                "log_id": "test_2", 
                "message": "Database connection timeout after 30 seconds",
                "level": "ERROR",
                "source_type": "application",
                "timestamp": datetime.now().isoformat()
            },
            {
                "log_id": "test_3",
                "message": "Unauthorized access attempt from IP 192.168.1.100",
                "level": "WARN",
                "source_type": "security",
                "timestamp": datetime.now().isoformat()
            },
            {
                "log_id": "test_4",
                "message": "High CPU usage detected: 95%",
                "level": "WARN",
                "source_type": "system",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        results = []
        
        for log_entry in test_logs:
            try:
                # Test single log analysis
                response = requests.post(
                    self.ml_analyze_url,
                    json={
                        "operation": "analyze",
                        "log_entry": log_entry
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results.append(result)
                    logger.info(f"✅ Analyzed log {log_entry['log_id']}: {result.get('analysis', {}).get('summary', {}).get('risk_level', 'unknown')}")
                else:
                    logger.error(f"❌ Failed to analyze log {log_entry['log_id']}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error analyzing log {log_entry['log_id']}: {str(e)}")
        
        return results
    
    def test_batch_analysis(self):
        """
        Test batch analysis of multiple logs.
        
        For beginners: This tests if our system can analyze multiple
        logs at once efficiently.
        """
        logger.info("Testing batch analysis...")
        
        # Generate test logs
        test_logs = []
        for i in range(10):
            test_logs.append({
                "log_id": f"batch_test_{i}",
                "message": f"Test log message {i}",
                "level": "INFO" if i % 2 == 0 else "WARN",
                "source_type": "application",
                "timestamp": datetime.now().isoformat()
            })
        
        try:
            response = requests.post(
                self.ml_analyze_url,
                json={
                    "operation": "batch_analyze",
                    "log_entries": test_logs
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Batch analysis completed: {len(result.get('analyses', []))} logs processed")
                return result
            else:
                logger.error(f"❌ Batch analysis failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error in batch analysis: {str(e)}")
            return None
    
    def test_realtime_status(self):
        """
        Test the real-time processing status endpoint.
        
        For beginners: This checks if our real-time processing system
        is working and what its current status is.
        """
        logger.info("Testing real-time status...")
        
        try:
            # Test GET request for status
            response = requests.get(self.realtime_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Real-time status retrieved successfully")
                logger.info(f"   Status: {result.get('stats', {}).get('is_running', 'unknown')}")
                logger.info(f"   Logs processed: {result.get('stats', {}).get('logs_processed', 0)}")
                return result
            else:
                logger.error(f"❌ Failed to get real-time status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting real-time status: {str(e)}")
            return None
    
    def test_realtime_control(self):
        """
        Test starting and stopping real-time processing.
        
        For beginners: This tests if we can start and stop the
        real-time processing system.
        """
        logger.info("Testing real-time control...")
        
        try:
            # Test starting processing
            start_response = requests.post(
                self.realtime_url,
                json={
                    "operation": "start",
                    "topics": ["logs", "security", "performance"]
                },
                timeout=10
            )
            
            if start_response.status_code == 200:
                logger.info("✅ Real-time processing started successfully")
            else:
                logger.error(f"❌ Failed to start processing: {start_response.status_code}")
                return False
            
            # Wait a bit
            time.sleep(2)
            
            # Test getting status
            status_response = requests.post(
                self.realtime_url,
                json={"operation": "status"},
                timeout=10
            )
            
            if status_response.status_code == 200:
                status = status_response.json()
                logger.info(f"✅ Status retrieved: {status.get('stats', {}).get('is_running', 'unknown')}")
            else:
                logger.error(f"❌ Failed to get status: {status_response.status_code}")
            
            # Test stopping processing
            stop_response = requests.post(
                self.realtime_url,
                json={"operation": "stop"},
                timeout=10
            )
            
            if stop_response.status_code == 200:
                logger.info("✅ Real-time processing stopped successfully")
                return True
            else:
                logger.error(f"❌ Failed to stop processing: {stop_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in real-time control: {str(e)}")
            return False
    
    def test_performance(self):
        """
        Test the performance of the ML analysis system.
        
        For beginners: This tests how fast our system can process logs
        and identifies any performance issues.
        """
        logger.info("Testing performance...")
        
        # Generate test logs
        test_logs = []
        for i in range(50):
            test_logs.append({
                "log_id": f"perf_test_{i}",
                "message": f"Performance test log {i}",
                "level": "INFO",
                "source_type": "application",
                "timestamp": datetime.now().isoformat()
            })
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.ml_analyze_url,
                json={
                    "operation": "batch_analyze",
                    "log_entries": test_logs
                },
                timeout=60
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                logs_processed = len(result.get('analyses', []))
                logs_per_second = logs_processed / processing_time
                
                logger.info(f"✅ Performance test completed:")
                logger.info(f"   Logs processed: {logs_processed}")
                logger.info(f"   Processing time: {processing_time:.2f} seconds")
                logger.info(f"   Logs per second: {logs_per_second:.2f}")
                
                return {
                    'logs_processed': logs_processed,
                    'processing_time': processing_time,
                    'logs_per_second': logs_per_second
                }
            else:
                logger.error(f"❌ Performance test failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error in performance test: {str(e)}")
            return None
    
    def run_all_tests(self):
        """
        Run all tests for the real-time processing system.
        
        For beginners: This runs all the tests we've created to make sure
        everything is working correctly.
        """
        logger.info("🚀 Starting Day 18 Real-time Processing Tests")
        logger.info("=" * 50)
        
        test_results = {}
        
        # Test 1: ML Analysis
        logger.info("\n📊 Test 1: ML Analysis")
        test_results['ml_analysis'] = self.test_ml_analysis()
        
        # Test 2: Batch Analysis
        logger.info("\n📊 Test 2: Batch Analysis")
        test_results['batch_analysis'] = self.test_batch_analysis()
        
        # Test 3: Real-time Status
        logger.info("\n📊 Test 3: Real-time Status")
        test_results['realtime_status'] = self.test_realtime_status()
        
        # Test 4: Real-time Control
        logger.info("\n📊 Test 4: Real-time Control")
        test_results['realtime_control'] = self.test_realtime_control()
        
        # Test 5: Performance
        logger.info("\n📊 Test 5: Performance")
        test_results['performance'] = self.test_performance()
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📋 Test Summary")
        logger.info("=" * 50)
        
        passed_tests = 0
        total_tests = 5
        
        if test_results['ml_analysis']:
            logger.info("✅ ML Analysis: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ ML Analysis: FAILED")
        
        if test_results['batch_analysis']:
            logger.info("✅ Batch Analysis: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Batch Analysis: FAILED")
        
        if test_results['realtime_status']:
            logger.info("✅ Real-time Status: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Real-time Status: FAILED")
        
        if test_results['realtime_control']:
            logger.info("✅ Real-time Control: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Real-time Control: FAILED")
        
        if test_results['performance']:
            logger.info("✅ Performance: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Performance: FAILED")
        
        logger.info(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! Real-time processing is working correctly.")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Check the logs above for details.")
        
        return test_results

def main():
    """
    Main function to run the real-time processing tests.
    
    For beginners: This is the main function that runs when you execute
    this script. It sets up the tester and runs all the tests.
    """
    print("🎯 Day 18: Real-time Processing Test")
    print("=" * 50)
    print("This script tests the real-time ML processing capabilities.")
    print("Make sure your Vercel development server is running!")
    print("Run: vercel dev")
    print("=" * 50)
    
    # Create tester instance
    tester = RealTimeTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    print("\n🏁 Testing completed!")
    print("Check the logs above for detailed results.")

if __name__ == "__main__":
    main()
