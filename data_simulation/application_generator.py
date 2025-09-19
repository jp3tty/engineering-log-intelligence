"""
Application log generator for data simulation.
Generates realistic application log entries for web apps, microservices, and APIs.
"""

import random
import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import structlog

from .base_generator import BaseLogGenerator

logger = structlog.get_logger(__name__)

class ApplicationLogGenerator(BaseLogGenerator):
    """Generator for application log entries."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize application log generator."""
        super().__init__("application", config)
        
        # Application-specific configuration
        self.application_types = config.get('application_types', [
            'web_app',
            'microservice',
            'api_gateway',
            'database_service',
            'auth_service',
            'notification_service',
            'payment_service',
            'user_service'
        ])
        
        self.frameworks = config.get('frameworks', [
            'Spring Boot',
            'Django',
            'Flask',
            'Express.js',
            'FastAPI',
            'ASP.NET Core',
            'Ruby on Rails',
            'Laravel'
        ])
        
        self.http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        self.http_status_codes = [200, 201, 204, 400, 401, 403, 404, 422, 429, 500, 502, 503, 504]
        self.status_weights = [0.6, 0.1, 0.05, 0.05, 0.02, 0.01, 0.05, 0.02, 0.01, 0.03, 0.02, 0.02, 0.01]
        
        # API endpoints for different services
        self.api_endpoints = {
            'web_app': [
                '/api/users', '/api/auth/login', '/api/auth/logout', '/api/dashboard',
                '/api/profile', '/api/settings', '/api/notifications', '/api/search'
            ],
            'microservice': [
                '/api/v1/users', '/api/v1/orders', '/api/v1/products', '/api/v1/inventory',
                '/api/v1/payments', '/api/v1/notifications', '/api/v1/analytics'
            ],
            'api_gateway': [
                '/gateway/auth', '/gateway/users', '/gateway/orders', '/gateway/products',
                '/gateway/payments', '/gateway/notifications', '/gateway/health'
            ],
            'database_service': [
                '/db/query', '/db/transaction', '/db/backup', '/db/health',
                '/db/performance', '/db/connections'
            ],
            'auth_service': [
                '/auth/login', '/auth/logout', '/auth/refresh', '/auth/validate',
                '/auth/register', '/auth/reset-password', '/auth/verify-email'
            ],
            'notification_service': [
                '/notify/email', '/notify/sms', '/notify/push', '/notify/queue',
                '/notify/templates', '/notify/history'
            ],
            'payment_service': [
                '/payments/process', '/payments/refund', '/payments/status',
                '/payments/webhook', '/payments/methods', '/payments/history'
            ],
            'user_service': [
                '/users/profile', '/users/preferences', '/users/activity',
                '/users/permissions', '/users/audit', '/users/export'
            ]
        }
        
        # Error types and messages
        self.error_types = {
            'validation_error': [
                'Invalid input parameters',
                'Required field missing',
                'Data format validation failed',
                'Business rule violation',
                'Input length exceeds limit'
            ],
            'authentication_error': [
                'Invalid credentials',
                'Token expired',
                'Access denied',
                'Session timeout',
                'Invalid API key'
            ],
            'authorization_error': [
                'Insufficient permissions',
                'Role-based access denied',
                'Resource access forbidden',
                'Admin privileges required'
            ],
            'database_error': [
                'Connection timeout',
                'Query execution failed',
                'Transaction rollback',
                'Deadlock detected',
                'Constraint violation'
            ],
            'network_error': [
                'Connection timeout',
                'Network unreachable',
                'DNS resolution failed',
                'SSL handshake failed',
                'Connection refused'
            ],
            'timeout_error': [
                'Request timeout',
                'Database query timeout',
                'External service timeout',
                'Processing timeout',
                'Connection pool exhausted'
            ],
            'resource_error': [
                'Memory allocation failed',
                'Disk space insufficient',
                'CPU usage exceeded',
                'File handle limit reached',
                'Thread pool exhausted'
            ],
            'business_logic_error': [
                'Invalid business state',
                'Workflow violation',
                'Data consistency error',
                'Business rule conflict',
                'Process validation failed'
            ]
        }
        
        # Performance metrics ranges
        self.response_time_ranges = {
            'fast': (1, 100),      # 1-100ms
            'normal': (100, 500),  # 100-500ms
            'slow': (500, 2000),   # 500ms-2s
            'very_slow': (2000, 10000)  # 2-10s
        }
        
        logger.info(
            "Application log generator initialized",
            application_types=len(self.application_types),
            frameworks=len(self.frameworks),
            error_types=len(self.error_types)
        )
    
    def select_application_type(self) -> str:
        """Select a random application type."""
        return random.choice(self.application_types)
    
    def select_framework(self) -> str:
        """Select a random framework."""
        return random.choice(self.frameworks)
    
    def select_http_method(self) -> str:
        """Select a random HTTP method."""
        return random.choice(self.http_methods)
    
    def select_http_status(self) -> int:
        """Select an HTTP status code based on weights."""
        return random.choices(self.http_status_codes, weights=self.status_weights)[0]
    
    def select_endpoint(self, app_type: str) -> str:
        """Select a random endpoint for the application type."""
        endpoints = self.api_endpoints.get(app_type, ['/api/unknown'])
        return random.choice(endpoints)
    
    def select_error_type(self) -> str:
        """Select a random error type."""
        return random.choice(list(self.error_types.keys()))
    
    def generate_error_message(self, error_type: str) -> str:
        """Generate a random error message for the given error type."""
        messages = self.error_types.get(error_type, ['Unknown error'])
        return random.choice(messages)
    
    def generate_response_time(self, status_code: int) -> float:
        """Generate realistic response time based on status code."""
        if status_code < 400:
            # Success responses - mostly fast to normal
            if random.random() < 0.7:
                range_type = random.choices(['fast', 'normal'], weights=[0.6, 0.4])[0]
            else:
                range_type = random.choices(['slow', 'very_slow'], weights=[0.8, 0.2])[0]
        else:
            # Error responses - can be any range
            range_type = random.choices(['fast', 'normal', 'slow', 'very_slow'], 
                                      weights=[0.1, 0.3, 0.4, 0.2])[0]
        
        min_time, max_time = self.response_time_ranges[range_type]
        return round(random.uniform(min_time, max_time), 2)
    
    def generate_user_agent(self) -> str:
        """Generate a realistic user agent string."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'PostmanRuntime/7.28.4',
            'curl/7.68.0',
            'python-requests/2.28.1',
            'Java/11.0.12',
            'Go-http-client/1.1'
        ]
        return random.choice(user_agents)
    
    def generate_ip_address(self) -> str:
        """Generate a realistic IP address."""
        if random.random() < 0.8:  # 80% internal IPs
            return f"192.168.{random.randint(1, 255)}.{random.randint(1, 254)}"
        else:  # 20% external IPs
            return f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 254)}"
    
    def generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())
    
    def generate_session_id(self) -> str:
        """Generate a session ID."""
        return f"sess_{random.randint(100000, 999999)}_{random.randint(1000, 9999)}"
    
    def generate_correlation_id(self) -> str:
        """Generate a correlation ID for tracing."""
        return f"corr_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{random.randint(1000, 9999)}"
    
    def generate_log(self) -> Dict[str, Any]:
        """Generate a single application log entry."""
        app_type = self.select_application_type()
        framework = self.select_framework()
        http_method = self.select_http_method()
        http_status = self.select_http_status()
        endpoint = self.select_endpoint(app_type)
        response_time = self.generate_response_time(http_status)
        
        # Generate timestamp
        timestamp = self.generate_timestamp()
        
        # Generate log level based on status code
        if http_status >= 500:
            log_level = 'ERROR'
        elif http_status >= 400:
            log_level = 'WARN'
        else:
            log_level = self.select_log_level()
        
        # Generate request details
        request_id = self.generate_request_id()
        session_id = self.generate_session_id()
        correlation_id = self.generate_correlation_id()
        user_agent = self.generate_user_agent()
        ip_address = self.generate_ip_address()
        
        # Generate log message
        if http_status < 400:
            message = f"{http_method} {endpoint} - {http_status} - {response_time}ms"
        else:
            error_type = self.select_error_type()
            error_message = self.generate_error_message(error_type)
            message = f"{http_method} {endpoint} - {http_status} - {error_message} - {response_time}ms"
        
        # Build structured log entry
        log_entry = {
            "log_id": self.generate_log_id(),
            "timestamp": timestamp,
            "level": log_level,
            "message": message,
            "application_type": app_type,
            "framework": framework,
            "http_method": http_method,
            "http_status": http_status,
            "endpoint": endpoint,
            "response_time_ms": response_time,
            "request_id": request_id,
            "session_id": session_id,
            "correlation_id": correlation_id,
            "user_agent": user_agent,
            "ip_address": ip_address,
            "host": self.select_host(),
            "service": self.select_service(),
            "category": self.select_category(),
            "tags": self.generate_tags(),
            "metadata": self.generate_metadata()
        }
        
        # Add error details if it's an error
        if http_status >= 400:
            error_type = self.select_error_type()
            log_entry["error_details"] = {
                "error_type": error_type,
                "error_message": self.generate_error_message(error_type),
                "stack_trace": self._generate_stack_trace(error_type),
                "error_code": f"ERR_{http_status}_{random.randint(1000, 9999)}"
            }
        
        # Add performance metrics
        log_entry["performance_metrics"] = {
            "response_time_ms": response_time,
            "memory_usage_mb": round(random.uniform(50, 500), 2),
            "cpu_usage_percent": round(random.uniform(10, 80), 2),
            "thread_count": random.randint(10, 100),
            "connection_count": random.randint(5, 50)
        }
        
        # Add business context
        log_entry["business_context"] = {
            "user_id": f"user_{random.randint(1000, 9999)}" if random.random() < 0.7 else None,
            "tenant_id": f"tenant_{random.randint(1, 10)}" if random.random() < 0.5 else None,
            "feature_flag": f"feature_{random.choice(['A', 'B', 'C'])}" if random.random() < 0.3 else None,
            "experiment_group": random.choice(['control', 'treatment']) if random.random() < 0.2 else None
        }
        
        return log_entry
    
    def _generate_stack_trace(self, error_type: str) -> str:
        """Generate a realistic stack trace for the error type."""
        stack_traces = {
            'validation_error': [
                'at com.example.ValidationService.validateInput(ValidationService.java:45)',
                'at com.example.UserController.createUser(UserController.java:123)',
                'at org.springframework.web.method.support.InvocableHandlerMethod.doInvoke(InvocableHandlerMethod.java:205)'
            ],
            'database_error': [
                'at org.hibernate.engine.jdbc.spi.SqlExceptionHelper.convert(SqlExceptionHelper.java:113)',
                'at org.hibernate.engine.jdbc.spi.SqlExceptionHelper.convert(SqlExceptionHelper.java:99)',
                'at com.example.UserRepository.save(UserRepository.java:67)'
            ],
            'network_error': [
                'at java.net.Socket.connect(Socket.java:589)',
                'at com.example.ExternalServiceClient.call(ExternalServiceClient.java:89)',
                'at com.example.PaymentService.processPayment(PaymentService.java:156)'
            ],
            'timeout_error': [
                'at java.util.concurrent.CompletableFuture.get(CompletableFuture.java:1995)',
                'at com.example.AsyncService.execute(AsyncService.java:78)',
                'at com.example.OrderService.processOrder(OrderService.java:234)'
            ]
        }
        
        traces = stack_traces.get(error_type, [
            'at com.example.Service.method(Service.java:123)',
            'at com.example.Controller.handle(Controller.java:456)'
        ])
        
        return '\n'.join(traces)
    
    def simulate_anomaly(self) -> Dict[str, Any]:
        """Generate an anomalous application log entry."""
        # Generate a normal log first
        log_entry = self.generate_log()
        
        # Make it anomalous
        anomaly_type = random.choice([
            'unusual_response_time',
            'high_error_rate',
            'unusual_traffic_pattern',
            'resource_exhaustion',
            'security_incident',
            'data_corruption'
        ])
        
        log_entry["anomaly_type"] = anomaly_type
        log_entry["is_anomaly"] = True
        
        if anomaly_type == 'unusual_response_time':
            log_entry["response_time_ms"] = random.uniform(5000, 30000)  # 5-30 seconds
            log_entry["level"] = "WARN"
            log_entry["message"] = f"UNUSUAL RESPONSE TIME: {log_entry['message']}"
        
        elif anomaly_type == 'high_error_rate':
            log_entry["http_status"] = random.choice([500, 502, 503, 504])
            log_entry["level"] = "ERROR"
            log_entry["message"] = f"HIGH ERROR RATE: {log_entry['message']}"
        
        elif anomaly_type == 'unusual_traffic_pattern':
            log_entry["ip_address"] = f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
            log_entry["user_agent"] = "SuspiciousBot/1.0"
            log_entry["level"] = "WARN"
            log_entry["message"] = f"UNUSUAL TRAFFIC: {log_entry['message']}"
        
        elif anomaly_type == 'resource_exhaustion':
            log_entry["performance_metrics"]["memory_usage_mb"] = random.uniform(800, 1000)
            log_entry["performance_metrics"]["cpu_usage_percent"] = random.uniform(90, 100)
            log_entry["level"] = "ERROR"
            log_entry["message"] = f"RESOURCE EXHAUSTION: {log_entry['message']}"
        
        elif anomaly_type == 'security_incident':
            log_entry["http_status"] = 401
            log_entry["ip_address"] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            log_entry["level"] = "FATAL"
            log_entry["message"] = f"SECURITY INCIDENT: {log_entry['message']}"
            log_entry["error_details"] = {
                "error_type": "security_violation",
                "error_message": "Multiple failed authentication attempts",
                "security_alert": True,
                "threat_level": "HIGH"
            }
        
        elif anomaly_type == 'data_corruption':
            log_entry["http_status"] = 500
            log_entry["level"] = "ERROR"
            log_entry["message"] = f"DATA CORRUPTION: {log_entry['message']}"
            log_entry["error_details"] = {
                "error_type": "data_corruption",
                "error_message": "Data integrity check failed",
                "corruption_type": random.choice(['checksum_mismatch', 'format_error', 'encoding_error'])
            }
        
        return log_entry
    
    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple application log entries with realistic distribution."""
        logs = []
        anomaly_count = int(count * self.anomaly_rate)
        error_count = int(count * self.error_rate)
        
        for i in range(count):
            try:
                if i < anomaly_count:
                    # Generate anomaly
                    log_entry = self.simulate_anomaly()
                elif i < anomaly_count + error_count:
                    # Generate error
                    log_entry = self.generate_log()
                    if log_entry["http_status"] < 400:
                        log_entry["http_status"] = random.choice([400, 401, 403, 404, 422, 500, 502, 503])
                        log_entry["level"] = "ERROR"
                else:
                    # Generate normal log
                    log_entry = self.generate_log()
                
                logs.append(log_entry)
            except Exception as e:
                logger.error("Failed to generate application log entry", error=str(e))
                continue
        
        logger.info(
            "Generated application log batch",
            count=len(logs),
            requested=count,
            anomalies=anomaly_count,
            errors=error_count
        )
        
        return logs
