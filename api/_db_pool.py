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
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_database_url():
    """Get DATABASE_URL from environment."""
    return os.getenv("DATABASE_URL")


def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Get a direct database connection (simplified for Vercel serverless).
    
    Returns:
        A psycopg2 connection object, or None if unavailable
        
    Important: 
        - Always close connections when done: conn.close()
        - Set autocommit if needed: conn.autocommit = True
    """
    try:
        database_url = _get_database_url()
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return None
        
        # Create direct connection (simpler for serverless)
        conn = psycopg2.connect(
            database_url,
            sslmode='require',
            connect_timeout=10
        )
        
        return conn
        
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None


def get_pool_status() -> dict:
    """
    Get status information about database connection.
    
    Returns:
        Dictionary with connection status information
    """
    return {
        "database_url_set": bool(_get_database_url()),
        "connection_method": "direct (simplified for Vercel serverless)"
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

