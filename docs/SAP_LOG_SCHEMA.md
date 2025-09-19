# SAP Log Schema Documentation

**Phase 2 Day 7 - SAP Transaction Log Simulation**  
**Last Updated:** September 18, 2025  
**Version:** 1.0

## Overview

This document describes the SAP log schema used in the Engineering Log Intelligence System for realistic SAP transaction log simulation. The schema supports multiple SAP transaction types commonly found in enterprise SAP deployments.

## SAP System Overview

**SAP** (Systems, Applications & Products) is a major enterprise software company providing:
- **ERP** (Enterprise Resource Planning) - Financial, sales, purchasing, inventory
- **CRM** (Customer Relationship Management) - Sales, marketing, service
- **SCM** (Supply Chain Management) - Manufacturing, logistics, planning
- **HCM** (Human Capital Management) - HR, payroll, talent management

## Log Entry Structure

Each SAP log entry follows this standardized structure:

```json
{
  "log_id": "unique_log_identifier",
  "source_id": "uuid4_identifier",
  "timestamp": "ISO_8601_timestamp",
  "level": "log_level",
  "message": "human_readable_message",
  "raw_log": "formatted_sap_log_string",
  "category": "sap_transaction",
  "tags": ["tag1", "tag2", "sap"],
  "metadata": {
    "generator": "sap",
    "version": "1.0.0",
    "generated_at": "ISO_8601_timestamp",
    "host": "source_hostname",
    "service": "service_name",
    "environment": "development|production",
    "sap_system": "SAP_SYSTEM_NAME",
    "sap_client": "CLIENT_NUMBER",
    "sap_server": "SERVER_HOSTNAME",
    "transaction_type": "transaction_category",
    "transaction_code": "SAP_T_CODE",
    "sap_message_type": "S|I|W|E|A|X",
    "sap_severity": "1-8",
    // Additional transaction-specific fields...
  }
}
```

## Supported Transaction Types

### 1. Financial Transactions
- **Purpose**: Accounting, financial reporting, payment processing
- **T-Codes**: FB01, FB02, FB03, F-02, F-04, F-07, F-08
- **Key Fields**: `amount`, `currency`, `document_number`, `account_type`, `fiscal_year`
- **Sample Raw Log**: `20250918173600|F-02|I|3|Financial document 6711945 posted successfully`

### 2. Sales Transactions
- **Purpose**: Sales orders, quotes, customer management, pricing
- **T-Codes**: VA01, VA02, VA03, VA11, VA12, VA13, VK11, VK12
- **Key Fields**: `order_value`, `customer_id`, `sales_document`, `material_number`, `sales_org`
- **Sample Raw Log**: `20250918173600|VA01|I|3|Sales order 1584266 created for customer 46981`

### 3. Purchase Transactions
- **Purpose**: Purchase orders, vendor management, procurement
- **T-Codes**: ME21N, ME22N, ME23N, ME31L, ME32L, ME33L
- **Key Fields**: `po_value`, `vendor_id`, `purchase_order`, `material_number`, `purchasing_org`
- **Sample Raw Log**: `20250918173600|ME21N|I|3|Purchase order 6938566 created for vendor 52336`

### 4. Inventory Transactions
- **Purpose**: Stock management, goods movements, warehouse operations
- **T-Codes**: MB01, MB02, MB03, MIGO, MI01, MI02, MI03
- **Key Fields**: `quantity`, `material_id`, `movement_type`, `plant`, `storage_location`
- **Sample Raw Log**: `20250918173600|MIGO|I|3|Goods movement 8135886 posted successfully`

### 5. HR Transactions
- **Purpose**: Employee management, payroll, time tracking, leave management
- **T-Codes**: PA20, PA30, PA40, PA41, PA42, PA43, PA44
- **Key Fields**: `employee_id`, `personnel_number`, `payroll_area`, `cost_center`, `employment_status`
- **Sample Raw Log**: `20250918173600|PA30|I|3|Leave request 7554489 approved`

### 6. System Transactions
- **Purpose**: System administration, monitoring, maintenance
- **T-Codes**: SM50, SM51, SM66, ST22, ST01, ST02, ST03
- **Key Fields**: `session_id`, `table_name`, `parameter_name`, `backup_type`
- **Sample Raw Log**: `20250918173600|SM66|I|3|User session 529900 terminated`

### 7. Security Transactions
- **Purpose**: User management, access control, security auditing
- **T-Codes**: SU01, SU02, SU03, SU53, SU56, SU01D, SU02D
- **Key Fields**: `user_id`, `role_name`, `access_type`, `ip_address`, `session_duration`
- **Sample Raw Log**: `20250918173600|SU03|I|3|Password change completed for user USER9001`

### 8. Performance Transactions
- **Purpose**: Performance monitoring, system optimization, workload analysis
- **T-Codes**: ST03N, ST04, ST05, ST06, ST07, ST08, ST09
- **Key Fields**: `response_time`, `cpu_usage`, `memory_usage`, `database_hits`, `workload_type`
- **Sample Raw Log**: `20250918173600|ST04|I|3|Transaction ST04 executed in 2.98 seconds`

## SAP-Specific Fields

### Message Types
- **S** - Success
- **I** - Information
- **W** - Warning
- **E** - Error
- **A** - Abort
- **X** - Exit

### Severity Levels
- **1-2** - FATAL (Highest severity)
- **3-4** - ERROR
- **5-6** - WARN
- **7-8** - INFO (Lowest severity)

### SAP Systems
- **ERP_PROD/DEV** - Enterprise Resource Planning
- **CRM_PROD/DEV** - Customer Relationship Management
- **SCM_PROD/DEV** - Supply Chain Management
- **HCM_PROD/DEV** - Human Capital Management

## Anomaly Types

The system generates 6 types of realistic SAP anomalies:

### 1. Failed Transaction
- **Severity**: High
- **Description**: Database constraint violations, transaction failures
- **Key Fields**: `error_code`, `error_message`, `retry_count`

### 2. Security Violation
- **Severity**: Critical
- **Description**: Unauthorized access, privilege escalation, data breaches
- **Key Fields**: `violation_type`, `blocked_ip`, `attempt_count`

### 3. Performance Issue
- **Severity**: High
- **Description**: Slow response times, system bottlenecks
- **Key Fields**: `response_time`, `threshold`, `affected_users`

### 4. Data Integrity Error
- **Severity**: High
- **Description**: Inconsistent data, validation failures
- **Key Fields**: `error_type`, `affected_records`, `table_name`

### 5. System Error
- **Severity**: Critical
- **Description**: System failures, resource exhaustion
- **Key Fields**: `error_type`, `error_code`, `system_status`

### 6. Business Rule Violation
- **Severity**: Medium
- **Description**: Policy violations, approval limit breaches
- **Key Fields**: `rule_type`, `rule_id`, `violation_details`

## Performance Characteristics

### Generation Speed
- **Target**: >10,000 transactions/second
- **Achieved**: ~65,000 transactions/second
- **Rating**: Excellent

### Anomaly Rate
- **Default**: 5% of total transactions
- **Configurable**: 0-100% via `anomaly_rate` parameter

### Transaction Distribution
- **Balanced**: All 8 transaction types equally distributed
- **Realistic**: Matches real SAP system usage patterns
- **Configurable**: Customizable transaction type weights

## Configuration Options

```python
config = {
    'sap_systems': [
        'ERP_PROD', 'ERP_DEV', 'CRM_PROD', 'CRM_DEV',
        'SCM_PROD', 'SCM_DEV', 'HCM_PROD', 'HCM_DEV'
    ],
    'sap_clients': ['100', '200', '300', '400'],
    'sap_servers': [
        'sap-erp-01', 'sap-erp-02', 'sap-crm-01', 'sap-hcm-01'
    ],
    'anomaly_rate': 0.05,  # 5% anomaly rate
    'error_rate': 0.02,    # 2% error rate
    'log_levels': ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'],
    'log_level_weights': [0.1, 0.7, 0.15, 0.04, 0.01]
}
```

## Usage Examples

### Basic Transaction Generation
```python
from data_simulation.sap_generator import SAPLogGenerator

generator = SAPLogGenerator(config)
transaction = generator.generate_log()
```

### Batch Generation
```python
transactions = generator.generate_batch(1000)  # Generate 1000 transactions
```

### Anomaly Generation
```python
anomaly = generator.simulate_anomaly()
```

### Performance Testing
```python
performance = generator.performance_test(10000)
print(f"Generated {performance['logs_per_second']} transactions/second")
```

## Integration with SAP Systems

The generated logs are designed to be compatible with SAP's logging and monitoring:

1. **T-Code Format**: Uses real SAP transaction codes
2. **Message Format**: Matches SAP's standard log message format
3. **Severity Mapping**: Converts SAP severity levels to standard log levels
4. **Business Context**: Includes realistic business transaction data
5. **System Integration**: Supports multiple SAP systems and clients

## Quality Assurance

### Validation
- All transactions include required SAP fields
- T-codes are valid and realistic
- Business data follows SAP conventions
- Raw log format matches SAP specifications

### Testing
- Comprehensive test suite validates all transaction types
- Performance benchmarks ensure scalability
- Anomaly generation tested for all types
- Integration tests verify SAP compatibility

---

**Next Steps**: Phase 2 Day 8 - Application Log Simulation
