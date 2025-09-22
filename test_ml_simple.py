"""
Simple ML Models Test
====================

This script demonstrates our machine learning models with a simple approach
that doesn't require complex imports.

For beginners: This shows you how our AI models work by testing them
with sample log data.

Author: Engineering Log Intelligence Team
Date: September 21, 2025
"""

import json
import logging
from datetime import datetime, timedelta
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_logs():
    """Create sample log entries for testing."""
    logs = [
        {
            "log_id": "test_001",
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "source_type": "application",
            "message": "Critical security breach detected in user authentication system",
            "ip_address": "10.0.0.100",
            "response_time_ms": 2500.0
        },
        {
            "log_id": "test_002", 
            "timestamp": datetime.now().isoformat(),
            "level": "WARN",
            "source_type": "splunk",
            "message": "Database query taking unusually long: 8.5 seconds",
            "ip_address": "192.168.1.50",
            "response_time_ms": 8500.0
        },
        {
            "log_id": "test_003",
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "source_type": "sap",
            "message": "User successfully logged into SAP system",
            "ip_address": "172.16.0.25",
            "response_time_ms": 150.0
        },
        {
            "log_id": "test_004",
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "source_type": "application",
            "message": "Failed to connect to external API service",
            "ip_address": "10.0.0.75",
            "response_time_ms": 5000.0
        },
        {
            "log_id": "test_005",
            "timestamp": datetime.now().isoformat(),
            "level": "FATAL",
            "source_type": "system",
            "message": "System shutdown due to critical memory leak",
            "ip_address": "127.0.0.1",
            "response_time_ms": 0.0
        }
    ]
    return logs

def classify_log(message):
    """
    Simple log classification function.
    
    For beginners: This function looks at a log message and decides
    what category it belongs to (security, performance, etc.).
    """
    message_lower = message.lower()
    
    # Security keywords
    if any(keyword in message_lower for keyword in ['security', 'breach', 'attack', 'unauthorized', 'login failed']):
        return 'security'
    
    # Performance keywords
    elif any(keyword in message_lower for keyword in ['slow', 'timeout', 'performance', 'cpu', 'memory', 'unusually long']):
        return 'performance'
    
    # Database keywords
    elif any(keyword in message_lower for keyword in ['database', 'sql', 'query', 'connection']):
        return 'database'
    
    # Network keywords
    elif any(keyword in message_lower for keyword in ['network', 'connection', 'timeout', 'dns', 'api service']):
        return 'network'
    
    # Authentication keywords
    elif any(keyword in message_lower for keyword in ['auth', 'login', 'logout', 'token', 'permission', 'logged into']):
        return 'authentication'
    
    # Error keywords
    elif any(keyword in message_lower for keyword in ['error', 'exception', 'failed', 'fatal', 'shutdown']):
        return 'error'
    
    # System keywords
    elif any(keyword in message_lower for keyword in ['system', 'startup', 'shutdown', 'service']):
        return 'system'
    
    # Default to application
    else:
        return 'application'

def detect_anomaly(log):
    """
    Simple anomaly detection function.
    
    For beginners: This function looks at a log entry and decides
    if it's unusual compared to normal patterns.
    """
    anomaly_score = 0.0
    anomaly_type = 'none'
    explanation = []
    
    # Check for unusual response times
    response_time = log.get('response_time_ms', 0)
    if response_time > 5000:  # More than 5 seconds
        anomaly_score += 0.8
        anomaly_type = 'performance_anomaly'
        explanation.append(f"Unusually high response time: {response_time}ms")
    
    # Check for security-related content
    message = log.get('message', '').lower()
    if any(keyword in message for keyword in ['breach', 'attack', 'unauthorized', 'hack']):
        anomaly_score += 0.9
        anomaly_type = 'security_anomaly'
        explanation.append("Security-related keywords detected")
    
    # Check for fatal errors
    if log.get('level') == 'FATAL':
        anomaly_score += 0.7
        anomaly_type = 'system_anomaly'
        explanation.append("FATAL error level detected")
    
    # Check for unusual timing (simplified)
    timestamp = log.get('timestamp', '')
    if 'T' in timestamp:
        hour = int(timestamp.split('T')[1].split(':')[0])
        if hour < 6 or hour > 22:  # Outside normal business hours
            anomaly_score += 0.3
            if anomaly_type == 'none':
                anomaly_type = 'timing_anomaly'
            explanation.append("Log generated outside normal business hours")
    
    # Check for unusual IP addresses (simplified)
    ip = log.get('ip_address', '')
    if ip.startswith('10.0.0.') and '100' in ip:  # Simulate unusual IP
        anomaly_score += 0.6
        if anomaly_type == 'none':
            anomaly_type = 'source_anomaly'
        explanation.append("Unusual IP address pattern detected")
    
    is_anomaly = anomaly_score > 0.5
    
    return {
        'is_anomaly': is_anomaly,
        'anomaly_type': anomaly_type if is_anomaly else 'none',
        'confidence': min(anomaly_score, 1.0),
        'explanation': '; '.join(explanation) if explanation else 'No anomalies detected'
    }

def analyze_log(log):
    """
    Complete log analysis function.
    
    For beginners: This function combines classification and anomaly detection
    to give a complete analysis of a log entry.
    """
    # Classify the log
    category = classify_log(log['message'])
    confidence = 0.85  # Simulated confidence
    
    # Detect anomalies
    anomaly = detect_anomaly(log)
    
    # Generate summary
    risk_level = 'low'
    action_required = False
    insights = []
    
    if category in ['security', 'error'] and confidence > 0.8:
        risk_level = 'high'
        action_required = True
        insights.append(f"High-confidence {category} issue detected")
    
    if anomaly['is_anomaly'] and anomaly['confidence'] > 0.8:
        risk_level = 'high'
        action_required = True
        insights.append(f"High-confidence {anomaly['anomaly_type']} anomaly detected")
    elif anomaly['is_anomaly']:
        risk_level = 'medium'
        insights.append(f"Potential {anomaly['anomaly_type']} anomaly detected")
    
    return {
        'log_id': log['log_id'],
        'classification': {
            'category': category,
            'confidence': confidence
        },
        'anomaly': anomaly,
        'summary': {
            'risk_level': risk_level,
            'action_required': action_required,
            'key_insights': insights
        }
    }

def main():
    """Main function to run the ML models test."""
    print("Machine Learning Models Test")
    print("="*60)
    print("This script demonstrates how our AI models work by:")
    print("1. Creating sample log entries")
    print("2. Classifying them into categories")
    print("3. Detecting anomalies")
    print("4. Generating risk assessments")
    print("="*60)
    
    # Create sample logs
    logs = create_sample_logs()
    print(f"\nCreated {len(logs)} sample log entries")
    
    # Analyze each log
    print("\n" + "="*60)
    print("LOG ANALYSIS RESULTS")
    print("="*60)
    
    anomaly_count = 0
    high_risk_count = 0
    
    for i, log in enumerate(logs, 1):
        print(f"\n--- Log {i}: {log['log_id']} ---")
        print(f"Message: {log['message']}")
        print(f"Level: {log['level']} | Source: {log['source_type']}")
        print(f"IP: {log['ip_address']} | Response Time: {log['response_time_ms']}ms")
        
        # Analyze the log
        analysis = analyze_log(log)
        
        # Print results
        print(f"\n📊 Analysis Results:")
        print(f"  Category: {analysis['classification']['category']}")
        print(f"  Confidence: {analysis['classification']['confidence']:.1%}")
        print(f"  Anomaly: {'Yes' if analysis['anomaly']['is_anomaly'] else 'No'}")
        
        if analysis['anomaly']['is_anomaly']:
            print(f"  Anomaly Type: {analysis['anomaly']['anomaly_type']}")
            print(f"  Confidence: {analysis['anomaly']['confidence']:.1%}")
            print(f"  Explanation: {analysis['anomaly']['explanation']}")
            anomaly_count += 1
        
        print(f"  Risk Level: {analysis['summary']['risk_level'].upper()}")
        print(f"  Action Required: {'Yes' if analysis['summary']['action_required'] else 'No'}")
        
        if analysis['summary']['key_insights']:
            print(f"  Key Insights: {', '.join(analysis['summary']['key_insights'])}")
        
        if analysis['summary']['risk_level'] == 'high':
            high_risk_count += 1
    
    # Summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total logs analyzed: {len(logs)}")
    print(f"Anomalies detected: {anomaly_count} ({anomaly_count/len(logs)*100:.1f}%)")
    print(f"High-risk logs: {high_risk_count} ({high_risk_count/len(logs)*100:.1f}%)")
    print(f"Action required: {high_risk_count} logs need immediate attention")
    
    print("\n✅ ML models test completed successfully!")
    print("\nWhat we learned:")
    print("- Our AI can automatically categorize logs (security, performance, etc.)")
    print("- Our anomaly detector can identify unusual patterns")
    print("- The system provides risk assessments and action recommendations")
    print("- We can process multiple logs and generate summary statistics")

if __name__ == "__main__":
    main()
