"""
Query optimization utilities for the Engineering Log Intelligence System.
Optimizes database and Elasticsearch queries for better performance.
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import structlog

logger = structlog.get_logger(__name__)


class QueryOptimizer:
    """Optimizes queries for better performance."""
    
    def __init__(self):
        """Initialize the query optimizer."""
        self.query_cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
        self.max_cache_size = 1000
        logger.info("Query optimizer initialized")
    
    def optimize_database_query(self, query: str, params: Tuple, query_type: str = "select") -> Dict[str, Any]:
        """
        Optimize database queries for better performance.
        
        Args:
            query: SQL query string
            params: Query parameters
            query_type: Type of query (select, insert, update, delete)
        
        Returns:
            Optimized query information
        """
        try:
            start_time = time.time()
            
            # Basic query analysis
            query_lower = query.lower().strip()
            
            # Check for common performance issues
            issues = []
            optimizations = []
            
            # Check for missing LIMIT clause
            if query_type == "select" and "limit" not in query_lower:
                issues.append("Missing LIMIT clause")
                optimizations.append("Add LIMIT clause to prevent large result sets")
            
            # Check for SELECT * usage
            if "select *" in query_lower:
                issues.append("Using SELECT *")
                optimizations.append("Specify specific columns instead of SELECT *")
            
            # Check for missing WHERE clause on large tables
            if query_type == "select" and "where" not in query_lower and "log_entries" in query_lower:
                issues.append("Missing WHERE clause on log_entries table")
                optimizations.append("Add WHERE clause to filter log_entries table")
            
            # Check for missing indexes
            if "order by" in query_lower and "timestamp" in query_lower:
                optimizations.append("Ensure timestamp column has an index for ORDER BY")
            
            # Check for complex JOINs
            join_count = query_lower.count("join")
            if join_count > 3:
                issues.append(f"Complex query with {join_count} JOINs")
                optimizations.append("Consider breaking down complex JOINs or using views")
            
            # Generate optimized query suggestions
            optimized_query = self._apply_query_optimizations(query, query_type)
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(issues, optimizations)
            
            end_time = time.time()
            analysis_time = end_time - start_time
            
            result = {
                "original_query": query,
                "optimized_query": optimized_query,
                "issues": issues,
                "optimizations": optimizations,
                "optimization_score": optimization_score,
                "analysis_time_ms": analysis_time * 1000,
                "query_type": query_type
            }
            
            logger.info(
                "Database query optimized",
                query_type=query_type,
                issues_count=len(issues),
                optimizations_count=len(optimizations),
                optimization_score=optimization_score,
                analysis_time_ms=analysis_time * 1000
            )
            
            return result
            
        except Exception as e:
            logger.error("Database query optimization failed", error=str(e))
            return {
                "original_query": query,
                "optimized_query": query,
                "issues": ["Optimization failed"],
                "optimizations": [],
                "optimization_score": 0,
                "analysis_time_ms": 0,
                "query_type": query_type,
                "error": str(e)
            }
    
    def optimize_elasticsearch_query(self, query: Dict[str, Any], query_type: str = "search") -> Dict[str, Any]:
        """
        Optimize Elasticsearch queries for better performance.
        
        Args:
            query: Elasticsearch query dictionary
            query_type: Type of query (search, aggregation, etc.)
        
        Returns:
            Optimized query information
        """
        try:
            start_time = time.time()
            
            # Analyze query structure
            issues = []
            optimizations = []
            
            # Check for missing size parameter
            if "size" not in query:
                issues.append("Missing size parameter")
                optimizations.append("Add size parameter to limit results")
            elif query.get("size", 0) > 10000:
                issues.append("Size parameter too large")
                optimizations.append("Consider using scroll API for large result sets")
            
            # Check for missing from parameter
            if "from" not in query and query.get("size", 0) > 1000:
                issues.append("Missing from parameter for pagination")
                optimizations.append("Add from parameter for proper pagination")
            
            # Check for complex aggregations
            if "aggs" in query:
                agg_count = len(query["aggs"])
                if agg_count > 5:
                    issues.append(f"Complex aggregation with {agg_count} aggregations")
                    optimizations.append("Consider breaking down complex aggregations")
            
            # Check for missing filters
            if "query" in query and "bool" in query["query"]:
                bool_query = query["query"]["bool"]
                if "filter" not in bool_query and "must" in bool_query:
                    optimizations.append("Consider using filter instead of must for better performance")
            
            # Check for missing sort
            if "sort" not in query and query_type == "search":
                optimizations.append("Add sort parameter for consistent result ordering")
            
            # Generate optimized query
            optimized_query = self._apply_elasticsearch_optimizations(query, query_type)
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(issues, optimizations)
            
            end_time = time.time()
            analysis_time = end_time - start_time
            
            result = {
                "original_query": query,
                "optimized_query": optimized_query,
                "issues": issues,
                "optimizations": optimizations,
                "optimization_score": optimization_score,
                "analysis_time_ms": analysis_time * 1000,
                "query_type": query_type
            }
            
            logger.info(
                "Elasticsearch query optimized",
                query_type=query_type,
                issues_count=len(issues),
                optimizations_count=len(optimizations),
                optimization_score=optimization_score,
                analysis_time_ms=analysis_time * 1000
            )
            
            return result
            
        except Exception as e:
            logger.error("Elasticsearch query optimization failed", error=str(e))
            return {
                "original_query": query,
                "optimized_query": query,
                "issues": ["Optimization failed"],
                "optimizations": [],
                "optimization_score": 0,
                "analysis_time_ms": 0,
                "query_type": query_type,
                "error": str(e)
            }
    
    def _apply_query_optimizations(self, query: str, query_type: str) -> str:
        """Apply optimizations to database query."""
        optimized = query
        
        # Add LIMIT if missing and it's a SELECT query
        if query_type == "select" and "limit" not in optimized.lower():
            # Add a reasonable default limit
            optimized += " LIMIT 1000"
        
        # Replace SELECT * with specific columns for log_entries
        if "select * from log_entries" in optimized.lower():
            optimized = optimized.replace(
                "SELECT * FROM log_entries",
                "SELECT log_id, timestamp, level, message, source_type, host, service"
            )
        
        return optimized
    
    def _apply_elasticsearch_optimizations(self, query: Dict[str, Any], query_type: str) -> Dict[str, Any]:
        """Apply optimizations to Elasticsearch query."""
        optimized = query.copy()
        
        # Add size if missing
        if "size" not in optimized:
            optimized["size"] = 100
        
        # Add from if missing and size is large
        if "from" not in optimized and optimized.get("size", 0) > 1000:
            optimized["from"] = 0
        
        # Add sort if missing
        if "sort" not in optimized and query_type == "search":
            optimized["sort"] = [{"timestamp": {"order": "desc"}}]
        
        # Optimize bool queries
        if "query" in optimized and "bool" in optimized["query"]:
            bool_query = optimized["query"]["bool"]
            
            # Move must clauses to filter if they don't affect scoring
            if "must" in bool_query and "filter" not in bool_query:
                bool_query["filter"] = bool_query["must"]
                del bool_query["must"]
        
        return optimized
    
    def _calculate_optimization_score(self, issues: List[str], optimizations: List[str]) -> float:
        """Calculate optimization score based on issues and optimizations."""
        if not issues and not optimizations:
            return 100.0  # Perfect score
        
        # Base score
        base_score = 100.0
        
        # Deduct points for issues
        issue_penalty = len(issues) * 10
        
        # Add points for optimizations
        optimization_bonus = len(optimizations) * 5
        
        # Calculate final score
        final_score = max(0, min(100, base_score - issue_penalty + optimization_bonus))
        
        return final_score
    
    def get_query_cache_key(self, query: str, params: Tuple) -> str:
        """Generate cache key for query."""
        import hashlib
        query_str = f"{query}:{str(params)}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def cache_query_result(self, cache_key: str, result: Any) -> None:
        """Cache query result."""
        try:
            # Simple cache eviction if size limit reached
            if len(self.query_cache) >= self.max_cache_size:
                # Remove oldest entries
                oldest_keys = list(self.query_cache.keys())[:100]
                for key in oldest_keys:
                    del self.query_cache[key]
            
            self.query_cache[cache_key] = {
                "result": result,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error("Query result caching failed", error=str(e))
    
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached query result."""
        try:
            if cache_key in self.query_cache:
                cached = self.query_cache[cache_key]
                
                # Check if cache entry is still valid
                if time.time() - cached["timestamp"] < self.cache_ttl:
                    return cached["result"]
                else:
                    # Remove expired entry
                    del self.query_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error("Cached result retrieval failed", error=str(e))
            return None
    
    def clear_cache(self) -> None:
        """Clear query cache."""
        try:
            self.query_cache.clear()
            logger.info("Query cache cleared")
        except Exception as e:
            logger.error("Cache clearing failed", error=str(e))
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            current_time = time.time()
            valid_entries = 0
            expired_entries = 0
            
            for cached in self.query_cache.values():
                if current_time - cached["timestamp"] < self.cache_ttl:
                    valid_entries += 1
                else:
                    expired_entries += 1
            
            return {
                "total_entries": len(self.query_cache),
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "cache_ttl": self.cache_ttl,
                "max_size": self.max_cache_size
            }
            
        except Exception as e:
            logger.error("Cache stats retrieval failed", error=str(e))
            return {}


# Global query optimizer instance
query_optimizer = QueryOptimizer()


def optimize_database_query(query: str, params: Tuple, query_type: str = "select") -> Dict[str, Any]:
    """Optimize database query using the global optimizer."""
    return query_optimizer.optimize_database_query(query, params, query_type)


def optimize_elasticsearch_query(query: Dict[str, Any], query_type: str = "search") -> Dict[str, Any]:
    """Optimize Elasticsearch query using the global optimizer."""
    return query_optimizer.optimize_elasticsearch_query(query, query_type)


def get_query_cache_key(query: str, params: Tuple) -> str:
    """Get query cache key using the global optimizer."""
    return query_optimizer.get_query_cache_key(query, params)


def cache_query_result(cache_key: str, result: Any) -> None:
    """Cache query result using the global optimizer."""
    query_optimizer.cache_query_result(cache_key, result)


def get_cached_result(cache_key: str) -> Optional[Any]:
    """Get cached result using the global optimizer."""
    return query_optimizer.get_cached_result(cache_key)
