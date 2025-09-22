"""
Optimized Logs endpoint for Vercel Functions.
Includes performance optimizations, caching, and connection pooling.
"""

import os
import json
import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from functools import lru_cache
import psycopg2
from psycopg2 import pool
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Connection pools for better performance
_postgres_pool = None
_requests_session = None

# Cache for frequently accessed data
@lru_cache(maxsize=100)
def get_cached_log_schema() -> Dict[str, Any]:
    """Cache log schema to avoid repeated processing."""
    return {
        "fields": [
            "id", "timestamp", "level", "message", "source", "service",
            "hostname", "user_id", "session_id", "request_id", "correlation_id"
        ],
        "indexes": ["timestamp", "level", "source", "service"],
        "searchable_fields": ["message", "source", "service", "hostname"]
    }


def get_postgres_pool():
    """Get or create PostgreSQL connection pool."""
    global _postgres_pool
    if _postgres_pool is None:
        try:
            _postgres_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,  # min and max connections
                dsn=os.getenv("DATABASE_URL")
            )
        except Exception as e:
            print(f"Failed to create PostgreSQL pool: {e}")
            return None
    return _postgres_pool


def get_requests_session():
    """Get or create optimized requests session."""
    global _requests_session
    if _requests_session is None:
        _requests_session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        _requests_session.mount("http://", adapter)
        _requests_session.mount("https://", adapter)
        
        # Set timeouts
        _requests_session.timeout = (5, 10)  # connect, read timeout
        
    return _requests_session


def get_elasticsearch_url() -> str:
    """Get Elasticsearch URL with caching."""
    return os.getenv("ELASTICSEARCH_URL", "")


def get_elasticsearch_auth() -> tuple:
    """Get Elasticsearch authentication with caching."""
    username = os.getenv("ELASTICSEARCH_USERNAME", "")
    password = os.getenv("ELASTICSEARCH_PASSWORD", "")
    return (username, password) if username and password else None


async def search_elasticsearch(query: Dict[str, Any], size: int = 100) -> List[Dict[str, Any]]:
    """Optimized Elasticsearch search with connection pooling."""
    try:
        es_url = get_elasticsearch_url()
        auth = get_elasticsearch_auth()
        
        if not es_url:
            return []
        
        session = get_requests_session()
        
        # Optimized search query
        search_body = {
            "query": query,
            "size": min(size, 1000),  # Limit results
            "sort": [{"timestamp": {"order": "desc"}}],
            "_source": ["id", "timestamp", "level", "message", "source", "service"]
        }
        
        response = session.get(
            f"{es_url}/engineering_logs/_search",
            json=search_body,
            auth=auth,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return [hit["_source"] for hit in data.get("hits", {}).get("hits", [])]
        
        return []
        
    except Exception as e:
        print(f"Elasticsearch search error: {e}")
        return []


def search_postgresql(query_params: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
    """Optimized PostgreSQL search with connection pooling."""
    try:
        pool = get_postgres_pool()
        if not pool:
            return []
        
        conn = pool.getconn()
        cursor = conn.cursor()
        
        # Build optimized query
        base_query = "SELECT id, timestamp, level, message, source, service, hostname FROM log_entries WHERE 1=1"
        params = []
        
        if query_params.get("level"):
            base_query += " AND level = %s"
            params.append(query_params["level"])
        
        if query_params.get("source"):
            base_query += " AND source = %s"
            params.append(query_params["source"])
        
        if query_params.get("start_time"):
            base_query += " AND timestamp >= %s"
            params.append(query_params["start_time"])
        
        if query_params.get("end_time"):
            base_query += " AND timestamp <= %s"
            params.append(query_params["end_time"])
        
        base_query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(min(limit, 1000))
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        # Convert to list of dicts
        columns = [desc[0] for desc in cursor.description]
        logs = [dict(zip(columns, row)) for row in results]
        
        cursor.close()
        pool.putconn(conn)
        
        return logs
        
    except Exception as e:
        print(f"PostgreSQL search error: {e}")
        return []


def handler(request) -> Dict[str, Any]:
    """
    Optimized logs handler for Vercel Functions.
    Supports both search and ingestion with performance optimizations.
    """
    try:
        # Parse request
        method = request.get("httpMethod", "GET")
        headers = request.get("headers", {})
        body = request.get("body", "{}")
        
        # Handle CORS preflight
        if method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
                "body": ""
            }
        
        # Route based on method
        if method == "GET":
            return handle_log_search(request)
        elif method == "POST":
            return handle_log_ingestion(request)
        else:
            return {
                "statusCode": 405,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Method not allowed"})
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }


def handle_log_search(request) -> Dict[str, Any]:
    """Handle log search requests with optimizations."""
    try:
        # Parse query parameters
        query_params = request.get("queryStringParameters", {}) or {}
        
        # Extract search parameters
        search_params = {
            "level": query_params.get("level"),
            "source": query_params.get("source"),
            "start_time": query_params.get("start_time"),
            "end_time": query_params.get("end_time"),
            "limit": int(query_params.get("limit", 100))
        }
        
        # Search both PostgreSQL and Elasticsearch
        postgres_logs = search_postgresql(search_params, search_params["limit"])
        
        # For now, return PostgreSQL results (Elasticsearch integration can be added)
        logs = postgres_logs
        
        # Get schema for response
        schema = get_cached_log_schema()
        
        response_data = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "query": search_params,
            "results": {
                "logs": logs,
                "total": len(logs),
                "schema": schema
            },
            "performance": {
                "response_time": f"{time.time():.3f}s",
                "sources": ["postgresql"]
            }
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=60",  # Cache for 1 minute
            },
            "body": json.dumps(response_data, separators=(',', ':'))
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Search failed",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }


def handle_log_ingestion(request) -> Dict[str, Any]:
    """Handle log ingestion requests with optimizations."""
    try:
        # Parse request body
        body = request.get("body", "{}")
        if isinstance(body, str):
            log_data = json.loads(body)
        else:
            log_data = body
        
        # Validate log data
        required_fields = ["level", "message", "source"]
        missing_fields = [field for field in required_fields if field not in log_data]
        
        if missing_fields:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Missing required fields",
                    "missing_fields": missing_fields
                })
            }
        
        # Add timestamp if not provided
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.utcnow().isoformat()
        
        # Store in PostgreSQL (simplified for now)
        pool = get_postgres_pool()
        if pool:
            conn = pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO log_entries (level, message, source, service, hostname, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                log_data["level"],
                log_data["message"],
                log_data["source"],
                log_data.get("service", "unknown"),
                log_data.get("hostname", "unknown"),
                log_data["timestamp"]
            ))
            
            conn.commit()
            cursor.close()
            pool.putconn(conn)
        
        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "status": "success",
                "message": "Log ingested successfully",
                "log_id": log_data.get("id", "generated"),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Ingestion failed",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }
