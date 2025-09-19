"""
Rate limiting middleware for the Engineering Log Intelligence System.
Implements per-user and per-endpoint rate limiting.
"""

import time
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Rate limiter with sliding window algorithm."""
    
    def __init__(self):
        """Initialize the rate limiter."""
        # In-memory storage for rate limiting (in production, use Redis)
        self.requests = {}  # {key: [(timestamp, count), ...]}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
        # Default rate limits
        self.default_limits = {
            'login': {'requests': 5, 'window': 300},  # 5 requests per 5 minutes
            'register': {'requests': 3, 'window': 3600},  # 3 requests per hour
            'api': {'requests': 1000, 'window': 3600},  # 1000 requests per hour
            'search': {'requests': 100, 'window': 300},  # 100 requests per 5 minutes
            'admin': {'requests': 200, 'window': 300},  # 200 requests per 5 minutes
        }
        
        logger.info("Rate limiter initialized")
    
    def _get_rate_limit_key(self, user_id: Optional[int], endpoint: str, ip_address: Optional[str] = None) -> str:
        """Generate a rate limit key."""
        if user_id:
            return f"user:{user_id}:{endpoint}"
        elif ip_address:
            return f"ip:{ip_address}:{endpoint}"
        else:
            return f"global:{endpoint}"
    
    def _cleanup_old_requests(self):
        """Clean up old request records."""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 3600  # Keep only last hour
        
        for key in list(self.requests.keys()):
            self.requests[key] = [
                (timestamp, count) for timestamp, count in self.requests[key]
                if timestamp > cutoff_time
            ]
            if not self.requests[key]:
                del self.requests[key]
        
        self.last_cleanup = current_time
    
    def _get_request_count(self, key: str, window_seconds: int) -> int:
        """Get the number of requests in the current window."""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        if key not in self.requests:
            return 0
        
        # Count requests in the window
        count = sum(
            count for timestamp, count in self.requests[key]
            if timestamp > window_start
        )
        
        return count
    
    def _record_request(self, key: str, count: int = 1):
        """Record a request."""
        current_time = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        self.requests[key].append((current_time, count))
    
    def check_rate_limit(
        self,
        user_id: Optional[int] = None,
        endpoint: str = 'api',
        ip_address: Optional[str] = None,
        custom_limits: Optional[Dict[str, int]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is within rate limits.
        
        Returns:
            (is_allowed, rate_limit_info)
        """
        try:
            # Clean up old requests
            self._cleanup_old_requests()
            
            # Get rate limits
            limits = custom_limits or self.default_limits.get(endpoint, self.default_limits['api'])
            max_requests = limits['requests']
            window_seconds = limits['window']
            
            # Generate rate limit key
            key = self._get_rate_limit_key(user_id, endpoint, ip_address)
            
            # Check current request count
            current_count = self._get_request_count(key, window_seconds)
            
            # Check if limit exceeded
            if current_count >= max_requests:
                reset_time = time.time() + window_seconds
                
                rate_limit_info = {
                    'allowed': False,
                    'limit': max_requests,
                    'remaining': 0,
                    'reset_time': reset_time,
                    'retry_after': window_seconds,
                    'endpoint': endpoint,
                    'user_id': user_id,
                    'ip_address': ip_address
                }
                
                logger.warning(
                    "Rate limit exceeded",
                    key=key,
                    current_count=current_count,
                    limit=max_requests,
                    window=window_seconds
                )
                
                return False, rate_limit_info
            
            # Record the request
            self._record_request(key)
            
            # Calculate remaining requests
            remaining = max(0, max_requests - current_count - 1)
            reset_time = time.time() + window_seconds
            
            rate_limit_info = {
                'allowed': True,
                'limit': max_requests,
                'remaining': remaining,
                'reset_time': reset_time,
                'retry_after': 0,
                'endpoint': endpoint,
                'user_id': user_id,
                'ip_address': ip_address
            }
            
            return True, rate_limit_info
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            # On error, allow the request but log the issue
            return True, {
                'allowed': True,
                'error': str(e),
                'endpoint': endpoint
            }
    
    def get_rate_limit_headers(self, rate_limit_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate rate limit headers for the response."""
        headers = {
            'X-RateLimit-Limit': str(rate_limit_info.get('limit', 0)),
            'X-RateLimit-Remaining': str(rate_limit_info.get('remaining', 0)),
            'X-RateLimit-Reset': str(int(rate_limit_info.get('reset_time', 0))),
        }
        
        if not rate_limit_info.get('allowed', True):
            headers['Retry-After'] = str(rate_limit_info.get('retry_after', 0))
        
        return headers


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(
    user_id: Optional[int] = None,
    endpoint: str = 'api',
    ip_address: Optional[str] = None,
    custom_limits: Optional[Dict[str, int]] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Check rate limit using the global rate limiter."""
    return rate_limiter.check_rate_limit(user_id, endpoint, ip_address, custom_limits)


def get_rate_limit_headers(rate_limit_info: Dict[str, Any]) -> Dict[str, str]:
    """Get rate limit headers using the global rate limiter."""
    return rate_limiter.get_rate_limit_headers(rate_limit_info)


def rate_limit_middleware(endpoint: str = 'api', custom_limits: Optional[Dict[str, int]] = None):
    """
    Decorator for rate limiting Vercel Functions.
    
    Usage:
    @rate_limit_middleware('login')
    def login_handler(request):
        # handler code
    """
    def decorator(func):
        def wrapper(request):
            # Extract user ID and IP address
            user_id = None
            ip_address = None
            
            # Try to get user ID from authentication
            try:
                from ..auth.middleware import authenticate_request
                auth_result = authenticate_request(request)
                if auth_result['success']:
                    user_id = auth_result['user'].id
            except:
                pass  # Not authenticated, use IP-based limiting
            
            # Get IP address from headers
            headers = request.get('headers', {})
            ip_address = (
                headers.get('x-forwarded-for', '').split(',')[0].strip() or
                headers.get('x-real-ip', '') or
                headers.get('remote-addr', '') or
                'unknown'
            )
            
            # Check rate limit
            allowed, rate_limit_info = check_rate_limit(
                user_id=user_id,
                endpoint=endpoint,
                ip_address=ip_address,
                custom_limits=custom_limits
            )
            
            if not allowed:
                # Return rate limit exceeded response
                headers = get_rate_limit_headers(rate_limit_info)
                
                return {
                    'statusCode': 429,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        **headers
                    },
                    'body': json.dumps({
                        'error': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Too many requests. Please try again later.',
                        'details': rate_limit_info,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                }
            
            # Call the original function
            response = func(request)
            
            # Add rate limit headers to successful responses
            if isinstance(response, dict) and response.get('statusCode') == 200:
                rate_limit_headers = get_rate_limit_headers(rate_limit_info)
                if 'headers' not in response:
                    response['headers'] = {}
                response['headers'].update(rate_limit_headers)
            
            return response
        
        return wrapper
    return decorator
