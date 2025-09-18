"""
Database connection utilities for the Engineering Log Intelligence System.
Handles PostgreSQL connections with connection pooling and error handling.
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)


class DatabaseManager:
    """Manages PostgreSQL database connections with pooling."""

    def __init__(self):
        self.connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the database connection pool."""
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL environment variable not set")

            # Parse database URL
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1, maxconn=10, dsn=database_url
            )
            logger.info("Database connection pool initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize database connection pool", error=str(e))
            raise

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        connection = None
        try:
            if not self.connection_pool:
                raise RuntimeError("Database connection pool not initialized")

            connection = self.connection_pool.getconn()
            yield connection

        except Exception as e:
            logger.error("Database connection error", error=str(e))
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)

    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """Get a database cursor with optional dictionary cursor."""
        with self.get_connection() as connection:
            cursor_class = RealDictCursor if dict_cursor else None
            cursor = connection.cursor(cursor_factory=cursor_class)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute_query(
        self, query: str, params: tuple = None, fetch: str = "all"
    ) -> Any:
        """Execute a database query and return results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)

            if fetch == "all":
                return cursor.fetchall()
            elif fetch == "one":
                return cursor.fetchone()
            elif fetch == "many":
                return cursor.fetchmany()
            else:
                return None

    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT query and return the inserted ID."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            cursor.connection.commit()
            return cursor.fetchone()[0] if cursor.description else None

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an UPDATE/DELETE query and return affected rows count."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            cursor.connection.commit()
            return cursor.rowcount

    def health_check(self) -> Dict[str, Any]:
        """Check database health and return status information."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT version(), current_database(), current_user")
                result = cursor.fetchone()

                return {
                    "status": "healthy",
                    "database": result[1],
                    "user": result[2],
                    "version": result[0][:50] + "..."
                    if len(result[0]) > 50
                    else result[0],
                }
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}

    def close_pool(self):
        """Close the database connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager


# Convenience functions for common operations
def execute_query(query: str, params: tuple = None, fetch: str = "all") -> Any:
    """Execute a database query using the global database manager."""
    return db_manager.execute_query(query, params, fetch)


def execute_insert(query: str, params: tuple = None) -> int:
    """Execute an INSERT query using the global database manager."""
    return db_manager.execute_insert(query, params)


def execute_update(query: str, params: tuple = None) -> int:
    """Execute an UPDATE/DELETE query using the global database manager."""
    return db_manager.execute_update(query, params)


def health_check() -> Dict[str, Any]:
    """Check database health using the global database manager."""
    return db_manager.health_check()
