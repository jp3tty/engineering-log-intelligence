"""
Shared Database Connection Pool for Vercel Serverless Functions
================================================================

This module provides a singleton connection pool that all API endpoints share.
This dramatically reduces the number of database connections from potentially
hundreds down to just 2-3 connections total.

Key Features:
- Global connection pool shared across all serverless functions
- Automatic connection reuse within Vercel container lifecycle
- Reduced Railway database connection count
- Thread-safe connection management

Usage in API endpoints:
    from api._db_pool import get_db_connection
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM log_entries LIMIT 10")
        results = cursor.fetchall()
        cursor.close()

Author: Engineering Log Intelligence Team
Date: October 15, 2025
"""

import os
import psycopg2
from psycopg2 import pool
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool - persists across function invocations in same container
_connection_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None
_pool_initialized = False


def _initialize_pool():
    """
    Initialize the global connection pool.
    This is called automatically on first use.
    
    Uses SimpleConnectionPool with just 1-2 connections to minimize
    Railway database connection count.
    """
    global _connection_pool, _pool_initialized
    
    if _pool_initialized:
        return
    
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            _pool_initialized = True  # Don't keep trying
            return
        
        # Create a small pool: min=1, max=2
        # This ensures we use at most 2 connections per serverless container
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=2,
            dsn=database_url,
            sslmode='require',
            connect_timeout=5,
            # Additional settings to prevent connection leaks
            options='-c statement_timeout=30000'  # 30 second query timeout
        )
        
        _pool_initialized = True
        logger.info("✅ Database connection pool initialized (1-2 connections)")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database connection pool: {e}")
        _pool_initialized = True  # Don't keep trying
        _connection_pool = None


def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Get a database connection from the shared pool.
    
    Returns:
        A psycopg2 connection object, or None if unavailable
        
    Important: 
        - Connections are automatically returned to the pool when closed
        - Always close connections when done: conn.close()
        - Set autocommit if needed: conn.autocommit = True
    """
    global _connection_pool, _pool_initialized
    
    # Initialize pool on first use
    if not _pool_initialized:
        _initialize_pool()
    
    # Check if pool exists
    if _connection_pool is None:
        logger.warning("Database connection pool not available")
        return None
    
    try:
        # Get connection from pool
        conn = _connection_pool.getconn()
        
        # Test if connection is alive
        if conn.closed:
            logger.warning("Got closed connection from pool, getting new one")
            _connection_pool.putconn(conn, close=True)
            conn = _connection_pool.getconn()
        
        return conn
        
    except Exception as e:
        logger.error(f"Failed to get connection from pool: {e}")
        return None


def return_db_connection(conn: psycopg2.extensions.connection):
    """
    Return a connection to the pool.
    
    Note: You can also just call conn.close() which will return it to the pool.
    This function is provided for explicit control.
    
    Args:
        conn: The connection to return to the pool
    """
    global _connection_pool
    
    if _connection_pool and conn:
        try:
            _connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {e}")


def close_all_connections():
    """
    Close all connections in the pool.
    
    Note: This is rarely needed in serverless functions as Vercel
    manages the container lifecycle. Only use for testing or cleanup.
    """
    global _connection_pool, _pool_initialized
    
    if _connection_pool:
        try:
            _connection_pool.closeall()
            logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
    
    _connection_pool = None
    _pool_initialized = False


def get_pool_status() -> dict:
    """
    Get status information about the connection pool.
    
    Returns:
        Dictionary with pool status information
    """
    global _connection_pool, _pool_initialized
    
    return {
        "pool_initialized": _pool_initialized,
        "pool_exists": _connection_pool is not None,
        "database_url_set": bool(os.getenv("DATABASE_URL")),
    }


# Convenience function for getting connection with error handling
def get_db_connection_safe() -> tuple[Optional[psycopg2.extensions.connection], Optional[str]]:
    """
    Get a database connection with error information.
    
    Returns:
        Tuple of (connection, error_message)
        - If successful: (connection_object, None)
        - If failed: (None, "error message")
    """
    try:
        conn = get_db_connection()
        if conn:
            return conn, None
        else:
            return None, "Database connection pool not available"
    except Exception as e:
        return None, str(e)

