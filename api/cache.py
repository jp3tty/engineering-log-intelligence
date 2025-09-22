"""
Caching utilities for the Engineering Log Intelligence System.
Implements intelligent caching strategies for improved performance.
"""

import json
import time
import hashlib
from typing import Any, Optional, Dict, Union
from functools import wraps
import os

# In-memory cache (Vercel Functions persist between invocations)
_cache = {}
_cache_metadata = {}
_cache_config = {
    "default_ttl": 300,  # 5 minutes
    "max_size": 1000,
    "cleanup_interval": 60  # 1 minute
}

# Cache statistics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "evictions": 0,
    "size": 0
}


def get_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from arguments."""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def is_cache_valid(key: str, ttl: int = None) -> bool:
    """Check if a cache entry is still valid."""
    if key not in _cache_metadata:
        return False
    
    ttl = ttl or _cache_config["default_ttl"]
    return time.time() - _cache_metadata[key]["timestamp"] < ttl


def get_from_cache(key: str) -> Optional[Any]:
    """Get value from cache if valid."""
    if key in _cache and is_cache_valid(key):
        _cache_stats["hits"] += 1
        return _cache[key]
    
    _cache_stats["misses"] += 1
    return None


def set_cache(key: str, value: Any, ttl: int = None) -> None:
    """Set value in cache with TTL."""
    ttl = ttl or _cache_config["default_ttl"]
    
    # Check cache size limit
    if len(_cache) >= _cache_config["max_size"]:
        cleanup_cache()
    
    _cache[key] = value
    _cache_metadata[key] = {
        "timestamp": time.time(),
        "ttl": ttl
    }
    _cache_stats["size"] = len(_cache)


def cleanup_cache() -> None:
    """Remove expired entries from cache."""
    current_time = time.time()
    expired_keys = []
    
    for key, metadata in _cache_metadata.items():
        if current_time - metadata["timestamp"] > metadata["ttl"]:
            expired_keys.append(key)
    
    for key in expired_keys:
        if key in _cache:
            del _cache[key]
        if key in _cache_metadata:
            del _cache_metadata[key]
        _cache_stats["evictions"] += 1
    
    _cache_stats["size"] = len(_cache)


def cached(ttl: int = None, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{get_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            set_cache(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_health_data(ttl: int = 30) -> None:
    """Cache health check data with short TTL."""
    @cached(ttl=ttl, key_prefix="health")
    def get_health_data():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "cached": True
        }
    
    return get_health_data()


def cache_log_schema(ttl: int = 3600) -> Dict[str, Any]:
    """Cache log schema with long TTL."""
    @cached(ttl=ttl, key_prefix="schema")
    def get_log_schema():
        return {
            "fields": [
                "id", "timestamp", "level", "message", "source", "service",
                "hostname", "user_id", "session_id", "request_id", "correlation_id"
            ],
            "indexes": ["timestamp", "level", "source", "service"],
            "searchable_fields": ["message", "source", "service", "hostname"],
            "cached": True
        }
    
    return get_log_schema()


def cache_database_connection_info(ttl: int = 300) -> Dict[str, Any]:
    """Cache database connection information."""
    @cached(ttl=ttl, key_prefix="db_config")
    def get_db_config():
        return {
            "database_url": os.getenv("DATABASE_URL"),
            "elasticsearch_url": os.getenv("ELASTICSEARCH_URL"),
            "kafka_bootstrap": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
            "cached": True
        }
    
    return get_db_config()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    total_requests = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "hit_rate": f"{hit_rate:.2f}%",
        "evictions": _cache_stats["evictions"],
        "current_size": _cache_stats["size"],
        "max_size": _cache_config["max_size"],
        "memory_usage": f"{len(str(_cache))} bytes"
    }


def clear_cache() -> None:
    """Clear all cache entries."""
    global _cache, _cache_metadata
    _cache.clear()
    _cache_metadata.clear()
    _cache_stats["size"] = 0


def cache_log_search_results(query_params: Dict[str, Any], results: Any, ttl: int = 60) -> None:
    """Cache log search results."""
    cache_key = f"log_search:{get_cache_key(query_params)}"
    set_cache(cache_key, results, ttl)


def get_cached_log_search_results(query_params: Dict[str, Any]) -> Optional[Any]:
    """Get cached log search results."""
    cache_key = f"log_search:{get_cache_key(query_params)}"
    return get_from_cache(cache_key)


def cache_user_authentication(user_id: str, auth_data: Dict[str, Any], ttl: int = 1800) -> None:
    """Cache user authentication data."""
    cache_key = f"user_auth:{user_id}"
    set_cache(cache_key, auth_data, ttl)


def get_cached_user_authentication(user_id: str) -> Optional[Dict[str, Any]]:
    """Get cached user authentication data."""
    cache_key = f"user_auth:{user_id}"
    return get_from_cache(cache_key)


def cache_api_response(endpoint: str, params: Dict[str, Any], response: Any, ttl: int = 300) -> None:
    """Cache API response data."""
    cache_key = f"api_response:{endpoint}:{get_cache_key(params)}"
    set_cache(cache_key, response, ttl)


def get_cached_api_response(endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
    """Get cached API response data."""
    cache_key = f"api_response:{endpoint}:{get_cache_key(params)}"
    return get_from_cache(cache_key)


def warm_cache() -> None:
    """Warm up cache with frequently accessed data."""
    print("🔥 Warming up cache...")
    
    # Cache health data
    cache_health_data()
    
    # Cache log schema
    cache_log_schema()
    
    # Cache database config
    cache_database_connection_info()
    
    print(f"✅ Cache warmed up. Stats: {get_cache_stats()}")


def cache_cleanup_job() -> None:
    """Background job to clean up expired cache entries."""
    cleanup_cache()
    print(f"🧹 Cache cleanup completed. Stats: {get_cache_stats()}")


# Cache configuration for different data types
CACHE_CONFIGS = {
    "health_check": {"ttl": 30, "max_size": 10},
    "log_schema": {"ttl": 3600, "max_size": 5},
    "database_config": {"ttl": 300, "max_size": 10},
    "log_search": {"ttl": 60, "max_size": 100},
    "user_auth": {"ttl": 1800, "max_size": 200},
    "api_response": {"ttl": 300, "max_size": 500}
}


def get_cache_config(data_type: str) -> Dict[str, int]:
    """Get cache configuration for specific data type."""
    return CACHE_CONFIGS.get(data_type, {
        "ttl": _cache_config["default_ttl"],
        "max_size": 100
    })


def adaptive_cache_ttl(data_type: str, access_frequency: int) -> int:
    """Calculate adaptive TTL based on access frequency."""
    base_config = get_cache_config(data_type)
    base_ttl = base_config["ttl"]
    
    # Increase TTL for frequently accessed data
    if access_frequency > 10:
        return min(base_ttl * 2, 3600)  # Max 1 hour
    elif access_frequency > 5:
        return min(base_ttl * 1.5, 1800)  # Max 30 minutes
    else:
        return base_ttl
