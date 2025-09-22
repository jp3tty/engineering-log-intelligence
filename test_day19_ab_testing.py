"""
Day 19: A/B Testing Framework Test
=================================

This script tests the A/B testing framework we built today.
It demonstrates how to create, manage, and monitor A/B tests for ML models.

For beginners: This script shows you how to test the A/B testing system
and see how it compares different AI models.

Author: Engineering Log Intelligence Team
Date: September 23, 2025
"""

import json
import time
import requests
import logging
from datetime import datetime
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ABTestingTester:
    """
    Test class for A/B testing framework.
    
    This class helps us test the A/B testing system
    and verify that it's working correctly.
    """
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the tester.
        
        For beginners: This sets up the tester with the URL of our
        local development server.
        """
        self.base_url = base_url
        self.ab_testing_url = f"{base_url}/api/ml/ab_testing"
        
        logger.info(f"A/B Testing tester initialized with base URL: {base_url}")
    
    def test_create_ab_test(self):
        """
        Test creating an A/B test.
        
        For beginners: This tests if we can create a new A/B test
        to compare different AI models.
        """
        logger.info("Testing A/B test creation...")
        
        test_data = {
            "operation": "create_test",
            "test_id": "test_log_classification",
            "name": "Log Classification Model Comparison",
            "description": "Compare different models for log classification accuracy"
        }
        
        try:
            response = requests.post(
                self.ab_testing_url,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ A/B test created successfully: {result.get('test_id')}")
                return True
            else:
                logger.error(f"❌ Failed to create A/B test: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating A/B test: {str(e)}")
            return False
    
    def test_add_variants(self):
        """
        Test adding variants to an A/B test.
        
        For beginners: This tests if we can add different AI models
        to our A/B test for comparison.
        """
        logger.info("Testing variant addition...")
        
        # Add first variant
        variant1_data = {
            "operation": "add_variant",
            "test_id": "test_log_classification",
            "variant": {
                "name": "Model A - Rule-based",
                "model_path": "models/rule_based_classifier.pkl",
                "traffic_percentage": 50.0
            }
        }
        
        try:
            response = requests.post(
                self.ab_testing_url,
                json=variant1_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Variant 1 added successfully")
            else:
                logger.error(f"❌ Failed to add variant 1: {response.status_code}")
                return False
            
            # Add second variant
            variant2_data = {
                "operation": "add_variant",
                "test_id": "test_log_classification",
                "variant": {
                    "name": "Model B - ML-based",
                    "model_path": "models/ml_classifier.pkl",
                    "traffic_percentage": 50.0
                }
            }
            
            response = requests.post(
                self.ab_testing_url,
                json=variant2_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Variant 2 added successfully")
                return True
            else:
                logger.error(f"❌ Failed to add variant 2: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding variants: {str(e)}")
            return False
    
    def test_start_ab_test(self):
        """
        Test starting an A/B test.
        
        For beginners: This tests if we can start the A/B test
        so it begins comparing the models.
        """
        logger.info("Testing A/B test start...")
        
        start_data = {
            "operation": "start_test",
            "test_id": "test_log_classification"
        }
        
        try:
            response = requests.post(
                self.ab_testing_url,
                json=start_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ A/B test started successfully: {result.get('test_id')}")
                return True
            else:
                logger.error(f"❌ Failed to start A/B test: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting A/B test: {str(e)}")
            return False
    
    def test_ab_prediction(self):
        """
        Test making predictions with A/B testing.
        
        For beginners: This tests if the A/B test can analyze logs
        using the different models and route traffic correctly.
        """
        logger.info("Testing A/B prediction...")
        
        # Test logs for prediction
        test_logs = [
            {
                "log_id": "ab_test_1",
                "message": "User authentication successful",
                "level": "INFO",
                "source_type": "application",
                "timestamp": datetime.now().isoformat()
            },
            {
                "log_id": "ab_test_2",
                "message": "Database connection timeout after 30 seconds",
                "level": "ERROR",
                "source_type": "application",
                "timestamp": datetime.now().isoformat()
            },
            {
                "log_id": "ab_test_3",
                "message": "Unauthorized access attempt from IP 192.168.1.100",
                "level": "WARN",
                "source_type": "security",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        results = []
        
        for i, log_entry in enumerate(test_logs, 1):
            try:
                prediction_data = {
                    "operation": "predict",
                    "log_entry": log_entry
                }
                
                response = requests.post(
                    self.ab_testing_url,
                    json=prediction_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get('prediction', {})
                    
                    logger.info(f"✅ Prediction {i} completed:")
                    logger.info(f"   Log: {log_entry['message'][:50]}...")
                    logger.info(f"   Variant: {prediction.get('variant_name', 'unknown')}")
                    logger.info(f"   Category: {prediction.get('category', 'unknown')}")
                    logger.info(f"   Confidence: {prediction.get('confidence', 0)}")
                    
                    results.append(prediction)
                else:
                    logger.error(f"❌ Failed to make prediction {i}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error making prediction {i}: {str(e)}")
        
        return len(results) > 0
    
    def test_get_test_status(self):
        """
        Test getting A/B test status.
        
        For beginners: This tests if we can check the status
        and results of our A/B test.
        """
        logger.info("Testing A/B test status...")
        
        try:
            # Get all tests
            response = requests.get(self.ab_testing_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ A/B test status retrieved successfully")
                logger.info(f"   Total tests: {result.get('total_tests', 0)}")
                logger.info(f"   Active tests: {result.get('active_count', 0)}")
                
                # Get specific test results
                specific_response = requests.get(
                    f"{self.ab_testing_url}?test_id=test_log_classification",
                    timeout=10
                )
                
                if specific_response.status_code == 200:
                    test_result = specific_response.json()
                    test_data = test_result.get('test', {})
                    logger.info(f"   Test status: {test_data.get('status', 'unknown')}")
                    logger.info(f"   Test duration: {test_data.get('duration_hours', 0):.2f} hours")
                    logger.info(f"   Total predictions: {test_data.get('total_predictions', 0)}")
                    
                    variants = test_data.get('variants', [])
                    for variant in variants:
                        logger.info(f"   Variant {variant.get('name', 'unknown')}: "
                                  f"Accuracy {variant.get('accuracy', 0):.3f}, "
                                  f"Predictions {variant.get('total_predictions', 0)}")
                
                return True
            else:
                logger.error(f"❌ Failed to get A/B test status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error getting A/B test status: {str(e)}")
            return False
    
    def test_stop_ab_test(self):
        """
        Test stopping an A/B test.
        
        For beginners: This tests if we can stop the A/B test
        and see which model won.
        """
        logger.info("Testing A/B test stop...")
        
        stop_data = {
            "operation": "stop_test",
            "test_id": "test_log_classification"
        }
        
        try:
            response = requests.post(
                self.ab_testing_url,
                json=stop_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                test_results = result.get('results', {})
                
                logger.info("✅ A/B test stopped successfully")
                logger.info(f"   Winner: {test_results.get('winner', 'unknown')}")
                logger.info(f"   Statistical significance: {test_results.get('statistical_significance', False)}")
                logger.info(f"   P-value: {test_results.get('p_value', 0)}")
                
                return True
            else:
                logger.error(f"❌ Failed to stop A/B test: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error stopping A/B test: {str(e)}")
            return False
    
    def test_performance_comparison(self):
        """
        Test performance comparison between variants.
        
        For beginners: This tests how well the A/B testing system
        compares the performance of different models.
        """
        logger.info("Testing performance comparison...")
        
        # Create a new test for performance comparison
        perf_test_data = {
            "operation": "create_test",
            "test_id": "test_performance_comparison",
            "name": "Performance Comparison Test",
            "description": "Compare response times and accuracy of different models"
        }
        
        try:
            # Create test
            response = requests.post(
                self.ab_testing_url,
                json=perf_test_data,
                timeout=10
            )
            
            if response.status_code != 201:
                logger.error(f"❌ Failed to create performance test: {response.status_code}")
                return False
            
            # Add variants with different performance characteristics
            variants = [
                {
                    "name": "Fast Model",
                    "model_path": "models/fast_model.pkl",
                    "traffic_percentage": 50.0
                },
                {
                    "name": "Accurate Model",
                    "model_path": "models/accurate_model.pkl",
                    "traffic_percentage": 50.0
                }
            ]
            
            for variant in variants:
                variant_data = {
                    "operation": "add_variant",
                    "test_id": "test_performance_comparison",
                    "variant": variant
                }
                
                response = requests.post(
                    self.ab_testing_url,
                    json=variant_data,
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Failed to add variant {variant['name']}")
                    return False
            
            # Start test
            start_data = {
                "operation": "start_test",
                "test_id": "test_performance_comparison"
            }
            
            response = requests.post(
                self.ab_testing_url,
                json=start_data,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to start performance test")
                return False
            
            # Make multiple predictions to generate performance data
            logger.info("   Making predictions to generate performance data...")
            for i in range(20):
                log_entry = {
                    "log_id": f"perf_test_{i}",
                    "message": f"Performance test log {i}",
                    "level": "INFO",
                    "source_type": "application",
                    "timestamp": datetime.now().isoformat()
                }
                
                prediction_data = {
                    "operation": "predict",
                    "log_entry": log_entry
                }
                
                requests.post(
                    self.ab_testing_url,
                    json=prediction_data,
                    timeout=5
                )
                
                time.sleep(0.1)  # Small delay between predictions
            
            # Stop test and get results
            stop_data = {
                "operation": "stop_test",
                "test_id": "test_performance_comparison"
            }
            
            response = requests.post(
                self.ab_testing_url,
                json=stop_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                test_results = result.get('results', {})
                
                logger.info("✅ Performance comparison completed")
                logger.info(f"   Winner: {test_results.get('winner', 'unknown')}")
                
                variants = test_results.get('variants', [])
                for variant in variants:
                    logger.info(f"   {variant.get('name', 'unknown')}: "
                              f"Accuracy {variant.get('accuracy', 0):.3f}, "
                              f"Avg Response Time {variant.get('average_response_time', 0):.3f}s")
                
                return True
            else:
                logger.error(f"❌ Failed to stop performance test")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in performance comparison: {str(e)}")
            return False
    
    def run_all_tests(self):
        """
        Run all A/B testing tests.
        
        For beginners: This runs all the tests we've created to make sure
        the A/B testing system is working correctly.
        """
        logger.info("🚀 Starting Day 19 A/B Testing Tests")
        logger.info("=" * 50)
        
        test_results = {}
        
        # Test 1: Create A/B Test
        logger.info("\n📊 Test 1: Create A/B Test")
        test_results['create_test'] = self.test_create_ab_test()
        
        # Test 2: Add Variants
        logger.info("\n📊 Test 2: Add Variants")
        test_results['add_variants'] = self.test_add_variants()
        
        # Test 3: Start A/B Test
        logger.info("\n📊 Test 3: Start A/B Test")
        test_results['start_test'] = self.test_start_ab_test()
        
        # Test 4: A/B Prediction
        logger.info("\n📊 Test 4: A/B Prediction")
        test_results['ab_prediction'] = self.test_ab_prediction()
        
        # Test 5: Get Test Status
        logger.info("\n📊 Test 5: Get Test Status")
        test_results['get_status'] = self.test_get_test_status()
        
        # Test 6: Stop A/B Test
        logger.info("\n📊 Test 6: Stop A/B Test")
        test_results['stop_test'] = self.test_stop_ab_test()
        
        # Test 7: Performance Comparison
        logger.info("\n📊 Test 7: Performance Comparison")
        test_results['performance_comparison'] = self.test_performance_comparison()
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📋 Test Summary")
        logger.info("=" * 50)
        
        passed_tests = 0
        total_tests = 7
        
        if test_results['create_test']:
            logger.info("✅ Create A/B Test: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Create A/B Test: FAILED")
        
        if test_results['add_variants']:
            logger.info("✅ Add Variants: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Add Variants: FAILED")
        
        if test_results['start_test']:
            logger.info("✅ Start A/B Test: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Start A/B Test: FAILED")
        
        if test_results['ab_prediction']:
            logger.info("✅ A/B Prediction: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ A/B Prediction: FAILED")
        
        if test_results['get_status']:
            logger.info("✅ Get Test Status: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Get Test Status: FAILED")
        
        if test_results['stop_test']:
            logger.info("✅ Stop A/B Test: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Stop A/B Test: FAILED")
        
        if test_results['performance_comparison']:
            logger.info("✅ Performance Comparison: PASSED")
            passed_tests += 1
        else:
            logger.info("❌ Performance Comparison: FAILED")
        
        logger.info(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! A/B testing framework is working correctly.")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Check the logs above for details.")
        
        return test_results

def main():
    """
    Main function to run the A/B testing tests.
    
    For beginners: This is the main function that runs when you execute
    this script. It sets up the tester and runs all the tests.
    """
    print("🎯 Day 19: A/B Testing Framework Test")
    print("=" * 50)
    print("This script tests the A/B testing framework for ML models.")
    print("Make sure your Vercel development server is running!")
    print("Run: vercel dev")
    print("=" * 50)
    
    # Create tester instance
    tester = ABTestingTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    print("\n🏁 Testing completed!")
    print("Check the logs above for detailed results.")

if __name__ == "__main__":
    main()
