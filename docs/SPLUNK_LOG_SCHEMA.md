# SPLUNK Log Schema Documentation

**Phase 2 Day 6 - SPLUNK Log Simulation**  
**Last Updated:** September 18, 2025  
**Version:** 1.0

## Overview

This document describes the SPLUNK log schema used in the Engineering Log Intelligence System for realistic log data simulation. The schema supports multiple log source types commonly found in enterprise SPLUNK deployments.

## Log Entry Structure

Each SPLUNK log entry follows this standardized structure:

```json
{
  "log_id": "unique_log_identifier",
  "source_id": "uuid4_identifier", 
  "timestamp": "ISO_8601_timestamp",
  "level": "log_level",
  "message": "human_readable_message",
  "raw_log": "formatted_raw_log_string",
  "category": "log_category",
  "tags": ["tag1", "tag2"],
  "metadata": {
    "generator": "splunk",
    "version": "1.0.0",
    "generated_at": "ISO_8601_timestamp",
    "host": "source_hostname",
    "service": "service_name",
    "environment": "development|production",
    "source": "splunk_source_type",
    "sourcetype": "splunk_source_type",
    "index": "splunk_index_name",
    "splunk_server": "splunk_server_hostname",
    // Additional source-specific fields...
  }
}
```

## Supported Source Types

### 1. Windows Event Logs

#### WinEventLog:Security
- **Purpose**: Security-related events (logins, access, permissions)
- **Key Fields**: `event_id`, `user`, `computer`, `event_type`
- **Sample Raw Log**: `[4624] User login successful - DOMAIN\user@COMPUTER`

#### WinEventLog:System  
- **Purpose**: System-level events (services, drivers, hardware)
- **Key Fields**: `event_id`, `service`, `computer`, `event_type`
- **Sample Raw Log**: `[1001] Service started: Windows Update - SYSTEM@COMPUTER`

#### WinEventLog:Application
- **Purpose**: Application-specific events (errors, startups, configurations)
- **Key Fields**: `event_id`, `application`, `computer`, `event_type`
- **Sample Raw Log**: `[2001] WebApp: Application started - SYSTEM@COMPUTER`

### 2. Web Server Logs

#### Apache Access Logs
- **Purpose**: HTTP request/response logging
- **Key Fields**: `ip`, `method`, `path`, `status`, `user_agent`, `response_size`
- **Sample Raw Log**: `192.168.1.100 - - [18/Sep/2025:16:45:30 +0000] "GET /api/users HTTP/1.1" 200 1234`

#### Apache Error Logs
- **Purpose**: Apache server error logging
- **Key Fields**: `module`, `error_type`, `pid`
- **Sample Raw Log**: `[ssl] SSL handshake failed - PID: 1234`

#### IIS Access Logs
- **Purpose**: Microsoft IIS HTTP request logging
- **Key Fields**: `ip`, `method`, `path`, `status`, `user_agent`, `response_size`
- **Sample Raw Log**: `10.0.1.100 GET /api/v1/data - 200`

#### IIS Error Logs
- **Purpose**: Microsoft IIS error logging
- **Key Fields**: `error_code`, `error_type`, `process_id`
- **Sample Raw Log**: `Error 5000: Internal server error - PID: 5678`

### 3. System Logs

#### Syslog
- **Purpose**: Standard Unix/Linux system logging
- **Key Fields**: `facility`, `priority`, `severity`, `hostname`
- **Sample Raw Log**: `<3>server01 Service restarted`

## Anomaly Types

The system generates 6 types of realistic anomalies:

### 1. System Failure
- **Severity**: Critical
- **Description**: Multiple services down, system-wide failures
- **Key Fields**: `affected_services`, `error_count`

### 2. Security Breach
- **Severity**: Critical  
- **Description**: Unauthorized access attempts, security violations
- **Key Fields**: `source_ip`, `attack_type`, `failed_attempts`

### 3. Performance Degradation
- **Severity**: High
- **Description**: Response time thresholds exceeded
- **Key Fields**: `response_time_ms`, `threshold_ms`, `cpu_usage`

### 4. Data Corruption
- **Severity**: High
- **Description**: Data integrity issues detected
- **Key Fields**: `corrupted_records`, `database`

### 5. Network Anomaly
- **Severity**: Medium
- **Description**: Unusual network traffic patterns
- **Key Fields**: `traffic_volume`, `normal_volume`, `protocol`

### 6. Resource Exhaustion
- **Severity**: High
- **Description**: System resources critically low
- **Key Fields**: `memory_usage`, `disk_usage`, `available_memory_mb`

## Performance Characteristics

### Generation Speed
- **Target**: >10,000 logs/second
- **Achieved**: ~90,000 logs/second
- **Rating**: Excellent

### Anomaly Rate
- **Default**: 5% of total logs
- **Configurable**: 0-100% via `anomaly_rate` parameter

### Log Level Distribution
- **INFO**: 70% (default)
- **WARN**: 15% (default)
- **ERROR**: 4% (default)
- **FATAL**: 1% (default)
- **DEBUG**: 10% (default)

## Configuration Options

```python
config = {
    'splunk_sources': [
        'WinEventLog:Security',
        'WinEventLog:System', 
        'WinEventLog:Application',
        'syslog',
        'apache_access',
        'apache_error',
        'iis_access',
        'iis_error'
    ],
    'splunk_hosts': [
        'web-server-01', 'web-server-02', 'db-server-01',
        'app-server-01', 'load-balancer-01', 'monitor-01'
    ],
    'anomaly_rate': 0.05,  # 5% anomaly rate
    'error_rate': 0.02,    # 2% error rate
    'log_levels': ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'],
    'log_level_weights': [0.1, 0.7, 0.15, 0.04, 0.01]
}
```

## Usage Examples

### Basic Log Generation
```python
from data_simulation.splunk_generator import SplunkLogGenerator

generator = SplunkLogGenerator(config)
log = generator.generate_log()
```

### Batch Generation
```python
logs = generator.generate_batch(1000)  # Generate 1000 logs
```

### Anomaly Generation
```python
anomaly = generator.simulate_anomaly()
```

### Performance Testing
```python
performance = generator.performance_test(10000)
print(f"Generated {performance['logs_per_second']} logs/second")
```

## Integration with SPLUNK

The generated logs are designed to be compatible with SPLUNK's parsing and indexing:

1. **Raw Log Format**: Matches standard SPLUNK source formats
2. **Field Extraction**: Structured metadata for easy field extraction
3. **Index Mapping**: Automatic index assignment based on source type
4. **Time Parsing**: ISO 8601 timestamps for accurate time-based analysis

## Quality Assurance

### Validation
- All logs include required SPLUNK fields
- Timestamps are valid ISO 8601 format
- Log levels follow standard conventions
- Raw log format matches source specifications

### Testing
- Comprehensive test suite validates all source types
- Performance benchmarks ensure scalability
- Anomaly generation tested for all types
- Integration tests verify SPLUNK compatibility

---

**Next Steps**: Phase 2 Day 7 - SAP Transaction Log Simulation
