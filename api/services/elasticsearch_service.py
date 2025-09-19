"""
Elasticsearch service for the Engineering Log Intelligence System.
Handles log indexing, searching, and analytics operations.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
import structlog

from ..models.log_entry import LogEntry
from ..utils.elasticsearch import get_elasticsearch_manager

logger = structlog.get_logger(__name__)


class ElasticsearchService:
    """Service for managing log data in Elasticsearch."""
    
    def __init__(self):
        """Initialize the Elasticsearch service."""
        self.es = get_elasticsearch_manager()
        self.index_name = "logs"
        self._ensure_index_exists()
        logger.info("Elasticsearch service initialized")
    
    def _ensure_index_exists(self):
        """Ensure the logs index exists with proper mapping."""
        mapping = {
            "properties": {
                # Core log fields
                "log_id": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "level": {"type": "keyword"},
                "message": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "source_type": {"type": "keyword"},
                "host": {"type": "keyword"},
                "service": {"type": "keyword"},
                "category": {"type": "keyword"},
                "tags": {"type": "keyword"},
                
                # Raw log data
                "raw_log": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "structured_data": {"type": "object"},
                
                # Correlation fields
                "request_id": {"type": "keyword"},
                "session_id": {"type": "keyword"},
                "correlation_id": {"type": "keyword"},
                "ip_address": {"type": "ip"},
                
                # Application-specific fields
                "application_type": {"type": "keyword"},
                "framework": {"type": "keyword"},
                "http_method": {"type": "keyword"},
                "http_status": {"type": "integer"},
                "endpoint": {"type": "keyword"},
                "response_time_ms": {"type": "float"},
                
                # SAP-specific fields
                "transaction_code": {"type": "keyword"},
                "sap_system": {"type": "keyword"},
                "department": {"type": "keyword"},
                "amount": {"type": "float"},
                "currency": {"type": "keyword"},
                "document_number": {"type": "keyword"},
                
                # SPLUNK-specific fields
                "splunk_source": {"type": "keyword"},
                "splunk_host": {"type": "keyword"},
                
                # Anomaly and error information
                "is_anomaly": {"type": "boolean"},
                "anomaly_type": {"type": "keyword"},
                "error_details": {"type": "object"},
                "performance_metrics": {"type": "object"},
                "business_context": {"type": "object"},
                
                # Metadata
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
        
        self.es.create_index(self.index_name, mapping)
    
    def index_log_entry(self, log_entry: LogEntry) -> str:
        """Index a single log entry."""
        try:
            # Convert log entry to dictionary
            doc = log_entry.to_dict()
            
            # Use log_id as document ID for deduplication
            doc_id = log_entry.log_id
            
            # Index the document
            result = self.es.index_document(doc, doc_id)
            
            logger.info("Log entry indexed", log_id=log_entry.log_id, doc_id=result)
            return result
            
        except Exception as e:
            logger.error("Failed to index log entry", error=str(e), log_id=log_entry.log_id)
            raise
    
    def bulk_index_log_entries(self, log_entries: List[LogEntry]) -> Tuple[int, int]:
        """Bulk index multiple log entries."""
        try:
            if not log_entries:
                return 0, 0
            
            # Convert log entries to documents
            documents = []
            for log_entry in log_entries:
                doc = log_entry.to_dict()
                doc["id"] = log_entry.log_id  # Use log_id as document ID
                documents.append(doc)
            
            # Bulk index
            success = self.es.bulk_index(documents)
            
            if success:
                logger.info("Bulk index successful", count=len(log_entries))
                return len(log_entries), 0
            else:
                logger.warning("Bulk index had failures", count=len(log_entries))
                return len(log_entries) - 1, 1  # Estimate
                
        except Exception as e:
            logger.error("Failed to bulk index log entries", error=str(e))
            raise
    
    def search_logs(
        self,
        query_text: Optional[str] = None,
        source_type: Optional[str] = None,
        level: Optional[str] = None,
        host: Optional[str] = None,
        service: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_anomaly: Optional[bool] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_field: str = "timestamp",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Search logs with advanced filtering and sorting."""
        try:
            # Build the Elasticsearch query
            query = self._build_search_query(
                query_text=query_text,
                source_type=source_type,
                level=level,
                host=host,
                service=service,
                start_time=start_time,
                end_time=end_time,
                is_anomaly=is_anomaly,
                request_id=request_id,
                session_id=session_id,
                correlation_id=correlation_id,
                ip_address=ip_address,
                limit=limit,
                offset=offset,
                sort_field=sort_field,
                sort_order=sort_order
            )
            
            # Execute search
            result = self.es.search_documents(query, size=limit, from_=offset)
            
            # Convert hits to LogEntry objects
            log_entries = []
            for hit in result["hits"]:
                try:
                    log_entry = LogEntry.from_dict(hit["_source"])
                    log_entries.append(log_entry)
                except Exception as e:
                    logger.warning("Failed to convert hit to LogEntry", error=str(e), hit_id=hit["_id"])
            
            return {
                "logs": log_entries,
                "total_count": result["total"],
                "max_score": result["max_score"],
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error("Failed to search logs", error=str(e))
            raise
    
    def _build_search_query(
        self,
        query_text: Optional[str] = None,
        source_type: Optional[str] = None,
        level: Optional[str] = None,
        host: Optional[str] = None,
        service: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_anomaly: Optional[bool] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_field: str = "timestamp",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Build Elasticsearch query from search parameters."""
        
        # Base query structure
        query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [
                {sort_field: {"order": sort_order}}
            ]
        }
        
        # Text search
        if query_text:
            query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query_text,
                    "fields": ["message^2", "raw_log", "structured_data.*"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        # Exact field filters
        filters = []
        
        if source_type:
            filters.append({"term": {"source_type": source_type}})
        
        if level:
            filters.append({"term": {"level": level}})
        
        if host:
            filters.append({"term": {"host": host}})
        
        if service:
            filters.append({"term": {"service": service}})
        
        if is_anomaly is not None:
            filters.append({"term": {"is_anomaly": is_anomaly}})
        
        if request_id:
            filters.append({"term": {"request_id": request_id}})
        
        if session_id:
            filters.append({"term": {"session_id": session_id}})
        
        if correlation_id:
            filters.append({"term": {"correlation_id": correlation_id}})
        
        if ip_address:
            filters.append({"term": {"ip_address": ip_address}})
        
        # Time range filter
        if start_time or end_time:
            time_filter = {"range": {"timestamp": {}}}
            if start_time:
                time_filter["range"]["timestamp"]["gte"] = start_time.isoformat()
            if end_time:
                time_filter["range"]["timestamp"]["lte"] = end_time.isoformat()
            filters.append(time_filter)
        
        # Add filters to query
        if filters:
            query["query"]["bool"]["filter"] = filters
        
        # If no must clauses, use match_all
        if not query["query"]["bool"]["must"]:
            query["query"]["bool"]["must"] = [{"match_all": {}}]
        
        return query
    
    def get_log_by_id(self, log_id: str) -> Optional[LogEntry]:
        """Get a log entry by log_id."""
        try:
            doc = self.es.get_document(log_id)
            if doc:
                return LogEntry.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error("Failed to get log by ID", error=str(e), log_id=log_id)
            raise
    
    def get_correlation_logs(
        self,
        correlation_key: str,
        correlation_value: str,
        limit: int = 100
    ) -> List[LogEntry]:
        """Get logs by correlation key and value."""
        try:
            # Build correlation query
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"request_id": correlation_value}},
                            {"term": {"session_id": correlation_value}},
                            {"term": {"correlation_id": correlation_value}},
                            {"term": {"ip_address": correlation_value}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                "sort": [{"timestamp": {"order": "desc"}}]
            }
            
            result = self.es.search_documents(query, size=limit)
            
            log_entries = []
            for hit in result["hits"]:
                try:
                    log_entry = LogEntry.from_dict(hit["_source"])
                    log_entries.append(log_entry)
                except Exception as e:
                    logger.warning("Failed to convert correlation hit to LogEntry", error=str(e))
            
            return log_entries
            
        except Exception as e:
            logger.error("Failed to get correlation logs", error=str(e))
            raise
    
    def get_log_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get log statistics and aggregations."""
        try:
            if not start_time:
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            if not end_time:
                end_time = datetime.now(timezone.utc)
            
            # Build aggregation query
            query = {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": start_time.isoformat(),
                                        "lte": end_time.isoformat()
                                    }
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "total_logs": {"value_count": {"field": "log_id"}},
                    "logs_by_level": {
                        "terms": {"field": "level", "size": 10}
                    },
                    "logs_by_source": {
                        "terms": {"field": "source_type", "size": 10}
                    },
                    "logs_by_host": {
                        "terms": {"field": "host", "size": 10}
                    },
                    "anomaly_count": {
                        "filter": {"term": {"is_anomaly": True}},
                        "aggs": {
                            "count": {"value_count": {"field": "log_id"}}
                        }
                    },
                    "error_count": {
                        "filter": {
                            "bool": {
                                "should": [
                                    {"terms": {"level": ["ERROR", "FATAL"]}},
                                    {"range": {"http_status": {"gte": 400}}}
                                ]
                            }
                        },
                        "aggs": {
                            "count": {"value_count": {"field": "log_id"}}
                        }
                    },
                    "avg_response_time": {
                        "avg": {"field": "response_time_ms"}
                    },
                    "top_endpoints": {
                        "terms": {"field": "endpoint", "size": 10}
                    }
                },
                "size": 0
            }
            
            result = self.es.search_documents(query)
            aggs = result.get("aggregations", {})
            
            # Process aggregations
            total_logs = aggs.get("total_logs", {}).get("value", 0)
            anomaly_count = aggs.get("anomaly_count", {}).get("count", {}).get("value", 0)
            error_count = aggs.get("error_count", {}).get("count", {}).get("value", 0)
            avg_response_time = aggs.get("avg_response_time", {}).get("value", 0)
            
            statistics = {
                "total_logs": total_logs,
                "logs_by_level": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs.get("logs_by_level", {}).get("buckets", [])
                },
                "logs_by_source": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs.get("logs_by_source", {}).get("buckets", [])
                },
                "logs_by_host": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs.get("logs_by_host", {}).get("buckets", [])
                },
                "anomaly_count": anomaly_count,
                "error_count": error_count,
                "anomaly_rate": (anomaly_count / total_logs * 100) if total_logs > 0 else 0,
                "error_rate": (error_count / total_logs * 100) if total_logs > 0 else 0,
                "avg_response_time_ms": avg_response_time,
                "top_endpoints": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs.get("top_endpoints", {}).get("buckets", [])
                },
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
            logger.info("Log statistics retrieved", statistics=statistics)
            return statistics
            
        except Exception as e:
            logger.error("Failed to get log statistics", error=str(e))
            raise
    
    def delete_log(self, log_id: str) -> bool:
        """Delete a log entry by log_id."""
        try:
            success = self.es.delete_document(log_id)
            if success:
                logger.info("Log entry deleted", log_id=log_id)
            return success
            
        except Exception as e:
            logger.error("Failed to delete log entry", error=str(e), log_id=log_id)
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check Elasticsearch service health."""
        try:
            es_health = self.es.health_check()
            
            return {
                "service": "elasticsearch",
                "status": es_health.get("status", "unknown"),
                "cluster_status": es_health.get("cluster_status", "unknown"),
                "index_name": self.index_name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error("Elasticsearch health check failed", error=str(e))
            return {
                "service": "elasticsearch",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
