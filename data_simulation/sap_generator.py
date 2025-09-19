"""
SAP transaction log generator for data simulation.
Generates realistic SAP-formatted log entries for business transactions.
"""

import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import structlog

from .base_generator import BaseLogGenerator

logger = structlog.get_logger(__name__)

class SAPLogGenerator(BaseLogGenerator):
    """Generator for SAP-formatted transaction log entries."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SAP log generator."""
        super().__init__("sap", config)
        
        # SAP-specific configuration
        self.sap_systems = config.get('sap_systems', [
            'ERP_PROD', 'ERP_DEV', 'CRM_PROD', 'CRM_DEV',
            'SCM_PROD', 'SCM_DEV', 'HCM_PROD', 'HCM_DEV'
        ])
        
        self.sap_clients = config.get('sap_clients', ['100', '200', '300', '400'])
        self.sap_servers = config.get('sap_servers', [
            'sap-erp-01', 'sap-erp-02', 'sap-crm-01', 'sap-hcm-01'
        ])
        
        # SAP transaction patterns
        self.transaction_patterns = {
            'financial': self._generate_financial_transaction,
            'sales': self._generate_sales_transaction,
            'purchase': self._generate_purchase_transaction,
            'inventory': self._generate_inventory_transaction,
            'hr': self._generate_hr_transaction,
            'system': self._generate_system_transaction,
            'security': self._generate_security_transaction,
            'performance': self._generate_performance_transaction
        }
        
        # SAP transaction codes (real SAP T-codes)
        self.transaction_codes = {
            'financial': ['FB01', 'FB02', 'FB03', 'F-02', 'F-04', 'F-07', 'F-08'],
            'sales': ['VA01', 'VA02', 'VA03', 'VA11', 'VA12', 'VA13', 'VK11', 'VK12'],
            'purchase': ['ME21N', 'ME22N', 'ME23N', 'ME31L', 'ME32L', 'ME33L'],
            'inventory': ['MB01', 'MB02', 'MB03', 'MIGO', 'MI01', 'MI02', 'MI03'],
            'hr': ['PA20', 'PA30', 'PA40', 'PA41', 'PA42', 'PA43', 'PA44'],
            'system': ['SM50', 'SM51', 'SM66', 'ST22', 'ST01', 'ST02', 'ST03'],
            'security': ['SU01', 'SU02', 'SU03', 'SU53', 'SU56', 'SU01D', 'SU02D'],
            'performance': ['ST03N', 'ST04', 'ST05', 'ST06', 'ST07', 'ST08', 'ST09']
        }
        
        # SAP user roles and departments
        self.user_roles = [
            'FI_ACCOUNTANT', 'SD_SALES', 'MM_PURCHASING', 'PP_PRODUCTION',
            'HR_ADMIN', 'IT_ADMIN', 'SECURITY_ADMIN', 'SYSTEM_ADMIN'
        ]
        
        self.departments = [
            'FINANCE', 'SALES', 'PURCHASING', 'PRODUCTION', 'HR', 'IT', 'SECURITY'
        ]
        
        # SAP message types and severity levels
        self.sap_message_types = ['S', 'I', 'W', 'E', 'A', 'X']  # Success, Info, Warning, Error, Abort, Exit
        self.sap_severity_levels = ['1', '2', '3', '4', '5', '6', '7', '8']  # 1=Highest, 8=Lowest
        
        logger.info(
            "SAP log generator initialized",
            sap_systems=len(self.sap_systems),
            transaction_types=len(self.transaction_patterns)
        )
    
    def generate_log(self) -> Dict[str, Any]:
        """Generate a SAP transaction log entry."""
        # Select transaction type
        transaction_type = random.choice(list(self.transaction_patterns.keys()))
        
        # Generate transaction data
        transaction_data = self.transaction_patterns[transaction_type]()
        
        # Add SAP-specific fields
        transaction_data.update({
            "sap_system": random.choice(self.sap_systems),
            "sap_client": random.choice(self.sap_clients),
            "sap_server": random.choice(self.sap_servers),
            "transaction_type": transaction_type,
            "sap_message_type": random.choice(self.sap_message_types),
            "sap_severity": random.choice(self.sap_severity_levels)
        })
        
        # Generate raw SAP log message
        raw_log = self._format_sap_log(transaction_data)
        
        # Build final log entry
        log_entry = {
            "log_id": self.generate_log_id(),
            "source_id": str(uuid.uuid4()),
            "timestamp": self.generate_timestamp(),
            "level": self._sap_severity_to_level(transaction_data["sap_severity"]),
            "message": transaction_data.get("message", "SAP transaction log"),
            "raw_log": raw_log,
            "category": "sap_transaction",
            "tags": self.generate_tags() + [transaction_type, "sap"],
            "metadata": {
                **self.generate_metadata(),
                **transaction_data
            }
        }
        
        return log_entry
    
    def simulate_anomaly(self) -> Dict[str, Any]:
        """Generate an anomalous SAP transaction log entry."""
        anomaly_types = [
            "failed_transaction",
            "security_violation",
            "performance_issue",
            "data_integrity_error",
            "system_error",
            "business_rule_violation"
        ]
        
        anomaly_type = random.choice(anomaly_types)
        
        if anomaly_type == "failed_transaction":
            return self._generate_failed_transaction_anomaly()
        elif anomaly_type == "security_violation":
            return self._generate_security_violation_anomaly()
        elif anomaly_type == "performance_issue":
            return self._generate_performance_issue_anomaly()
        elif anomaly_type == "data_integrity_error":
            return self._generate_data_integrity_error_anomaly()
        elif anomaly_type == "system_error":
            return self._generate_system_error_anomaly()
        else:  # business_rule_violation
            return self._generate_business_rule_violation_anomaly()
    
    def _generate_financial_transaction(self) -> Dict[str, Any]:
        """Generate financial transaction log."""
        tcode = random.choice(self.transaction_codes['financial'])
        amount = random.uniform(100, 100000)
        currency = random.choice(['USD', 'EUR', 'GBP', 'JPY'])
        
        messages = [
            f"Financial document {random.randint(1000000, 9999999)} posted successfully",
            f"Journal entry created for {currency} {amount:,.2f}",
            f"Account reconciliation completed for {random.choice(['AR', 'AP', 'GL'])}",
            f"Financial report generated for period {random.randint(1, 12)}/{random.randint(2020, 2025)}",
            f"Payment processed for vendor {random.randint(10000, 99999)}"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "amount": round(amount, 2),
            "currency": currency,
            "document_number": random.randint(1000000, 9999999),
            "account_type": random.choice(['AR', 'AP', 'GL', 'AA', 'CO']),
            "fiscal_year": random.randint(2020, 2025),
            "posting_period": random.randint(1, 12),
            "user_role": random.choice(['FI_ACCOUNTANT', 'FI_MANAGER']),
            "department": "FINANCE"
        }
    
    def _generate_sales_transaction(self) -> Dict[str, Any]:
        """Generate sales transaction log."""
        tcode = random.choice(self.transaction_codes['sales'])
        order_value = random.uniform(500, 50000)
        customer_id = random.randint(10000, 99999)
        
        messages = [
            f"Sales order {random.randint(1000000, 9999999)} created for customer {customer_id}",
            f"Quote generated for {random.choice(['USD', 'EUR'])} {order_value:,.2f}",
            f"Pricing condition updated for material {random.randint(100000, 999999)}",
            f"Sales document {random.randint(1000000, 9999999)} delivered successfully",
            f"Customer {customer_id} credit limit checked and approved"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "order_value": round(order_value, 2),
            "customer_id": customer_id,
            "sales_document": random.randint(1000000, 9999999),
            "material_number": random.randint(100000, 999999),
            "sales_org": random.choice(['1000', '2000', '3000']),
            "distribution_channel": random.choice(['10', '20', '30']),
            "division": random.choice(['00', '10', '20']),
            "user_role": random.choice(['SD_SALES', 'SD_MANAGER']),
            "department": "SALES"
        }
    
    def _generate_purchase_transaction(self) -> Dict[str, Any]:
        """Generate purchase transaction log."""
        tcode = random.choice(self.transaction_codes['purchase'])
        po_value = random.uniform(1000, 100000)
        vendor_id = random.randint(10000, 99999)
        
        messages = [
            f"Purchase order {random.randint(1000000, 9999999)} created for vendor {vendor_id}",
            f"PO approval workflow initiated for {random.choice(['USD', 'EUR'])} {po_value:,.2f}",
            f"Goods receipt posted for PO {random.randint(1000000, 9999999)}",
            f"Vendor {vendor_id} master data updated",
            f"Purchase requisition {random.randint(1000000, 9999999)} converted to PO"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "po_value": round(po_value, 2),
            "vendor_id": vendor_id,
            "purchase_order": random.randint(1000000, 9999999),
            "material_number": random.randint(100000, 999999),
            "purchasing_org": random.choice(['1000', '2000', '3000']),
            "company_code": random.choice(['1000', '2000', '3000']),
            "user_role": random.choice(['MM_PURCHASING', 'MM_MANAGER']),
            "department": "PURCHASING"
        }
    
    def _generate_inventory_transaction(self) -> Dict[str, Any]:
        """Generate inventory transaction log."""
        tcode = random.choice(self.transaction_codes['inventory'])
        quantity = random.randint(1, 1000)
        material_id = random.randint(100000, 999999)
        
        messages = [
            f"Material {material_id} quantity updated by {quantity} units",
            f"Goods movement {random.randint(1000000, 9999999)} posted successfully",
            f"Inventory count completed for plant {random.choice(['1000', '2000', '3000'])}",
            f"Material {material_id} transferred between storage locations",
            f"Stock adjustment posted for material {material_id}"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "quantity": quantity,
            "material_id": material_id,
            "movement_type": random.choice(['101', '102', '103', '104', '105']),
            "plant": random.choice(['1000', '2000', '3000']),
            "storage_location": random.choice(['0001', '0002', '0003']),
            "batch_number": f"B{random.randint(100000, 999999)}",
            "user_role": random.choice(['MM_INVENTORY', 'MM_MANAGER']),
            "department": "PURCHASING"
        }
    
    def _generate_hr_transaction(self) -> Dict[str, Any]:
        """Generate HR transaction log."""
        tcode = random.choice(self.transaction_codes['hr'])
        employee_id = random.randint(10000, 99999)
        
        messages = [
            f"Employee {employee_id} personal data updated",
            f"Payroll run completed for period {random.randint(1, 12)}/{random.randint(2020, 2025)}",
            f"Time entry recorded for employee {employee_id}",
            f"Leave request {random.randint(1000000, 9999999)} approved",
            f"Employee {employee_id} organizational assignment changed"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "employee_id": employee_id,
            "personnel_number": random.randint(100000, 999999),
            "payroll_area": random.choice(['01', '02', '03']),
            "cost_center": random.choice(['1000', '2000', '3000']),
            "employment_status": random.choice(['ACTIVE', 'INACTIVE', 'TERMINATED']),
            "user_role": random.choice(['HR_ADMIN', 'HR_MANAGER']),
            "department": "HR"
        }
    
    def _generate_system_transaction(self) -> Dict[str, Any]:
        """Generate system administration transaction log."""
        tcode = random.choice(self.transaction_codes['system'])
        
        messages = [
            f"System backup completed successfully",
            f"User session {random.randint(100000, 999999)} terminated",
            f"System performance monitoring data collected",
            f"Database maintenance completed for table {random.choice(['T001', 'T002', 'T003'])}",
            f"System configuration updated for parameter {random.choice(['PARAM1', 'PARAM2', 'PARAM3'])}"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "session_id": random.randint(100000, 999999),
            "table_name": random.choice(['T001', 'T002', 'T003', 'T004', 'T005']),
            "parameter_name": random.choice(['PARAM1', 'PARAM2', 'PARAM3', 'PARAM4', 'PARAM5']),
            "backup_type": random.choice(['FULL', 'INCREMENTAL', 'DIFFERENTIAL']),
            "user_role": random.choice(['IT_ADMIN', 'SYSTEM_ADMIN']),
            "department": "IT"
        }
    
    def _generate_security_transaction(self) -> Dict[str, Any]:
        """Generate security-related transaction log."""
        tcode = random.choice(self.transaction_codes['security'])
        user_id = f"USER{random.randint(1000, 9999)}"
        
        messages = [
            f"User {user_id} login successful",
            f"Password change completed for user {user_id}",
            f"Role assignment updated for user {user_id}",
            f"Security audit log generated for period {random.randint(1, 12)}/{random.randint(2020, 2025)}",
            f"User {user_id} access rights modified"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "user_id": user_id,
            "role_name": random.choice(['FI_ACCOUNTANT', 'SD_SALES', 'MM_PURCHASING']),
            "access_type": random.choice(['READ', 'WRITE', 'ADMIN']),
            "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "session_duration": random.randint(30, 480),  # minutes
            "user_role": random.choice(['SECURITY_ADMIN', 'IT_ADMIN']),
            "department": "SECURITY"
        }
    
    def _generate_performance_transaction(self) -> Dict[str, Any]:
        """Generate performance monitoring transaction log."""
        tcode = random.choice(self.transaction_codes['performance'])
        response_time = random.uniform(0.1, 5.0)
        
        messages = [
            f"Transaction {tcode} executed in {response_time:.2f} seconds",
            f"Database query performance report generated",
            f"System resource utilization: CPU {random.randint(20, 90)}%, Memory {random.randint(30, 85)}%",
            f"Workload analysis completed for period {random.randint(1, 12)}/{random.randint(2020, 2025)}",
            f"Performance bottleneck identified in module {random.choice(['FI', 'SD', 'MM', 'PP'])}"
        ]
        
        return {
            "level": "INFO",
            "message": random.choice(messages),
            "transaction_code": tcode,
            "response_time": round(response_time, 2),
            "cpu_usage": random.randint(20, 90),
            "memory_usage": random.randint(30, 85),
            "database_hits": random.randint(100, 10000),
            "workload_type": random.choice(['OLTP', 'OLAP', 'BATCH']),
            "module": random.choice(['FI', 'SD', 'MM', 'PP', 'HR', 'CO']),
            "user_role": random.choice(['IT_ADMIN', 'SYSTEM_ADMIN']),
            "department": "IT"
        }
    
    def _generate_failed_transaction_anomaly(self) -> Dict[str, Any]:
        """Generate failed transaction anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "ERROR"
        log_entry["message"] = "SAP transaction failed - Database constraint violation"
        log_entry["metadata"]["anomaly_type"] = "failed_transaction"
        log_entry["metadata"]["severity"] = "high"
        log_entry["metadata"]["error_code"] = random.choice(['DB001', 'DB002', 'DB003'])
        log_entry["metadata"]["error_message"] = "Foreign key constraint violation detected"
        log_entry["metadata"]["retry_count"] = random.randint(1, 5)
        log_entry["raw_log"] = f"ERROR: Transaction {log_entry['metadata']['transaction_code']} failed - {log_entry['metadata']['error_message']} (Code: {log_entry['metadata']['error_code']})"
        return log_entry
    
    def _generate_security_violation_anomaly(self) -> Dict[str, Any]:
        """Generate security violation anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "FATAL"
        log_entry["message"] = "SECURITY ALERT - Unauthorized access attempt detected"
        log_entry["metadata"]["anomaly_type"] = "security_violation"
        log_entry["metadata"]["severity"] = "critical"
        log_entry["metadata"]["violation_type"] = random.choice(['UNAUTHORIZED_ACCESS', 'PRIVILEGE_ESCALATION', 'DATA_BREACH'])
        log_entry["metadata"]["blocked_ip"] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        log_entry["metadata"]["attempt_count"] = random.randint(5, 50)
        log_entry["raw_log"] = f"FATAL: Security violation - {log_entry['metadata']['violation_type']} from IP {log_entry['metadata']['blocked_ip']} (Attempts: {log_entry['metadata']['attempt_count']})"
        return log_entry
    
    def _generate_performance_issue_anomaly(self) -> Dict[str, Any]:
        """Generate performance issue anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "ERROR"
        log_entry["message"] = "PERFORMANCE ALERT - Transaction response time exceeded threshold"
        log_entry["metadata"]["anomaly_type"] = "performance_issue"
        log_entry["metadata"]["severity"] = "high"
        log_entry["metadata"]["response_time"] = random.uniform(10.0, 60.0)
        log_entry["metadata"]["threshold"] = 5.0
        log_entry["metadata"]["affected_users"] = random.randint(10, 100)
        log_entry["raw_log"] = f"ERROR: Performance issue - Response time {log_entry['metadata']['response_time']:.2f}s exceeds threshold {log_entry['metadata']['threshold']}s (Affected users: {log_entry['metadata']['affected_users']})"
        return log_entry
    
    def _generate_data_integrity_error_anomaly(self) -> Dict[str, Any]:
        """Generate data integrity error anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "ERROR"
        log_entry["message"] = "DATA INTEGRITY ERROR - Inconsistent data detected in business object"
        log_entry["metadata"]["anomaly_type"] = "data_integrity_error"
        log_entry["metadata"]["severity"] = "high"
        log_entry["metadata"]["error_type"] = random.choice(['REFERENTIAL_INTEGRITY', 'DATA_VALIDATION', 'BUSINESS_RULE'])
        log_entry["metadata"]["affected_records"] = random.randint(100, 10000)
        log_entry["metadata"]["table_name"] = random.choice(['T001', 'T002', 'T003', 'T004', 'T005'])
        log_entry["raw_log"] = f"ERROR: Data integrity error - {log_entry['metadata']['error_type']} in table {log_entry['metadata']['table_name']} (Affected records: {log_entry['metadata']['affected_records']})"
        return log_entry
    
    def _generate_system_error_anomaly(self) -> Dict[str, Any]:
        """Generate system error anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "FATAL"
        log_entry["message"] = "SYSTEM ERROR - Critical system failure detected"
        log_entry["metadata"]["anomaly_type"] = "system_error"
        log_entry["metadata"]["severity"] = "critical"
        log_entry["metadata"]["error_type"] = random.choice(['DATABASE_CONNECTION', 'MEMORY_OVERFLOW', 'DISK_SPACE', 'NETWORK_TIMEOUT'])
        log_entry["metadata"]["error_code"] = random.choice(['SYS001', 'SYS002', 'SYS003', 'SYS004'])
        log_entry["metadata"]["system_status"] = "DOWN"
        log_entry["raw_log"] = f"FATAL: System error - {log_entry['metadata']['error_type']} (Code: {log_entry['metadata']['error_code']}) - System status: {log_entry['metadata']['system_status']}"
        return log_entry
    
    def _generate_business_rule_violation_anomaly(self) -> Dict[str, Any]:
        """Generate business rule violation anomaly."""
        log_entry = self.generate_log()
        log_entry["level"] = "WARN"
        log_entry["message"] = "BUSINESS RULE VIOLATION - Transaction violates company policy"
        log_entry["metadata"]["anomaly_type"] = "business_rule_violation"
        log_entry["metadata"]["severity"] = "medium"
        log_entry["metadata"]["rule_type"] = random.choice(['APPROVAL_LIMIT', 'BUDGET_EXCEEDED', 'AUTHORIZATION_MISSING', 'VALIDATION_FAILED'])
        log_entry["metadata"]["rule_id"] = f"RULE_{random.randint(1000, 9999)}"
        log_entry["metadata"]["violation_details"] = "Transaction amount exceeds user approval limit"
        log_entry["raw_log"] = f"WARN: Business rule violation - {log_entry['metadata']['rule_type']} (Rule: {log_entry['metadata']['rule_id']}) - {log_entry['metadata']['violation_details']}"
        return log_entry
    
    def _format_sap_log(self, transaction_data: Dict[str, Any]) -> str:
        """Format SAP log message."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        tcode = transaction_data.get('transaction_code', 'UNKNOWN')
        message_type = transaction_data.get('sap_message_type', 'I')
        severity = transaction_data.get('sap_severity', '3')
        message = transaction_data.get('message', 'SAP transaction log')
        
        return f"{timestamp}|{tcode}|{message_type}|{severity}|{message}"
    
    def _sap_severity_to_level(self, sap_severity: str) -> str:
        """Convert SAP severity to standard log level."""
        severity_map = {
            '1': 'FATAL',   # Highest severity
            '2': 'FATAL',
            '3': 'ERROR',
            '4': 'ERROR',
            '5': 'WARN',
            '6': 'WARN',
            '7': 'INFO',
            '8': 'INFO'     # Lowest severity
        }
        return severity_map.get(sap_severity, 'INFO')
    
    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple SAP log entries efficiently."""
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
        """Test SAP log generation performance."""
        import time
        
        start_time = time.time()
        logs = self.generate_batch(count)
        end_time = time.time()
        
        duration = end_time - start_time
        logs_per_second = count / duration if duration > 0 else 0
        
        # Analyze log distribution
        transaction_counts = {}
        level_counts = {}
        anomaly_count = 0
        
        for log in logs:
            transaction_type = log.get('metadata', {}).get('transaction_type', 'unknown')
            level = log.get('level', 'unknown')
            
            transaction_counts[transaction_type] = transaction_counts.get(transaction_type, 0) + 1
            level_counts[level] = level_counts.get(level, 0) + 1
            
            if 'anomaly_type' in log.get('metadata', {}):
                anomaly_count += 1
        
        return {
            "total_logs": count,
            "duration_seconds": round(duration, 3),
            "logs_per_second": round(logs_per_second, 2),
            "anomaly_count": anomaly_count,
            "anomaly_rate": round(anomaly_count / count, 3),
            "transaction_distribution": transaction_counts,
            "level_distribution": level_counts,
            "performance_rating": "excellent" if logs_per_second > 1000 else "good" if logs_per_second > 500 else "needs_optimization"
        }
