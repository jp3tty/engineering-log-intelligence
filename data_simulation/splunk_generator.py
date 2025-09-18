"""
SPLUNK log generator for data simulation.
Generates realistic SPLUNK-formatted log entries.
"""

import random
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import structlog

from .base_generator import BaseLogGenerator

logger = structlog.get_logger(__name__)

class SplunkLogGenerator(BaseLogGenerator):
    """Generator for SPLUNK-formatted log entries."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SPLUNK log generator."""
        super().__init__("splunk", config)
        
        # SPLUNK-specific configuration
        self.splunk_sources = config.get('splunk_sources', [
            'WinEventLog:Security',
            'WinEventLog:System',
            'WinEventLog:Application',
            'syslog',
            'apache_access',
            'apache_error',
            'iis_access',
            'iis_error'
        ])
        
        self.splunk_hosts = config.get('splunk_hosts', [
            'web-server-01',
            'web-server-02',
            'db-server-01',
            'app-server-01',
            'load-balancer-01'
        ])
        
        # Log patterns for different source types
        self.log_patterns = {
            'WinEventLog:Security': self._generate_security_event,
            'WinEventLog:System': self._generate_system_event,
            'WinEventLog:Application': self._generate_application_event,
            'syslog': self._generate_syslog_event,
            'apache_access': self._generate_apache_access,
            'apache_error': self._generate_apache_error,
            'iis_access': self._generate_iis_access,
            'iis_error': self._generate_iis_error
        }
    
    def generate_log(self) -> Dict[str, Any]:
        """Generate a SPLUNK log entry."""
        # Select source type
        source = random.choice(self.splunk_sources)
        
        # Generate log based on source type
        if source in self.log_patterns:
            log_data = self.log_patterns[source]()
        else:
            log_data = self._generate_generic_log()
        
        # Add SPLUNK-specific fields
        log_data.update({
            "source": source,
            "sourcetype": source,
            "host": random.choice(self.splunk_hosts),
            "index": self._get_index_for_source(source),
            "splunk_server": "splunk-prod.company.com"
        })
        
        # Generate raw log message
        raw_log = self._format_raw_log(log_data, source)
        
        # Build final log entry
        log_entry = {
            "log_id": self.generate_log_id(),
            "source_id": str(uuid.uuid4()),
            "timestamp": self.generate_timestamp(),
            "level": log_data.get("level", self.select_log_level()),
            "message": log_data.get("message", "SPLUNK log entry"),
            "raw_log": raw_log,
            "category": self.select_category(),
            "tags": self.generate_tags(),
            "metadata": {
                **self.generate_metadata(),
                **log_data
            }
        }
        
        return log_entry
    
    def simulate_anomaly(self) -> Dict[str, Any]:
        """Generate an anomalous SPLUNK log entry."""
        anomaly_types = [
            "system_failure",
            "security_breach", 
            "performance_degradation",
            "data_corruption",
            "network_anomaly",
            "resource_exhaustion"
        ]
        
        anomaly_type = random.choice(anomaly_types)
        
        if anomaly_type == "system_failure":
            return self._generate_system_failure_anomaly()
        elif anomaly_type == "security_breach":
            return self._generate_security_breach_anomaly()
        elif anomaly_type == "performance_degradation":
            return self._generate_performance_anomaly()
        elif anomaly_type == "data_corruption":
            return self._generate_data_corruption_anomaly()
        elif anomaly_type == "network_anomaly":
            return self._generate_network_anomaly()
        else:  # resource_exhaustion
            return self._generate_resource_exhaustion_anomaly()
    
    def _generate_system_failure_anomaly(self) -> Dict[str, Any]:
        """Generate system failure anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "FATAL"
        log_entry["message"] = "CRITICAL SYSTEM FAILURE - Multiple services down"
        log_entry["metadata"]["anomaly_type"] = "system_failure"
        log_entry["metadata"]["severity"] = "critical"
        log_entry["metadata"]["affected_services"] = random.sample(self.services, random.randint(2, 4))
        log_entry["metadata"]["error_count"] = random.randint(50, 200)
        log_entry["raw_log"] = f"FATAL: {log_entry['message']} - Services: {', '.join(log_entry['metadata']['affected_services'])} - Error Count: {log_entry['metadata']['error_count']}"
        return log_entry
    
    def _generate_security_breach_anomaly(self) -> Dict[str, Any]:
        """Generate security breach anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "FATAL"
        log_entry["message"] = "SECURITY ALERT - Unauthorized access detected"
        log_entry["metadata"]["anomaly_type"] = "security_breach"
        log_entry["metadata"]["severity"] = "critical"
        log_entry["metadata"]["source_ip"] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        log_entry["metadata"]["attack_type"] = random.choice(["brute_force", "sql_injection", "xss", "privilege_escalation"])
        log_entry["metadata"]["failed_attempts"] = random.randint(10, 100)
        log_entry["raw_log"] = f"FATAL: {log_entry['message']} - IP: {log_entry['metadata']['source_ip']} - Attack: {log_entry['metadata']['attack_type']} - Attempts: {log_entry['metadata']['failed_attempts']}"
        return log_entry
    
    def _generate_performance_anomaly(self) -> Dict[str, Any]:
        """Generate performance degradation anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "ERROR"
        log_entry["message"] = "PERFORMANCE ALERT - Response time exceeded threshold"
        log_entry["metadata"]["anomaly_type"] = "performance_degradation"
        log_entry["metadata"]["severity"] = "high"
        log_entry["metadata"]["response_time_ms"] = random.randint(5000, 30000)
        log_entry["metadata"]["threshold_ms"] = 1000
        log_entry["metadata"]["cpu_usage"] = random.randint(90, 100)
        log_entry["raw_log"] = f"ERROR: {log_entry['message']} - Response Time: {log_entry['metadata']['response_time_ms']}ms (Threshold: {log_entry['metadata']['threshold_ms']}ms) - CPU: {log_entry['metadata']['cpu_usage']}%"
        return log_entry
    
    def _generate_data_corruption_anomaly(self) -> Dict[str, Any]:
        """Generate data corruption anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "ERROR"
        log_entry["message"] = "DATA INTEGRITY ALERT - Corrupted data detected"
        log_entry["metadata"]["anomaly_type"] = "data_corruption"
        log_entry["metadata"]["severity"] = "high"
        log_entry["metadata"]["corrupted_records"] = random.randint(100, 1000)
        log_entry["metadata"]["database"] = random.choice(["users", "transactions", "logs", "config"])
        log_entry["raw_log"] = f"ERROR: {log_entry['message']} - Database: {log_entry['metadata']['database']} - Corrupted Records: {log_entry['metadata']['corrupted_records']}"
        return log_entry
    
    def _generate_network_anomaly(self) -> Dict[str, Any]:
        """Generate network anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "WARN"
        log_entry["message"] = "NETWORK ALERT - Unusual traffic pattern detected"
        log_entry["metadata"]["anomaly_type"] = "network_anomaly"
        log_entry["metadata"]["severity"] = "medium"
        log_entry["metadata"]["traffic_volume"] = random.randint(1000, 10000)
        log_entry["metadata"]["normal_volume"] = random.randint(100, 500)
        log_entry["metadata"]["protocol"] = random.choice(["TCP", "UDP", "HTTP", "HTTPS"])
        log_entry["raw_log"] = f"WARN: {log_entry['message']} - Protocol: {log_entry['metadata']['protocol']} - Volume: {log_entry['metadata']['traffic_volume']} (Normal: {log_entry['metadata']['normal_volume']})"
        return log_entry
    
    def _generate_resource_exhaustion_anomaly(self) -> Dict[str, Any]:
        """Generate resource exhaustion anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "ERROR"
        log_entry["message"] = "RESOURCE ALERT - System resources exhausted"
        log_entry["metadata"]["anomaly_type"] = "resource_exhaustion"
        log_entry["metadata"]["severity"] = "high"
        log_entry["metadata"]["memory_usage"] = random.randint(95, 100)
        log_entry["metadata"]["disk_usage"] = random.randint(90, 100)
        log_entry["metadata"]["available_memory_mb"] = random.randint(10, 100)
        log_entry["raw_log"] = f"ERROR: {log_entry['message']} - Memory: {log_entry['metadata']['memory_usage']}% - Disk: {log_entry['metadata']['disk_usage']}% - Available: {log_entry['metadata']['available_memory_mb']}MB"
        return log_entry
    
    def _generate_security_event(self) -> Dict[str, Any]:
        """Generate Windows Security Event log."""
        events = [
            "User login successful",
            "User login failed",
            "User logout",
            "Password change",
            "Account locked",
            "Privilege escalation",
            "File access denied",
            "Process started",
            "Process terminated"
        ]
        
        event = random.choice(events)
        user = f"user{random.randint(1, 1000)}"
        domain = random.choice(["COMPANY", "LOCAL"])
        
        return {
            "level": "INFO" if "successful" in event else "WARN",
            "message": event,
            "event_id": random.randint(4624, 4634),
            "user": f"{domain}\\{user}",
            "computer": random.choice(self.splunk_hosts),
            "event_type": "Security"
        }
    
    def _generate_system_event(self) -> Dict[str, Any]:
        """Generate Windows System Event log."""
        events = [
            "Service started",
            "Service stopped",
            "System startup",
            "System shutdown",
            "Driver loaded",
            "Driver failed",
            "Disk space low",
            "Memory low",
            "Network adapter connected"
        ]
        
        event = random.choice(events)
        service = random.choice(["Windows Update", "SQL Server", "IIS", "DNS", "DHCP"])
        
        return {
            "level": "INFO" if "started" in event or "connected" in event else "WARN",
            "message": f"{event}: {service}",
            "event_id": random.randint(1000, 1099),
            "service": service,
            "computer": random.choice(self.splunk_hosts),
            "event_type": "System"
        }
    
    def _generate_application_event(self) -> Dict[str, Any]:
        """Generate Windows Application Event log."""
        events = [
            "Application started",
            "Application error",
            "Database connection failed",
            "Configuration loaded",
            "User session created",
            "Cache cleared",
            "Backup completed",
            "Backup failed",
            "License expired"
        ]
        
        event = random.choice(events)
        app = random.choice(["WebApp", "Database", "API", "Scheduler", "Monitor"])
        
        return {
            "level": "ERROR" if "failed" in event or "error" in event else "INFO",
            "message": f"{app}: {event}",
            "event_id": random.randint(2000, 2099),
            "application": app,
            "computer": random.choice(self.splunk_hosts),
            "event_type": "Application"
        }
    
    def _generate_syslog_event(self) -> Dict[str, Any]:
        """Generate syslog event."""
        facilities = ["kern", "user", "mail", "daemon", "auth", "syslog", "lpr", "news"]
        facilities = random.choice(facilities)
        
        messages = [
            "System booted",
            "User login",
            "Service restarted",
            "Configuration changed",
            "Error occurred",
            "Warning generated",
            "Info message",
            "Debug output"
        ]
        
        message = random.choice(messages)
        priority = random.randint(0, 7)
        
        return {
            "level": self._priority_to_level(priority),
            "message": message,
            "facility": facilities,
            "priority": priority,
            "severity": priority % 8,
            "hostname": random.choice(self.splunk_hosts)
        }
    
    def _generate_apache_access(self) -> Dict[str, Any]:
        """Generate Apache access log."""
        methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
        status_codes = [200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]
        
        method = random.choice(methods)
        status = random.choice(status_codes)
        path = random.choice([
            "/", "/api/users", "/api/data", "/login", "/dashboard",
            "/reports", "/admin", "/static/css/style.css", "/images/logo.png"
        ])
        
        ip = f"192.168.1.{random.randint(1, 254)}"
        user_agent = random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ])
        
        return {
            "level": "INFO",
            "message": f"{method} {path} HTTP/1.1 {status}",
            "ip": ip,
            "method": method,
            "path": path,
            "status": status,
            "user_agent": user_agent,
            "response_size": random.randint(100, 10000)
        }
    
    def _generate_apache_error(self) -> Dict[str, Any]:
        """Generate Apache error log."""
        errors = [
            "File does not exist",
            "Permission denied",
            "Connection refused",
            "Timeout waiting for input",
            "Invalid request",
            "SSL handshake failed",
            "Module not found",
            "Configuration error"
        ]
        
        error = random.choice(errors)
        module = random.choice(["core", "ssl", "rewrite", "auth", "proxy"])
        
        return {
            "level": "ERROR",
            "message": f"[{module}] {error}",
            "module": module,
            "error_type": error,
            "pid": random.randint(1000, 9999)
        }
    
    def _generate_iis_access(self) -> Dict[str, Any]:
        """Generate IIS access log."""
        methods = ["GET", "POST", "PUT", "DELETE"]
        status_codes = [200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]
        
        method = random.choice(methods)
        status = random.choice(status_codes)
        path = random.choice([
            "/", "/api/v1/users", "/api/v1/data", "/login.aspx", "/default.aspx",
            "/reports/report1.aspx", "/admin/users.aspx", "/css/style.css"
        ])
        
        ip = f"10.0.{random.randint(1, 255)}.{random.randint(1, 254)}"
        
        return {
            "level": "INFO",
            "message": f"{method} {path} - {status}",
            "ip": ip,
            "method": method,
            "path": path,
            "status": status,
            "user_agent": "Mozilla/5.0 (compatible; MSIE 11.0; Windows NT 10.0)",
            "response_size": random.randint(200, 5000)
        }
    
    def _generate_iis_error(self) -> Dict[str, Any]:
        """Generate IIS error log."""
        errors = [
            "The page cannot be found",
            "Access is denied",
            "Internal server error",
            "Application error",
            "Configuration error",
            "Module load error",
            "Handler not found",
            "Request timeout"
        ]
        
        error = random.choice(errors)
        
        return {
            "level": "ERROR",
            "message": error,
            "error_code": random.randint(1000, 9999),
            "error_type": error,
            "process_id": random.randint(1000, 9999)
        }
    
    def _generate_generic_log(self) -> Dict[str, Any]:
        """Generate generic log entry."""
        messages = [
            "System operation completed",
            "User action performed",
            "Data processed",
            "Configuration updated",
            "Status check passed",
            "Resource allocated",
            "Task scheduled",
            "Event triggered"
        ]
        
        return {
            "level": self.select_log_level(),
            "message": random.choice(messages),
            "component": random.choice(["system", "application", "service", "module"])
        }
    
    def _get_index_for_source(self, source: str) -> str:
        """Get SPLUNK index for source type."""
        index_mapping = {
            'WinEventLog:Security': 'security',
            'WinEventLog:System': 'system',
            'WinEventLog:Application': 'application',
            'syslog': 'syslog',
            'apache_access': 'web',
            'apache_error': 'web',
            'iis_access': 'web',
            'iis_error': 'web'
        }
        return index_mapping.get(source, 'main')
    
    def _priority_to_level(self, priority: int) -> str:
        """Convert syslog priority to log level."""
        if priority <= 2:
            return "FATAL"
        elif priority <= 4:
            return "ERROR"
        elif priority <= 6:
            return "WARN"
        else:
            return "INFO"
    
    def _format_raw_log(self, log_data: Dict[str, Any], source: str) -> str:
        """Format raw log message based on source type."""
        if source.startswith('WinEventLog'):
            return f"[{log_data.get('event_id', 'N/A')}] {log_data.get('message', '')} - {log_data.get('user', 'SYSTEM')}@{log_data.get('computer', 'UNKNOWN')}"
        elif source == 'syslog':
            return f"<{log_data.get('priority', 0)}>{log_data.get('hostname', 'localhost')} {log_data.get('message', '')}"
        elif source.startswith('apache'):
            return f"{log_data.get('ip', '127.0.0.1')} - - [{datetime.now(timezone.utc).strftime('%d/%b/%Y:%H:%M:%S')} +0000] \"{log_data.get('method', 'GET')} {log_data.get('path', '/')} HTTP/1.1\" {log_data.get('status', 200)} {log_data.get('response_size', 0)}"
        elif source.startswith('iis'):
            return f"{log_data.get('ip', '127.0.0.1')} {log_data.get('method', 'GET')} {log_data.get('path', '/')} - {log_data.get('status', 200)}"
        else:
            return f"{log_data.get('level', 'INFO')}: {log_data.get('message', '')}"
    
    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple SPLUNK log entries efficiently."""
        logs = []
        anomaly_count = int(count * self.anomaly_rate)
        
        # Generate normal logs
        for _ in range(count - anomaly_count):
            logs.append(self.generate_log())
        
        # Generate anomaly logs
        for _ in range(anomaly_count):
            logs.append(self.simulate_anomaly())
        
        # Shuffle to mix normal and anomaly logs
        random.shuffle(logs)
        
        return logs
    
    def performance_test(self, count: int = 1000) -> Dict[str, Any]:
        """Test log generation performance."""
        import time
        
        start_time = time.time()
        logs = self.generate_batch(count)
        end_time = time.time()
        
        duration = end_time - start_time
        logs_per_second = count / duration if duration > 0 else 0
        
        # Analyze log distribution
        source_counts = {}
        level_counts = {}
        anomaly_count = 0
        
        for log in logs:
            source = log.get('metadata', {}).get('source', 'unknown')
            level = log.get('level', 'unknown')
            
            source_counts[source] = source_counts.get(source, 0) + 1
            level_counts[level] = level_counts.get(level, 0) + 1
            
            if 'anomaly_type' in log.get('metadata', {}):
                anomaly_count += 1
        
        return {
            "total_logs": count,
            "duration_seconds": round(duration, 3),
            "logs_per_second": round(logs_per_second, 2),
            "anomaly_count": anomaly_count,
            "anomaly_rate": round(anomaly_count / count, 3),
            "source_distribution": source_counts,
            "level_distribution": level_counts,
            "performance_rating": "excellent" if logs_per_second > 1000 else "good" if logs_per_second > 500 else "needs_optimization"
        }
