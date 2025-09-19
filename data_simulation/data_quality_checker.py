"""
Data quality checker for log simulation.
Validates generated logs for consistency, completeness, and realism.
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
import structlog

logger = structlog.get_logger(__name__)

class DataQualityChecker:
    """Checks data quality for generated logs."""
    
    def __init__(self):
        """Initialize the data quality checker."""
        self.valid_log_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
        self.valid_http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        self.valid_http_status_codes = list(range(100, 600))
        self.quality_issues = []
        
        logger.info("Data quality checker initialized")
    
    def check_log_quality(self, log: Dict[str, Any]) -> List[str]:
        """
        Check the quality of a single log entry.
        
        Args:
            log: Log entry dictionary
            
        Returns:
            List of quality issues found
        """
        issues = []
        
        # Check required fields
        required_fields = ['log_id', 'timestamp', 'level', 'message']
        for field in required_fields:
            if field not in log:
                issues.append(f"Missing required field '{field}'")
            elif not log[field]:
                issues.append(f"Empty required field '{field}'")
        
        # Check log ID format
        if 'log_id' in log:
            log_id = log['log_id']
            if not isinstance(log_id, str) or len(log_id) < 10:
                issues.append(f"Invalid log_id format: {log_id}")
        
        # Check timestamp format
        if 'timestamp' in log:
            timestamp = log['timestamp']
            if not self._is_valid_timestamp(timestamp):
                issues.append(f"Invalid timestamp format: {timestamp}")
        
        # Check log level
        if 'level' in log:
            level = log['level']
            if level not in self.valid_log_levels:
                issues.append(f"Invalid log level: {level}")
        
        # Check message content
        if 'message' in log:
            message = log['message']
            if not isinstance(message, str) or len(message) < 5:
                issues.append(f"Invalid message content: {message}")
        
        # Check metadata structure
        if 'metadata' in log:
            metadata = log['metadata']
            if not isinstance(metadata, dict):
                issues.append("Metadata must be a dictionary")
            else:
                required_metadata = ['generator', 'version', 'generated_at']
                for field in required_metadata:
                    if field not in metadata:
                        issues.append(f"Missing metadata field '{field}'")
        
        # Check application-specific fields
        if log.get('metadata', {}).get('generator') == 'application':
            issues.extend(self._check_application_log_quality(log))
        elif log.get('metadata', {}).get('generator') == 'splunk':
            issues.extend(self._check_splunk_log_quality(log))
        elif log.get('metadata', {}).get('generator') == 'sap':
            issues.extend(self._check_sap_log_quality(log))
        
        return issues
    
    def _is_valid_timestamp(self, timestamp: str) -> bool:
        """Check if timestamp is in valid ISO format."""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except (ValueError, TypeError):
            return False
    
    def _check_application_log_quality(self, log: Dict[str, Any]) -> List[str]:
        """Check application-specific log quality."""
        issues = []
        
        # Check HTTP fields
        if 'http_method' in log:
            method = log['http_method']
            if method not in self.valid_http_methods:
                issues.append(f"Invalid HTTP method: {method}")
        
        if 'http_status' in log:
            status = log['http_status']
            if not isinstance(status, int) or status not in self.valid_http_status_codes:
                issues.append(f"Invalid HTTP status code: {status}")
        
        # Check response time
        if 'response_time_ms' in log:
            response_time = log['response_time_ms']
            if not isinstance(response_time, (int, float)) or response_time < 0 or response_time > 60000:
                issues.append(f"Invalid response time: {response_time}ms")
        
        # Check endpoint format
        if 'endpoint' in log:
            endpoint = log['endpoint']
            if not endpoint.startswith('/'):
                issues.append(f"Invalid endpoint format: {endpoint}")
        
        # Check IP address format
        if 'ip_address' in log:
            ip_address = log['ip_address']
            if not self._is_valid_ip_address(ip_address):
                issues.append(f"Invalid IP address: {ip_address}")
        
        # Check UUID format for request_id
        if 'request_id' in log:
            request_id = log['request_id']
            if not self._is_valid_uuid(request_id):
                issues.append(f"Invalid request_id format: {request_id}")
        
        return issues
    
    def _check_splunk_log_quality(self, log: Dict[str, Any]) -> List[str]:
        """Check SPLUNK-specific log quality."""
        issues = []
        
        # Check SPLUNK source format
        if 'splunk_source' in log:
            source = log['splunk_source']
            valid_sources = [
                'WinEventLog:Security', 'WinEventLog:System', 'WinEventLog:Application',
                'syslog', 'apache_access', 'apache_error', 'iis_access', 'iis_error'
            ]
            if source not in valid_sources:
                issues.append(f"Invalid SPLUNK source: {source}")
        
        # Check raw log format
        if 'raw_log' in log:
            raw_log = log['raw_log']
            if not isinstance(raw_log, str) or len(raw_log) < 10:
                issues.append(f"Invalid raw log format: {raw_log}")
        
        return issues
    
    def _check_sap_log_quality(self, log: Dict[str, Any]) -> List[str]:
        """Check SAP-specific log quality."""
        issues = []
        
        # Check T-code format
        if 'transaction_code' in log:
            t_code = log['transaction_code']
            if not isinstance(t_code, str) or len(t_code) < 3:
                issues.append(f"Invalid T-code format: {t_code}")
        
        # Check SAP system
        if 'sap_system' in log:
            sap_system = log['sap_system']
            valid_systems = ['ERP_PROD', 'ERP_DEV', 'CRM_PROD', 'CRM_DEV', 'SCM_PROD', 'SCM_DEV', 'HCM_PROD', 'HCM_DEV']
            if sap_system not in valid_systems:
                issues.append(f"Invalid SAP system: {sap_system}")
        
        # Check amount format
        if 'amount' in log:
            amount = log['amount']
            if not isinstance(amount, (int, float)) or amount < 0:
                issues.append(f"Invalid amount: {amount}")
        
        return issues
    
    def _is_valid_ip_address(self, ip: str) -> bool:
        """Check if IP address is valid."""
        if not isinstance(ip, str):
            return False
        
        # Simple IP validation
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            for part in parts:
                num = int(part)
                if not 0 <= num <= 255:
                    return False
            return True
        except ValueError:
            return False
    
    def _is_valid_uuid(self, uuid_str: str) -> bool:
        """Check if string is a valid UUID."""
        if not isinstance(uuid_str, str):
            return False
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, uuid_str, re.IGNORECASE))
    
    def check_batch_quality(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check quality of a batch of logs.
        
        Args:
            logs: List of log entries
            
        Returns:
            Dictionary with quality statistics
        """
        total_logs = len(logs)
        logs_with_issues = 0
        total_issues = 0
        issue_types = {}
        
        for log in logs:
            issues = self.check_log_quality(log)
            if issues:
                logs_with_issues += 1
                total_issues += len(issues)
                
                for issue in issues:
                    issue_type = issue.split(':')[0] if ':' in issue else issue
                    issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        quality_score = ((total_logs - logs_with_issues) / total_logs * 100) if total_logs > 0 else 0
        
        return {
            'total_logs': total_logs,
            'logs_with_issues': logs_with_issues,
            'total_issues': total_issues,
            'quality_score': round(quality_score, 2),
            'issue_types': issue_types,
            'issues_per_log': round(total_issues / total_logs, 2) if total_logs > 0 else 0
        }
    
    def check_correlation_quality(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check correlation quality across different log types.
        
        Args:
            logs: List of log entries from different systems
            
        Returns:
            Dictionary with correlation statistics
        """
        # Group logs by system
        logs_by_system = {}
        for log in logs:
            system = log.get('metadata', {}).get('generator', 'unknown')
            if system not in logs_by_system:
                logs_by_system[system] = []
            logs_by_system[system].append(log)
        
        # Check timestamp correlation
        timestamp_correlations = self._check_timestamp_correlations(logs)
        
        # Check IP correlation
        ip_correlations = self._check_ip_correlations(logs)
        
        # Check request correlation
        request_correlations = self._check_request_correlations(logs)
        
        return {
            'systems_found': list(logs_by_system.keys()),
            'logs_per_system': {system: len(system_logs) for system, system_logs in logs_by_system.items()},
            'timestamp_correlations': timestamp_correlations,
            'ip_correlations': ip_correlations,
            'request_correlations': request_correlations
        }
    
    def _check_timestamp_correlations(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check timestamp correlations across logs."""
        timestamps = []
        for log in logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamps.append(dt)
                except (ValueError, TypeError):
                    continue
        
        if not timestamps:
            return {'valid_timestamps': 0, 'time_span_minutes': 0, 'correlation_score': 0}
        
        timestamps.sort()
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 60
        
        # Check for reasonable time distribution
        correlation_score = 100 if time_span < 60 else max(0, 100 - (time_span - 60) * 2)
        
        return {
            'valid_timestamps': len(timestamps),
            'time_span_minutes': round(time_span, 2),
            'correlation_score': round(correlation_score, 2)
        }
    
    def _check_ip_correlations(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check IP address correlations across logs."""
        ip_addresses = {}
        for log in logs:
            ip = log.get('ip_address')
            if ip:
                ip_addresses[ip] = ip_addresses.get(ip, 0) + 1
        
        unique_ips = len(ip_addresses)
        total_logs = len(logs)
        ip_distribution = max(ip_addresses.values()) if ip_addresses else 0
        
        return {
            'unique_ips': unique_ips,
            'total_logs': total_logs,
            'ip_distribution': ip_distribution,
            'correlation_score': round(min(100, unique_ips / total_logs * 100), 2) if total_logs > 0 else 0
        }
    
    def _check_request_correlations(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check request ID correlations across logs."""
        request_ids = {}
        for log in logs:
            req_id = log.get('request_id')
            if req_id:
                request_ids[req_id] = request_ids.get(req_id, 0) + 1
        
        unique_requests = len(request_ids)
        total_logs = len(logs)
        
        return {
            'unique_requests': unique_requests,
            'total_logs': total_logs,
            'correlation_score': round(min(100, unique_requests / total_logs * 100), 2) if total_logs > 0 else 0
        }
    
    def generate_quality_report(self, logs: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive quality report.
        
        Args:
            logs: List of log entries
            
        Returns:
            Formatted quality report string
        """
        batch_quality = self.check_batch_quality(logs)
        correlation_quality = self.check_correlation_quality(logs)
        
        report = []
        report.append("=" * 60)
        report.append("DATA QUALITY REPORT")
        report.append("=" * 60)
        
        # Basic quality metrics
        report.append(f"Total Logs: {batch_quality['total_logs']}")
        report.append(f"Logs with Issues: {batch_quality['logs_with_issues']}")
        report.append(f"Total Issues: {batch_quality['total_issues']}")
        report.append(f"Quality Score: {batch_quality['quality_score']}%")
        report.append(f"Issues per Log: {batch_quality['issues_per_log']}")
        
        # Issue types
        if batch_quality['issue_types']:
            report.append("\nIssue Types:")
            for issue_type, count in sorted(batch_quality['issue_types'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {issue_type}: {count}")
        
        # Correlation metrics
        report.append(f"\nSystems Found: {', '.join(correlation_quality['systems_found'])}")
        report.append("Logs per System:")
        for system, count in correlation_quality['logs_per_system'].items():
            report.append(f"  {system}: {count}")
        
        # Timestamp correlation
        ts_corr = correlation_quality['timestamp_correlations']
        report.append(f"\nTimestamp Correlation:")
        report.append(f"  Valid Timestamps: {ts_corr['valid_timestamps']}")
        report.append(f"  Time Span: {ts_corr['time_span_minutes']} minutes")
        report.append(f"  Correlation Score: {ts_corr['correlation_score']}%")
        
        # IP correlation
        ip_corr = correlation_quality['ip_correlations']
        report.append(f"\nIP Correlation:")
        report.append(f"  Unique IPs: {ip_corr['unique_ips']}")
        report.append(f"  Correlation Score: {ip_corr['correlation_score']}%")
        
        # Request correlation
        req_corr = correlation_quality['request_correlations']
        report.append(f"\nRequest Correlation:")
        report.append(f"  Unique Requests: {req_corr['unique_requests']}")
        report.append(f"  Correlation Score: {req_corr['correlation_score']}%")
        
        # Overall assessment
        overall_score = (batch_quality['quality_score'] + ts_corr['correlation_score'] + 
                        ip_corr['correlation_score'] + req_corr['correlation_score']) / 4
        
        report.append(f"\nOverall Quality Score: {round(overall_score, 2)}%")
        
        if overall_score >= 90:
            report.append("🎉 Excellent data quality!")
        elif overall_score >= 75:
            report.append("✅ Good data quality")
        elif overall_score >= 50:
            report.append("⚠️  Fair data quality - some improvements needed")
        else:
            report.append("❌ Poor data quality - significant issues found")
        
        return "\n".join(report)
