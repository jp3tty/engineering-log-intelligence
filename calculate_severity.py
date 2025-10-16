"""
Business Severity Calculator
============================

This module calculates business impact severity for log entries.
Unlike log levels (INFO, ERROR), severity indicates actual business impact.

Author: Engineering Log Intelligence Team
Date: October 16, 2025
"""

from typing import Dict
from datetime import datetime


def calculate_business_severity(log: Dict) -> str:
    """
    Calculate business severity based on multiple factors.
    
    Returns one of: 'critical', 'high', 'medium', 'low'
    
    Severity considers:
    - Service criticality (which service generated the log)
    - Log level (FATAL > ERROR > WARN > INFO)
    - Message content (what kind of error)
    - Endpoint criticality (which endpoint was affected)
    - Context (time of day, frequency, etc.)
    
    Args:
        log: Dictionary with fields like level, message, source_type, endpoint, etc.
        
    Returns:
        Severity string: 'critical', 'high', 'medium', or 'low'
    """
    score = 0
    
    # ========================================================================
    # Factor 1: Service Criticality (0-40 points)
    # ========================================================================
    source_type = log.get('source_type', '').lower()
    
    # Critical services - revenue/auth impacting
    if any(keyword in source_type for keyword in [
        'payment', 'checkout', 'auth', 'billing', 'transaction'
    ]):
        score += 40
    # High priority services - core functionality
    elif any(keyword in source_type for keyword in [
        'user', 'order', 'inventory', 'cart', 'product'
    ]):
        score += 30
    # Medium priority services - supporting functionality
    elif any(keyword in source_type for keyword in [
        'notification', 'email', 'analytics', 'search', 'recommendation'
    ]):
        score += 20
    # Low priority services - internal/testing
    elif any(keyword in source_type for keyword in [
        'test', 'dev', 'debug', 'health', 'metrics', 'monitoring'
    ]):
        score += 5
    else:
        # Unknown service - default to medium
        score += 25
    
    # ========================================================================
    # Factor 2: Log Level (0-30 points)
    # ========================================================================
    level = log.get('level', 'INFO').upper()
    
    if level == 'FATAL':
        score += 30
    elif level == 'ERROR':
        score += 25
    elif level == 'WARN':
        score += 15
    elif level == 'DEBUG':
        score += 3
    else:  # INFO
        score += 5
    
    # ========================================================================
    # Factor 3: Message Content - Error Type (0-20 points)
    # ========================================================================
    message = log.get('message', '').lower()
    
    # Critical error keywords - immediate business impact
    if any(keyword in message for keyword in [
        'payment failed', 'payment error', 'transaction failed',
        'unauthorized access', 'security breach', 'data breach',
        'sql injection', 'authentication bypass', 'authorization failed'
    ]):
        score += 20
    
    # High severity keywords - significant operational issues
    elif any(keyword in message for keyword in [
        'database connection failed', 'connection timeout', 'connection refused',
        'service unavailable', 'out of memory', 'disk full',
        'deadlock', 'database error', 'cannot connect'
    ]):
        score += 15
    
    # Medium severity keywords - performance/degradation
    elif any(keyword in message for keyword in [
        'slow response', 'timeout', 'degraded', 'retry',
        'rate limit', 'throttle', 'queue full',
        'cache miss', 'high latency'
    ]):
        score += 10
    
    # Low severity keywords - routine operations
    elif any(keyword in message for keyword in [
        'started successfully', 'completed', 'health check',
        'test', 'debug', 'trace', 'warming up'
    ]):
        score += 3
    
    # Default for unmatched messages
    else:
        score += 8
    
    # ========================================================================
    # Factor 4: Endpoint Criticality (0-10 points)
    # ========================================================================
    endpoint = log.get('endpoint', '').lower() if log.get('endpoint') else ''
    
    # Critical endpoints - customer-facing transactions
    if any(ep in endpoint for ep in [
        '/checkout', '/payment', '/purchase', '/transaction',
        '/login', '/authenticate', '/authorize', '/register'
    ]):
        score += 10
    
    # High priority endpoints - core API operations
    elif any(ep in endpoint for ep in [
        '/order', '/cart', '/user', '/account',
        '/inventory', '/product', '/api/v1'
    ]):
        score += 7
    
    # Medium priority endpoints - supporting features
    elif any(ep in endpoint for ep in [
        '/search', '/recommend', '/analytics', '/notification'
    ]):
        score += 5
    
    # Low priority endpoints - health/monitoring
    elif any(ep in endpoint for ep in [
        '/health', '/ping', '/status', '/metrics',
        '/actuator', '/debug', '/test'
    ]):
        score += 1
    
    # No endpoint or default
    else:
        score += 5
    
    # ========================================================================
    # Bonus Adjustments (can push score up or down)
    # ========================================================================
    
    # HTTP Status Code considerations
    http_status = log.get('http_status', 0)
    if http_status >= 500:  # Server errors
        score += 5
    elif http_status == 401 or http_status == 403:  # Auth issues
        score += 3
    elif http_status >= 400:  # Client errors
        score += 2
    
    # Response time considerations
    response_time = log.get('response_time_ms', 0)
    if response_time > 5000:  # > 5 seconds
        score += 5
    elif response_time > 3000:  # > 3 seconds
        score += 3
    elif response_time > 1000:  # > 1 second
        score += 1
    
    # Anomaly flag from database (if already marked as anomaly)
    if log.get('is_anomaly', False):
        score += 10
    
    # ========================================================================
    # Convert Score to Severity Level (0-100+ scale)
    # ========================================================================
    
    if score >= 85:
        return 'critical'
    elif score >= 60:
        return 'high'
    elif score >= 35:
        return 'medium'
    else:
        return 'low'


def explain_severity(log: Dict, severity: str) -> str:
    """
    Generate human-readable explanation for why a severity was assigned.
    
    Args:
        log: The log entry
        severity: The calculated severity
        
    Returns:
        Explanation string
    """
    reasons = []
    
    source = log.get('source_type', 'unknown')
    level = log.get('level', 'INFO')
    message = log.get('message', '')
    
    # Explain service criticality
    if any(k in source.lower() for k in ['payment', 'auth', 'checkout']):
        reasons.append(f"Critical service: {source}")
    
    # Explain log level
    if level in ['FATAL', 'ERROR']:
        reasons.append(f"High severity log level: {level}")
    
    # Explain message content
    if 'payment failed' in message.lower():
        reasons.append("Payment failure detected")
    elif 'connection' in message.lower() and 'failed' in message.lower():
        reasons.append("Connection failure")
    elif 'unauthorized' in message.lower():
        reasons.append("Security concern")
    
    # Explain endpoint
    endpoint = log.get('endpoint', '')
    if '/payment' in endpoint or '/checkout' in endpoint:
        reasons.append(f"Critical endpoint: {endpoint}")
    
    if reasons:
        return f"Severity '{severity}' because: " + "; ".join(reasons)
    else:
        return f"Severity '{severity}' based on standard classification"


def get_severity_stats(logs: list) -> Dict:
    """
    Calculate severity distribution statistics for a set of logs.
    
    Args:
        logs: List of log dictionaries
        
    Returns:
        Dictionary with severity counts and percentages
    """
    from collections import Counter
    
    severities = [calculate_business_severity(log) for log in logs]
    counts = Counter(severities)
    total = len(severities)
    
    return {
        'total_logs': total,
        'counts': dict(counts),
        'percentages': {
            severity: (count / total * 100) 
            for severity, count in counts.items()
        },
        'distribution': {
            'critical': counts.get('critical', 0),
            'high': counts.get('high', 0),
            'medium': counts.get('medium', 0),
            'low': counts.get('low', 0)
        }
    }


if __name__ == "__main__":
    # Test the severity calculator
    print("🧪 Testing Business Severity Calculator")
    print("=" * 70)
    print()
    
    test_cases = [
        {
            'source_type': 'payment-api',
            'level': 'ERROR',
            'message': 'Payment processor connection timeout',
            'endpoint': '/api/checkout/process',
            'http_status': 500,
            'response_time_ms': 5000,
            'expected': 'critical'
        },
        {
            'source_type': 'test-service',
            'level': 'ERROR',
            'message': 'Test database connection failed',
            'endpoint': '/health',
            'http_status': 200,
            'response_time_ms': 100,
            'expected': 'low'
        },
        {
            'source_type': 'user-api',
            'level': 'WARN',
            'message': 'API response time degraded to 2000ms',
            'endpoint': '/api/users/profile',
            'http_status': 200,
            'response_time_ms': 2000,
            'expected': 'medium'
        },
        {
            'source_type': 'health-check',
            'level': 'INFO',
            'message': 'Health check endpoint returned 200 OK',
            'endpoint': '/health',
            'http_status': 200,
            'response_time_ms': 50,
            'expected': 'low'
        },
        {
            'source_type': 'auth-service',
            'level': 'WARN',
            'message': 'Unauthorized access attempt detected from IP 1.2.3.4',
            'endpoint': '/api/login',
            'http_status': 401,
            'response_time_ms': 100,
            'expected': 'high'
        }
    ]
    
    correct = 0
    for i, test in enumerate(test_cases, 1):
        severity = calculate_business_severity(test)
        explanation = explain_severity(test, severity)
        match = '✅' if severity == test['expected'] else '❌'
        
        print(f"Test {i}: {match}")
        print(f"  Message: {test['message']}")
        print(f"  Service: {test['source_type']} | Level: {test['level']}")
        print(f"  Expected: {test['expected']} | Got: {severity}")
        print(f"  {explanation}")
        print()
        
        if severity == test['expected']:
            correct += 1
    
    print("=" * 70)
    print(f"✅ Passed {correct}/{len(test_cases)} tests ({correct/len(test_cases)*100:.1f}%)")
    print()

