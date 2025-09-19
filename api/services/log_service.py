"""
Log service for the Engineering Log Intelligence System.
Handles log entry operations and queries.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
import structlog

from ..models.log_entry import LogEntry
from ..utils.database import get_database_manager

logger = structlog.get_logger(__name__)


class LogService:
    """Service for managing log entries."""
    
    def __init__(self):
        """Initialize the log service."""
        self.db = get_database_manager()
        logger.info("Log service initialized")
    
    def create_log_entry(self, log_entry: LogEntry) -> LogEntry:
        """Create a new log entry."""
        try:
            # Validate the log entry
            errors = log_entry.validate()
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")
            
            # Generate log ID if not set
            log_entry.generate_log_id()
            
            # Insert into database
            query, params = log_entry.get_database_insert_query()
            log_id = self.db.execute_insert(query, params)
            
            # Set the ID and return
            log_entry.id = log_id
            logger.info("Log entry created", log_id=log_entry.log_id, id=log_id)
            return log_entry
            
        except Exception as e:
            logger.error("Failed to create log entry", error=str(e), log_id=log_entry.log_id)
            raise
    
    def get_log_entry(self, log_id: str) -> Optional[LogEntry]:
        """Get a log entry by log_id."""
        try:
            query = "SELECT * FROM log_entries WHERE log_id = %s"
            row = self.db.execute_query(query, (log_id,), fetch="one")
            
            if row:
                log_entry = LogEntry.from_database_row(row)
                logger.info("Log entry retrieved", log_id=log_id)
                return log_entry
            else:
                logger.warning("Log entry not found", log_id=log_id)
                return None
                
        except Exception as e:
            logger.error("Failed to get log entry", error=str(e), log_id=log_id)
            raise
    
    def get_log_entry_by_id(self, entry_id: int) -> Optional[LogEntry]:
        """Get a log entry by database ID."""
        try:
            query = "SELECT * FROM log_entries WHERE id = %s"
            row = self.db.execute_query(query, (entry_id,), fetch="one")
            
            if row:
                log_entry = LogEntry.from_database_row(row)
                logger.info("Log entry retrieved by ID", id=entry_id)
                return log_entry
            else:
                logger.warning("Log entry not found by ID", id=entry_id)
                return None
                
        except Exception as e:
            logger.error("Failed to get log entry by ID", error=str(e), id=entry_id)
            raise
    
    def update_log_entry(self, log_entry: LogEntry) -> LogEntry:
        """Update an existing log entry."""
        try:
            if not log_entry.id:
                raise ValueError("Log entry ID is required for update")
            
            # Update timestamp
            log_entry.updated_at = datetime.now(timezone.utc)
            
            query = """
            UPDATE log_entries SET
                level = %s, message = %s, host = %s, service = %s, category = %s,
                tags = %s, raw_log = %s, structured_data = %s, request_id = %s,
                session_id = %s, correlation_id = %s, ip_address = %s,
                application_type = %s, framework = %s, http_method = %s,
                http_status = %s, endpoint = %s, response_time_ms = %s,
                transaction_code = %s, sap_system = %s, department = %s,
                amount = %s, currency = %s, document_number = %s,
                splunk_source = %s, splunk_host = %s, is_anomaly = %s,
                anomaly_type = %s, error_details = %s, performance_metrics = %s,
                business_context = %s, updated_at = %s
            WHERE id = %s
            """
            
            import json
            params = (
                log_entry.level, log_entry.message, log_entry.host, log_entry.service,
                log_entry.category, json.dumps(log_entry.tags), log_entry.raw_log,
                json.dumps(log_entry.structured_data), log_entry.request_id,
                log_entry.session_id, log_entry.correlation_id, log_entry.ip_address,
                log_entry.application_type, log_entry.framework, log_entry.http_method,
                log_entry.http_status, log_entry.endpoint, log_entry.response_time_ms,
                log_entry.transaction_code, log_entry.sap_system, log_entry.department,
                log_entry.amount, log_entry.currency, log_entry.document_number,
                log_entry.splunk_source, log_entry.splunk_host, log_entry.is_anomaly,
                log_entry.anomaly_type, json.dumps(log_entry.error_details),
                json.dumps(log_entry.performance_metrics), json.dumps(log_entry.business_context),
                log_entry.updated_at, log_entry.id
            )
            
            rows_affected = self.db.execute_update(query, params)
            
            if rows_affected > 0:
                logger.info("Log entry updated", id=log_entry.id, log_id=log_entry.log_id)
                return log_entry
            else:
                logger.warning("Log entry not found for update", id=log_entry.id)
                return None
                
        except Exception as e:
            logger.error("Failed to update log entry", error=str(e), id=log_entry.id)
            raise
    
    def delete_log_entry(self, log_id: str) -> bool:
        """Delete a log entry by log_id."""
        try:
            query = "DELETE FROM log_entries WHERE log_id = %s"
            rows_affected = self.db.execute_update(query, (log_id,))
            
            if rows_affected > 0:
                logger.info("Log entry deleted", log_id=log_id)
                return True
            else:
                logger.warning("Log entry not found for deletion", log_id=log_id)
                return False
                
        except Exception as e:
            logger.error("Failed to delete log entry", error=str(e), log_id=log_id)
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
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[LogEntry], int]:
        """Search log entries with filters."""
        try:
            # Build the WHERE clause
            where_conditions = []
            params = []
            
            if query_text:
                where_conditions.append("""
                    (to_tsvector('english', message) @@ plainto_tsquery('english', %s) OR
                     to_tsvector('english', raw_log) @@ plainto_tsquery('english', %s))
                """)
                params.extend([query_text, query_text])
            
            if source_type:
                where_conditions.append("source_type = %s")
                params.append(source_type)
            
            if level:
                where_conditions.append("level = %s")
                params.append(level)
            
            if host:
                where_conditions.append("host = %s")
                params.append(host)
            
            if service:
                where_conditions.append("service = %s")
                params.append(service)
            
            if start_time:
                where_conditions.append("timestamp >= %s")
                params.append(start_time)
            
            if end_time:
                where_conditions.append("timestamp <= %s")
                params.append(end_time)
            
            if is_anomaly is not None:
                where_conditions.append("is_anomaly = %s")
                params.append(is_anomaly)
            
            # Build the query
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Count query
            count_query = f"SELECT COUNT(*) FROM log_entries WHERE {where_clause}"
            total_count = self.db.execute_query(count_query, params, fetch="one")[0]
            
            # Data query
            data_query = f"""
                SELECT * FROM log_entries 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            rows = self.db.execute_query(data_query, params)
            log_entries = [LogEntry.from_database_row(row) for row in rows]
            
            logger.info(
                "Log search completed",
                query_text=query_text,
                source_type=source_type,
                level=level,
                results_count=len(log_entries),
                total_count=total_count
            )
            
            return log_entries, total_count
            
        except Exception as e:
            logger.error("Failed to search logs", error=str(e))
            raise
    
    def get_logs_by_correlation(
        self,
        correlation_key: str,
        correlation_value: str,
        limit: int = 100
    ) -> List[LogEntry]:
        """Get logs by correlation key and value."""
        try:
            query = f"SELECT * FROM get_logs_by_correlation(%s, %s) LIMIT %s"
            rows = self.db.execute_query(query, (correlation_key, correlation_value, limit))
            log_entries = [LogEntry.from_database_row(row) for row in rows]
            
            logger.info(
                "Correlation search completed",
                correlation_key=correlation_key,
                correlation_value=correlation_value,
                results_count=len(log_entries)
            )
            
            return log_entries
            
        except Exception as e:
            logger.error("Failed to get logs by correlation", error=str(e))
            raise
    
    def get_recent_high_priority_logs(self, hours: int = 24, limit: int = 100) -> List[LogEntry]:
        """Get recent high-priority logs."""
        try:
            query = """
                SELECT * FROM recent_high_priority_logs
                WHERE timestamp >= NOW() - INTERVAL '%s hours'
                LIMIT %s
            """
            rows = self.db.execute_query(query, (hours, limit))
            log_entries = [LogEntry.from_database_row(row) for row in rows]
            
            logger.info(
                "High priority logs retrieved",
                hours=hours,
                results_count=len(log_entries)
            )
            
            return log_entries
            
        except Exception as e:
            logger.error("Failed to get high priority logs", error=str(e))
            raise
    
    def get_log_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get log statistics for a time period."""
        try:
            if not start_time:
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            if not end_time:
                end_time = datetime.now(timezone.utc)
            
            # Total logs
            total_query = """
                SELECT COUNT(*) as total_logs
                FROM log_entries
                WHERE timestamp BETWEEN %s AND %s
            """
            total_result = self.db.execute_query(total_query, (start_time, end_time), fetch="one")
            total_logs = total_result[0] if total_result else 0
            
            # Logs by level
            level_query = """
                SELECT level, COUNT(*) as count
                FROM log_entries
                WHERE timestamp BETWEEN %s AND %s
                GROUP BY level
                ORDER BY count DESC
            """
            level_rows = self.db.execute_query(level_query, (start_time, end_time))
            logs_by_level = {row['level']: row['count'] for row in level_rows}
            
            # Logs by source type
            source_query = """
                SELECT source_type, COUNT(*) as count
                FROM log_entries
                WHERE timestamp BETWEEN %s AND %s
                GROUP BY source_type
                ORDER BY count DESC
            """
            source_rows = self.db.execute_query(source_query, (start_time, end_time))
            logs_by_source = {row['source_type']: row['count'] for row in source_rows}
            
            # Anomaly count
            anomaly_query = """
                SELECT COUNT(*) as anomaly_count
                FROM log_entries
                WHERE timestamp BETWEEN %s AND %s AND is_anomaly = TRUE
            """
            anomaly_result = self.db.execute_query(anomaly_query, (start_time, end_time), fetch="one")
            anomaly_count = anomaly_result[0] if anomaly_result else 0
            
            # Error count
            error_query = """
                SELECT COUNT(*) as error_count
                FROM log_entries
                WHERE timestamp BETWEEN %s AND %s 
                AND (level IN ('ERROR', 'FATAL') OR http_status >= 400)
            """
            error_result = self.db.execute_query(error_query, (start_time, end_time), fetch="one")
            error_count = error_result[0] if error_result else 0
            
            statistics = {
                'total_logs': total_logs,
                'logs_by_level': logs_by_level,
                'logs_by_source': logs_by_source,
                'anomaly_count': anomaly_count,
                'error_count': error_count,
                'anomaly_rate': (anomaly_count / total_logs * 100) if total_logs > 0 else 0,
                'error_rate': (error_count / total_logs * 100) if total_logs > 0 else 0,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
            logger.info("Log statistics retrieved", statistics=statistics)
            return statistics
            
        except Exception as e:
            logger.error("Failed to get log statistics", error=str(e))
            raise
    
    def bulk_insert_logs(self, log_entries: List[LogEntry]) -> int:
        """Bulk insert multiple log entries."""
        try:
            if not log_entries:
                return 0
            
            # Prepare bulk insert query
            query = """
                INSERT INTO log_entries (
                    log_id, timestamp, level, message, source_type, host, service, category,
                    tags, raw_log, structured_data, request_id, session_id, correlation_id,
                    ip_address, application_type, framework, http_method, http_status,
                    endpoint, response_time_ms, transaction_code, sap_system, department,
                    amount, currency, document_number, splunk_source, splunk_host,
                    is_anomaly, anomaly_type, error_details, performance_metrics,
                    business_context, created_at, updated_at
                ) VALUES %s
            """
            
            import json
            values = []
            for log_entry in log_entries:
                # Generate log ID if not set
                log_entry.generate_log_id()
                
                values.append((
                    log_entry.log_id, log_entry.timestamp, log_entry.level, log_entry.message,
                    log_entry.source_type, log_entry.host, log_entry.service, log_entry.category,
                    json.dumps(log_entry.tags), log_entry.raw_log, json.dumps(log_entry.structured_data),
                    log_entry.request_id, log_entry.session_id, log_entry.correlation_id,
                    log_entry.ip_address, log_entry.application_type, log_entry.framework,
                    log_entry.http_method, log_entry.http_status, log_entry.endpoint,
                    log_entry.response_time_ms, log_entry.transaction_code, log_entry.sap_system,
                    log_entry.department, log_entry.amount, log_entry.currency,
                    log_entry.document_number, log_entry.splunk_source, log_entry.splunk_host,
                    log_entry.is_anomaly, log_entry.anomaly_type, json.dumps(log_entry.error_details),
                    json.dumps(log_entry.performance_metrics), json.dumps(log_entry.business_context),
                    log_entry.created_at, log_entry.updated_at
                ))
            
            # Execute bulk insert
            from psycopg2.extras import execute_values
            with self.db.get_cursor() as cursor:
                execute_values(cursor, query, values)
                cursor.connection.commit()
                rows_inserted = cursor.rowcount
            
            logger.info("Bulk log insert completed", rows_inserted=rows_inserted)
            return rows_inserted
            
        except Exception as e:
            logger.error("Failed to bulk insert logs", error=str(e))
            raise
