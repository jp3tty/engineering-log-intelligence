"""
Test ML Models
==============

This script demonstrates how our machine learning models work by testing
them with sample log data.

For beginners: This script shows you how to use our AI models and what
kind of results they produce.

Author: Engineering Log Intelligence Team
Date: September 21, 2025
"""

import json
import logging
import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to the Python path
project_root = os.path.dirname(__file__)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'external_services'))

# Import ML modules directly
from external_services.ml.log_classifier import LogClassifier
from external_services.ml.anomaly_detector import AnomalyDetector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_training_data():
    """
    Create sample training data for our ML models.
    
    For beginners: This creates fake log data that we can use to teach
    our AI models what different types of logs look like.
    """
    logger.info("Creating sample training data...")
    
    training_data = []
    
    # Security logs
    security_logs = [
        {"message": "Failed login attempt from IP 192.168.1.100", "category": "security"},
        {"message": "Unauthorized access attempt to admin panel", "category": "security"},
        {"message": "Security breach detected in user database", "category": "security"},
        {"message": "Multiple failed authentication attempts", "category": "security"},
        {"message": "Suspicious network activity from unknown IP", "category": "security"},
    ]
    
    # Performance logs
    performance_logs = [
        {"message": "High CPU usage detected: 95%", "category": "performance"},
        {"message": "Database query taking 5.2 seconds", "category": "performance"},
        {"message": "Memory usage exceeded 80% threshold", "category": "performance"},
        {"message": "Slow response time: 3.4 seconds", "category": "performance"},
        {"message": "Disk space running low: 15% remaining", "category": "performance"},
    ]
    
    # System logs
    system_logs = [
        {"message": "System startup completed successfully", "category": "system"},
        {"message": "Service restarted due to memory leak", "category": "system"},
        {"message": "Database connection pool initialized", "category": "system"},
        {"message": "Scheduled maintenance completed", "category": "system"},
        {"message": "System health check passed", "category": "system"},
    ]
    
    # Application logs
    application_logs = [
        {"message": "User profile updated successfully", "category": "application"},
        {"message": "New order created: #12345", "category": "application"},
        {"message": "Payment processed for order #12345", "category": "application"},
        {"message": "Email notification sent to user", "category": "application"},
        {"message": "Report generated for Q3 2025", "category": "application"},
    ]
    
    # Database logs
    database_logs = [
        {"message": "Database connection established", "category": "database"},
        {"message": "Query executed successfully: SELECT * FROM users", "category": "database"},
        {"message": "Database backup completed", "category": "database"},
        {"message": "Index optimization finished", "category": "database"},
        {"message": "Transaction committed successfully", "category": "database"},
    ]
    
    # Network logs
    network_logs = [
        {"message": "Network connection established", "category": "network"},
        {"message": "DNS resolution completed", "category": "network"},
        {"message": "SSL handshake successful", "category": "network"},
        {"message": "Connection timeout after 30 seconds", "category": "network"},
        {"message": "Network interface up", "category": "network"},
    ]
    
    # Authentication logs
    auth_logs = [
        {"message": "User login successful", "category": "authentication"},
        {"message": "Password reset requested", "category": "authentication"},
        {"message": "Token refresh completed", "category": "authentication"},
        {"message": "Session expired, user logged out", "category": "authentication"},
        {"message": "Two-factor authentication enabled", "category": "authentication"},
    ]
    
    # Error logs
    error_logs = [
        {"message": "Application error: NullPointerException", "category": "error"},
        {"message": "Database connection failed", "category": "error"},
        {"message": "File not found: config.json", "category": "error"},
        {"message": "Invalid input parameters", "category": "error"},
        {"message": "Service unavailable", "category": "error"},
    ]
    
    # Combine all logs
    all_logs = (security_logs + performance_logs + system_logs + 
                application_logs + database_logs + network_logs + 
                auth_logs + error_logs)
    
    # Add metadata to each log entry
    for i, log in enumerate(all_logs):
        log_entry = {
            "log_id": f"log_{i+1:04d}",
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
            "level": random.choice(["INFO", "WARN", "ERROR", "DEBUG"]),
            "source_type": random.choice(["splunk", "sap", "application"]),
            "message": log["message"],
            "category": log["category"],
            "ip_address": f"192.168.1.{random.randint(1, 254)}",
            "response_time_ms": random.uniform(10, 1000),
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        training_data.append(log_entry)
    
    logger.info(f"Created {len(training_data)} training samples")
    return training_data

def create_sample_test_logs():
    """
    Create sample test logs to demonstrate our ML models.
    
    For beginners: This creates some test log entries that we can analyze
    to see how well our AI models work.
    """
    logger.info("Creating sample test logs...")
    
    test_logs = [
        {
            "log_id": "test_001",
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "source_type": "application",
            "message": "Critical security breach detected in user authentication system",
            "ip_address": "10.0.0.100",
            "response_time_ms": 2500.0,
            "user_agent": "curl/7.68.0"
        },
        {
            "log_id": "test_002", 
            "timestamp": datetime.now().isoformat(),
            "level": "WARN",
            "source_type": "splunk",
            "message": "Database query taking unusually long: 8.5 seconds",
            "ip_address": "192.168.1.50",
            "response_time_ms": 8500.0,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },
        {
            "log_id": "test_003",
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "source_type": "sap",
            "message": "User successfully logged into SAP system",
            "ip_address": "172.16.0.25",
            "response_time_ms": 150.0,
            "user_agent": "SAP GUI 7.50"
        },
        {
            "log_id": "test_004",
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "source_type": "application",
            "message": "Failed to connect to external API service",
            "ip_address": "10.0.0.75",
            "response_time_ms": 5000.0,
            "user_agent": "Python-requests/2.25.1"
        },
        {
            "log_id": "test_005",
            "timestamp": datetime.now().isoformat(),
            "level": "FATAL",
            "source_type": "system",
            "message": "System shutdown due to critical memory leak",
            "ip_address": "127.0.0.1",
            "response_time_ms": 0.0,
            "user_agent": "system"
        }
    ]
    
    logger.info(f"Created {len(test_logs)} test logs")
    return test_logs

def test_ml_models():
    """
    Test our ML models with sample data.
    
    For beginners: This function shows you how to use our AI models
    and what kind of results they produce.
    """
    logger.info("Starting ML models test...")
    
    try:
        # Initialize individual models
        classifier = LogClassifier()
        anomaly_detector = AnomalyDetector()
        logger.info("ML models initialized")
        
        # Create training data
        training_data = create_sample_training_data()
        logger.info(f"Created {len(training_data)} training samples")
        
        # Train the models
        logger.info("Training log classifier...")
        classifier_results = classifier.train(training_data)
        
        logger.info("Training anomaly detector...")
        anomaly_results = anomaly_detector.train(training_data)
        
        logger.info("Training completed successfully")
        
        # Print training results
        print("\n" + "="*60)
        print("TRAINING RESULTS")
        print("="*60)
        print("Log Classifier:")
        print(json.dumps(classifier_results, indent=2))
        print("\nAnomaly Detector:")
        print(json.dumps(anomaly_results, indent=2))
        
        # Create test logs
        test_logs = create_sample_test_logs()
        
        # Test each log entry
        print("\n" + "="*60)
        print("TESTING ML MODELS")
        print("="*60)
        
        for i, test_log in enumerate(test_logs, 1):
            print(f"\n--- Test Log {i} ---")
            print(f"Message: {test_log['message']}")
            print(f"Level: {test_log['level']}")
            print(f"Source: {test_log['source_type']}")
            
            # Classify the log
            classification = classifier.predict(test_log['message'])
            print(f"\nClassification Results:")
            print(f"  Category: {classification['category']}")
            print(f"  Confidence: {classification['confidence']:.2%}")
            
            # Detect anomalies
            anomaly = anomaly_detector.detect_anomaly(test_log)
            print(f"\nAnomaly Detection Results:")
            print(f"  Anomaly Detected: {anomaly['is_anomaly']}")
            if anomaly['is_anomaly']:
                print(f"  Anomaly Type: {anomaly['anomaly_type']}")
                print(f"  Confidence: {anomaly['confidence']:.2%}")
                print(f"  Explanation: {anomaly['explanation']}")
            
            # Generate summary
            risk_level = 'low'
            action_required = False
            insights = []
            
            if classification['category'] in ['security', 'error'] and classification['confidence'] > 0.8:
                risk_level = 'high'
                action_required = True
                insights.append(f"High-confidence {classification['category']} issue detected")
            
            if anomaly['is_anomaly'] and anomaly['confidence'] > 0.8:
                risk_level = 'high'
                action_required = True
                insights.append(f"High-confidence {anomaly['anomaly_type']} anomaly detected")
            elif anomaly['is_anomaly']:
                risk_level = 'medium'
                insights.append(f"Potential {anomaly['anomaly_type']} anomaly detected")
            
            print(f"\nSummary:")
            print(f"  Risk Level: {risk_level}")
            print(f"  Action Required: {action_required}")
            if insights:
                print(f"  Key Insights: {', '.join(insights)}")
        
        # Test batch analysis
        print("\n" + "="*60)
        print("BATCH ANALYSIS TEST")
        print("="*60)
        
        anomaly_count = 0
        for test_log in test_logs:
            anomaly = anomaly_detector.detect_anomaly(test_log)
            if anomaly['is_anomaly']:
                anomaly_count += 1
        
        print(f"Analyzed {len(test_logs)} logs")
        print(f"Anomalies detected: {anomaly_count}/{len(test_logs)}")
        
        # Get model info
        print("\n" + "="*60)
        print("MODEL INFORMATION")
        print("="*60)
        
        classifier_info = classifier.get_model_info()
        anomaly_info = anomaly_detector.get_model_info()
        
        print("Log Classifier:")
        print(json.dumps(classifier_info, indent=2))
        print("\nAnomaly Detector:")
        print(json.dumps(anomaly_info, indent=2))
        
        logger.info("ML models test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error testing ML models: {str(e)}")
        return False

def main():
    """Main function to run the ML models test."""
    print("Machine Learning Models Test")
    print("="*60)
    print("This script demonstrates how our AI models work by:")
    print("1. Creating sample training data")
    print("2. Training the models on this data")
    print("3. Testing the models with new log entries")
    print("4. Showing the analysis results")
    print("="*60)
    
    success = test_ml_models()
    
    if success:
        print("\n✅ ML models test completed successfully!")
        print("\nWhat we learned:")
        print("- Our AI models can classify logs into categories (security, performance, etc.)")
        print("- Our anomaly detector can identify unusual patterns in logs")
        print("- The models provide confidence scores and explanations")
        print("- We can analyze logs individually or in batches")
    else:
        print("\n❌ ML models test failed!")
        print("Check the logs for error details.")

if __name__ == "__main__":
    main()
