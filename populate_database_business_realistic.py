"""
Populate Database with Business-Realistic Log Data
===================================================
Generates realistic log entries that represent actual business-critical services
like payment processing, authentication, checkout, etc.

This creates representative data for ML training.

Author: Engineering Log Intelligence Team
Date: October 16, 2025
"""

import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

load_dotenv('.env.local')
load_dotenv()


def generate_business_realistic_logs(count=10000):
    """Generate business-realistic log entries"""
    
    print(f"🏗️  Generating {count} business-realistic log entries...")
    print()
    
    # Realistic service distribution
    services = {
        # Critical services (10%)
        'payment-api': {'weight': 0.05, 'criticality': 'critical'},
        'checkout-api': {'weight': 0.03, 'criticality': 'critical'},
        'auth-service': {'weight': 0.02, 'criticality': 'critical'},
        
        # High priority services (25%)
        'user-api': {'weight': 0.08, 'criticality': 'high'},
        'order-api': {'weight': 0.07, 'criticality': 'high'},
        'inventory-api': {'weight': 0.05, 'criticality': 'high'},
        'cart-api': {'weight': 0.05, 'criticality': 'high'},
        
        # Medium priority services (40%)
        'product-api': {'weight': 0.12, 'criticality': 'medium'},
        'search-api': {'weight': 0.10, 'criticality': 'medium'},
        'notification-service': {'weight': 0.08, 'criticality': 'medium'},
        'analytics-service': {'weight': 0.05, 'criticality': 'medium'},
        'recommendation-api': {'weight': 0.05, 'criticality': 'medium'},
        
        # Low priority services (25%)
        'health-check': {'weight': 0.10, 'criticality': 'low'},
        'metrics-collector': {'weight': 0.05, 'criticality': 'low'},
        'test-service': {'weight': 0.05, 'criticality': 'low'},
        'dev-sandbox': {'weight': 0.03, 'criticality': 'low'},
        'debug-service': {'weight': 0.02, 'criticality': 'low'},
    }
    
    service_names = list(services.keys())
    service_weights = [services[s]['weight'] for s in service_names]
    
    # Realistic endpoints per service
    endpoints = {
        'payment-api': ['/payment/process', '/payment/validate', '/payment/refund', '/payment/status'],
        'checkout-api': ['/checkout/start', '/checkout/complete', '/checkout/cart', '/checkout/summary'],
        'auth-service': ['/auth/login', '/auth/register', '/auth/logout', '/auth/validate', '/auth/refresh'],
        'user-api': ['/users/profile', '/users/update', '/users/preferences', '/users/avatar'],
        'order-api': ['/orders/create', '/orders/list', '/orders/status', '/orders/cancel'],
        'inventory-api': ['/inventory/check', '/inventory/reserve', '/inventory/release'],
        'cart-api': ['/cart/add', '/cart/remove', '/cart/view', '/cart/clear'],
        'product-api': ['/products/list', '/products/detail', '/products/search', '/products/categories'],
        'search-api': ['/search/products', '/search/autocomplete', '/search/filters'],
        'notification-service': ['/notifications/send', '/notifications/email', '/notifications/sms'],
        'analytics-service': ['/analytics/track', '/analytics/report', '/analytics/metrics'],
        'recommendation-api': ['/recommend/products', '/recommend/similar', '/recommend/personalized'],
        'health-check': ['/health', '/ping', '/status', '/ready'],
        'metrics-collector': ['/metrics', '/stats', '/performance'],
        'test-service': ['/test/api', '/test/health', '/test/mock'],
        'dev-sandbox': ['/dev/test', '/dev/debug'],
        'debug-service': ['/debug/trace', '/debug/logs']
    }
    
    # Realistic log levels with proper distribution
    log_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
    level_weights = [0.20, 0.65, 0.12, 0.025, 0.005]
    
    # Business-realistic messages by level and service criticality
    messages_by_context = {
        'payment-api': {
            'DEBUG': ['Payment validation started', 'Processing payment request', 'Payment gateway connection established'],
            'INFO': ['Payment processed successfully', 'Payment authorization completed', 'Refund processed'],
            'WARN': ['Payment retry attempted', 'Payment gateway slow response', 'Payment validation warning'],
            'ERROR': ['Payment processor connection timeout', 'Payment authorization failed', 'Payment declined by gateway'],
            'FATAL': ['Payment gateway unreachable', 'Payment processing critical failure', 'Payment database connection lost']
        },
        'checkout-api': {
            'DEBUG': ['Cart validation in progress', 'Calculating order total', 'Applying discount codes'],
            'INFO': ['Checkout completed successfully', 'Order confirmed', 'Cart updated'],
            'WARN': ['Inventory low for item', 'Checkout taking longer than expected', 'Discount validation slow'],
            'ERROR': ['Checkout process failed', 'Invalid cart state', 'Payment integration error during checkout'],
            'FATAL': ['Checkout service critical error', 'Order processing system down']
        },
        'auth-service': {
            'DEBUG': ['Token validation in progress', 'Session lookup started', 'Password hash check'],
            'INFO': ['User logged in successfully', 'Authentication token issued', 'User registered successfully'],
            'WARN': ['Failed login attempt', 'Password reset requested', 'Suspicious login pattern detected'],
            'ERROR': ['Authentication failed - invalid credentials', 'Session expired', 'Token validation failed'],
            'FATAL': ['Authentication service unavailable', 'User database connection lost']
        },
        'user-api': {
            'DEBUG': ['User profile lookup', 'Preferences loading', 'Avatar processing'],
            'INFO': ['User profile updated', 'User preferences saved', 'Profile picture uploaded'],
            'WARN': ['User profile incomplete', 'Slow database query for user data'],
            'ERROR': ['User not found', 'Profile update failed', 'Invalid user data'],
            'FATAL': ['User database critical error']
        },
        'default': {
            'DEBUG': ['Debug trace for request processing', 'Function entry point', 'Variable state logged'],
            'INFO': ['Request processed successfully', 'Operation completed', 'Data retrieved'],
            'WARN': ['High memory usage detected', 'Slow response time', 'Rate limit approaching'],
            'ERROR': ['Database connection failed', 'API request timeout', 'File not found'],
            'FATAL': ['Out of memory error', 'Critical system failure', 'Database server unreachable']
        }
    }
    
    logs = []
    base_time = datetime.now(timezone.utc) - timedelta(hours=24)
    
    print(f"📊 Service Distribution:")
    print(f"   Critical (payment, checkout, auth): 10%")
    print(f"   High (user, order, inventory): 25%")
    print(f"   Medium (product, search, etc.): 40%")
    print(f"   Low (health, test, debug): 25%")
    print()
    
    for i in range(count):
        # Select service
        service = random.choices(service_names, weights=service_weights)[0]
        service_info = services[service]
        
        # Select log level (critical services have slightly higher error rates)
        if service_info['criticality'] == 'critical':
            # Critical services: slightly more errors to create training examples
            level_weights_adjusted = [0.18, 0.60, 0.15, 0.05, 0.02]
        elif service_info['criticality'] == 'low':
            # Test/debug services: even fewer errors
            level_weights_adjusted = [0.25, 0.70, 0.045, 0.004, 0.001]
        else:
            level_weights_adjusted = level_weights
        
        level = random.choices(log_levels, weights=level_weights_adjusted)[0]
        
        # Select endpoint
        endpoint = random.choice(endpoints.get(service, ['/api/default']))
        
        # Generate timestamp (spread over last 24 hours, with more recent activity)
        # Weight toward more recent times (last 6 hours get 50% of logs)
        time_offset = random.choices(
            [random.randint(0, 21600), random.randint(21600, 86400)],
            weights=[0.5, 0.5]
        )[0]
        timestamp = base_time + timedelta(seconds=time_offset)
        
        # Select message
        message_pool = messages_by_context.get(service, messages_by_context['default'])
        message = random.choice(message_pool.get(level, ['Default log message']))
        
        # Response time (realistic based on service and level)
        if level in ['ERROR', 'FATAL']:
            response_time = random.randint(1000, 5000)  # Errors take longer
        elif level == 'WARN':
            response_time = random.randint(300, 1500)
        elif service_info['criticality'] == 'critical':
            response_time = random.randint(50, 300)  # Critical services are optimized
        else:
            response_time = random.randint(50, 500)
        
        # HTTP status (realistic)
        if level == 'FATAL':
            http_status = random.choice([500, 503, 504])
        elif level == 'ERROR':
            http_status = random.choice([400, 401, 403, 404, 500, 502])
        elif level == 'WARN':
            http_status = random.choice([200, 201, 429])  # 429 = rate limit
        else:
            http_status = random.choice([200, 201, 204])
        
        # Anomaly detection (errors in critical services are more likely anomalies)
        if level in ['ERROR', 'FATAL'] and service_info['criticality'] in ['critical', 'high']:
            is_anomaly = random.random() < 0.4
        elif level in ['ERROR', 'FATAL']:
            is_anomaly = random.random() < 0.2
        else:
            is_anomaly = random.random() < 0.05
        
        # HTTP method distribution
        if endpoint and '/create' in endpoint or '/add' in endpoint or '/send' in endpoint:
            http_method = 'POST'
        elif endpoint and '/update' in endpoint or '/edit' in endpoint:
            http_method = 'PUT'
        elif endpoint and '/delete' in endpoint or '/remove' in endpoint:
            http_method = 'DELETE'
        else:
            http_method = 'GET'
        
        log_entry = {
            'log_id': str(uuid.uuid4()),
            'timestamp': timestamp,
            'level': level,
            'source_type': 'application',  # Use allowed enum value
            'message': message,
            'host': random.choice(['prod-server-01', 'prod-server-02', 'prod-server-03']),
            'service': service,  # Actual service name (payment-api, user-api, etc.)
            'category': service_info['criticality'],
            'endpoint': endpoint,
            'http_method': http_method,
            'http_status': http_status,
            'response_time_ms': response_time,
            'ip_address': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'request_id': str(uuid.uuid4()),
            'correlation_id': str(uuid.uuid4()),
            'session_id': str(uuid.uuid4()) if random.random() < 0.5 else None,
            'is_anomaly': is_anomaly
        }
        
        logs.append(log_entry)
    
    print(f"✅ Generated {len(logs):,} log entries")
    return logs


def insert_logs(logs):
    """Insert logs into database"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    print(f"🔌 Connecting to database...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    print(f"💾 Inserting {len(logs):,} logs into database...")
    
    insert_query = """
        INSERT INTO log_entries (
            log_id, timestamp, level, source_type, message, host, service,
            category, endpoint, http_method, http_status, response_time_ms,
            ip_address, request_id, correlation_id, session_id, is_anomaly
        ) VALUES (
            %(log_id)s, %(timestamp)s, %(level)s, %(source_type)s, %(message)s,
            %(host)s, %(service)s, %(category)s, %(endpoint)s, %(http_method)s,
            %(http_status)s, %(response_time_ms)s, %(ip_address)s,
            %(request_id)s, %(correlation_id)s, %(session_id)s, %(is_anomaly)s
        )
    """
    
    execute_batch(cursor, insert_query, logs, page_size=1000)
    conn.commit()
    
    print(f"✅ Inserted {len(logs):,} logs successfully")
    
    # Show summary
    from collections import Counter
    services = Counter([log['source_type'] for log in logs])
    levels = Counter([log['level'] for log in logs])
    
    print()
    print("📊 Summary:")
    print("-" * 60)
    print("Top 10 Services:")
    for service, count in services.most_common(10):
        pct = (count / len(logs) * 100)
        print(f"  {service:25}: {count:5,} ({pct:4.1f}%)")
    
    print()
    print("Log Levels:")
    for level in ['FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG']:
        count = levels.get(level, 0)
        pct = (count / len(logs) * 100)
        print(f"  {level:10}: {count:6,} ({pct:5.1f}%)")
    
    cursor.close()
    conn.close()
    return True


if __name__ == '__main__':
    import sys
    
    print("="*70)
    print("🏢 BUSINESS-REALISTIC LOG DATA GENERATOR")
    print("="*70)
    print()
    
    # Get count from command line or default to 10000
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    
    # Generate logs
    logs = generate_business_realistic_logs(count)
    
    # Insert into database
    success = insert_logs(logs)
    
    if success:
        print()
        print("="*70)
        print("✅ DATABASE POPULATED WITH BUSINESS-REALISTIC DATA")
        print("="*70)
        print()
        print("🚀 Next step: Run generate_severity_training_data.py")
        print()
    else:
        print("❌ Failed to populate database")
        sys.exit(1)

