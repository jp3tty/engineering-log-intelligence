"""
Day 24: Automated Incident Response System Testing

This script tests the comprehensive incident response and alerting systems including:
- Incident creation and management
- Alert processing and correlation
- Escalation workflows
- Notification systems
- Integration between alerting and incident response
"""

import json
import requests
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import uuid


class IncidentResponseTester:
    """Test suite for incident response and alerting systems."""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.test_results = []
        self.incident_ids = []
        self.alert_ids = []
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", data: Dict = None):
        """Log test result."""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': data or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()
    
    def test_incident_creation(self) -> bool:
        """Test creating incidents."""
        print("🧪 Testing Incident Creation...")
        
        try:
            # Test data for different incident types
            test_incidents = [
                {
                    'title': 'Database Connection Failure',
                    'description': 'Multiple database connection timeouts detected across services',
                    'severity': 'critical',
                    'category': 'database',
                    'priority': 2,
                    'source': 'automated',
                    'metadata': {
                        'affected_services': ['postgresql', 'redis'],
                        'error_count': 150,
                        'first_error': (datetime.now(timezone.utc) - timedelta(minutes=35)).isoformat()
                    }
                },
                {
                    'title': 'High Error Rate Detected',
                    'description': 'Application error rate increased to 15% in the last hour',
                    'severity': 'high',
                    'category': 'performance',
                    'priority': 3,
                    'source': 'monitoring',
                    'metadata': {
                        'error_rate': 0.15,
                        'baseline_rate': 0.02,
                        'affected_endpoints': ['/api/users', '/api/orders']
                    }
                },
                {
                    'title': 'Security Incident - Unauthorized Access',
                    'description': 'Multiple failed login attempts detected from suspicious IP',
                    'severity': 'critical',
                    'category': 'security',
                    'priority': 1,
                    'source': 'security_monitoring',
                    'metadata': {
                        'suspicious_ip': '192.168.1.100',
                        'attempt_count': 25,
                        'time_window_minutes': 10,
                        'affected_accounts': ['admin', 'user123']
                    }
                }
            ]
            
            created_incidents = []
            for incident_data in test_incidents:
                response = requests.post(
                    f"{self.base_url}/api/incident_response",
                    json=incident_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 201:
                    incident = response.json().get('incident', {})
                    created_incidents.append(incident)
                    self.incident_ids.append(incident.get('incident_id'))
                else:
                    self.log_test_result(
                        f"Create Incident: {incident_data['title']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            
            # Test successful creation
            self.log_test_result(
                "Incident Creation",
                len(created_incidents) == len(test_incidents),
                f"Created {len(created_incidents)} incidents",
                {'incident_ids': [inc.get('incident_id') for inc in created_incidents]}
            )
            
            return len(created_incidents) == len(test_incidents)
            
        except Exception as e:
            self.log_test_result("Incident Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_incident_retrieval(self) -> bool:
        """Test retrieving incidents."""
        print("🧪 Testing Incident Retrieval...")
        
        try:
            # Test get all incidents
            response = requests.get(f"{self.base_url}/api/incident_response")
            
            if response.status_code == 200:
                data = response.json()
                incidents = data.get('incidents', [])
                
                self.log_test_result(
                    "Get All Incidents",
                    True,
                    f"Retrieved {len(incidents)} incidents",
                    {'total': len(incidents)}
                )
                
                # Test get specific incident
                if incidents:
                    incident_id = incidents[0].get('incident_id')
                    response = requests.get(f"{self.base_url}/api/incident_response/{incident_id}")
                    
                    if response.status_code == 200:
                        incident_data = response.json().get('incident', {})
                        self.log_test_result(
                            "Get Specific Incident",
                            True,
                            f"Retrieved incident {incident_id}",
                            {'incident_id': incident_id}
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Get Specific Incident",
                            False,
                            f"HTTP {response.status_code}: {response.text}"
                        )
                        return False
                else:
                    self.log_test_result("Get Specific Incident", False, "No incidents to retrieve")
                    return False
            else:
                self.log_test_result("Get All Incidents", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("Incident Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_alert_processing(self) -> bool:
        """Test alert processing and correlation."""
        print("🧪 Testing Alert Processing...")
        
        try:
            # Test alert data
            test_alerts = [
                {
                    'title': 'Database Connection Timeout',
                    'description': 'Database connection timeout after 30 seconds',
                    'severity': 'critical',
                    'category': 'system',
                    'source': 'monitoring',
                    'correlation_id': 'db-conn-001',
                    'metadata': {
                        'database': 'postgresql',
                        'timeout_seconds': 30,
                        'connection_pool_size': 10
                    }
                },
                {
                    'title': 'High Memory Usage',
                    'description': 'Memory usage exceeded 90% threshold',
                    'severity': 'high',
                    'category': 'performance',
                    'source': 'monitoring',
                    'correlation_id': 'memory-001',
                    'metadata': {
                        'memory_usage_percent': 92,
                        'threshold_percent': 90,
                        'server': 'web-server-01'
                    }
                },
                {
                    'title': 'Failed Login Attempts',
                    'description': 'Multiple failed login attempts detected',
                    'severity': 'medium',
                    'category': 'security',
                    'source': 'security_monitoring',
                    'correlation_id': 'security-001',
                    'metadata': {
                        'attempt_count': 5,
                        'ip_address': '192.168.1.100',
                        'username': 'admin'
                    }
                }
            ]
            
            processed_alerts = []
            for alert_data in test_alerts:
                response = requests.post(
                    f"{self.base_url}/api/alerting/send",
                    json=alert_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json().get('result', {})
                    processed_alerts.append(result)
                    self.alert_ids.append(result.get('alert_id'))
                else:
                    self.log_test_result(
                        f"Process Alert: {alert_data['title']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            
            # Test successful processing
            self.log_test_result(
                "Alert Processing",
                len(processed_alerts) == len(test_alerts),
                f"Processed {len(processed_alerts)} alerts",
                {'alert_ids': [alert.get('alert_id') for alert in processed_alerts]}
            )
            
            return len(processed_alerts) == len(test_alerts)
            
        except Exception as e:
            self.log_test_result("Alert Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_incident_from_alert(self) -> bool:
        """Test creating incidents from alerts."""
        print("🧪 Testing Incident Creation from Alert...")
        
        try:
            # Create a critical alert
            critical_alert = {
                'alert': {
                    'alert_id': str(uuid.uuid4()),
                    'title': 'Critical System Failure',
                    'description': 'Complete system failure detected across multiple services',
                    'severity': 'critical',
                    'category': 'system',
                    'source': 'monitoring',
                    'log_entries': [12345, 12346, 12347],
                    'correlation_id': 'system-failure-001',
                    'triggered_at': datetime.now(timezone.utc).isoformat()
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/incident_response/from-alert",
                json=critical_alert,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                data = response.json()
                incident = data.get('incident', {})
                escalation_actions = data.get('escalation_actions', [])
                playbook = data.get('response_playbook', {})
                
                self.log_test_result(
                    "Incident from Alert",
                    True,
                    f"Created incident {incident.get('incident_id')} with {len(escalation_actions)} escalation actions",
                    {
                        'incident_id': incident.get('incident_id'),
                        'escalation_actions': len(escalation_actions),
                        'playbook': playbook.get('title', 'No playbook')
                    }
                )
                
                self.incident_ids.append(incident.get('incident_id'))
                return True
            else:
                self.log_test_result(
                    "Incident from Alert",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Incident from Alert", False, f"Exception: {str(e)}")
            return False
    
    def test_escalation_workflows(self) -> bool:
        """Test escalation workflows."""
        print("🧪 Testing Escalation Workflows...")
        
        try:
            # Test escalation rules
            response = requests.get(f"{self.base_url}/api/incident_response/escalation-rules")
            
            if response.status_code == 200:
                data = response.json()
                rules = data.get('escalation_rules', [])
                
                self.log_test_result(
                    "Get Escalation Rules",
                    len(rules) > 0,
                    f"Retrieved {len(rules)} escalation rules",
                    {'rules_count': len(rules)}
                )
                
                # Test manual escalation
                if self.incident_ids:
                    incident_id = self.incident_ids[0]
                    escalation_data = {
                        'incident_id': incident_id,
                        'escalation_level': 2,
                        'escalate_to': 'engineering_manager',
                        'reason': 'Critical issue requires immediate attention'
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/api/incident_response/escalate",
                        json=escalation_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        escalation_result = response.json().get('escalation', {})
                        self.log_test_result(
                            "Manual Escalation",
                            True,
                            f"Escalated incident {incident_id}",
                            {'escalation_level': escalation_result.get('escalation_level')}
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Manual Escalation",
                            False,
                            f"HTTP {response.status_code}: {response.text}"
                        )
                        return False
                else:
                    self.log_test_result("Manual Escalation", False, "No incidents available for escalation")
                    return False
            else:
                self.log_test_result("Get Escalation Rules", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("Escalation Workflows", False, f"Exception: {str(e)}")
            return False
    
    def test_response_playbooks(self) -> bool:
        """Test response playbooks."""
        print("🧪 Testing Response Playbooks...")
        
        try:
            response = requests.get(f"{self.base_url}/api/incident_response/playbooks")
            
            if response.status_code == 200:
                data = response.json()
                playbooks = data.get('playbooks', {})
                
                self.log_test_result(
                    "Get Response Playbooks",
                    len(playbooks) > 0,
                    f"Retrieved {len(playbooks)} playbooks",
                    {'playbooks': list(playbooks.keys())}
                )
                
                return len(playbooks) > 0
            else:
                self.log_test_result("Get Response Playbooks", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("Response Playbooks", False, f"Exception: {str(e)}")
            return False
    
    def test_alert_rules(self) -> bool:
        """Test alert rules."""
        print("🧪 Testing Alert Rules...")
        
        try:
            response = requests.get(f"{self.base_url}/api/alerting/rules")
            
            if response.status_code == 200:
                data = response.json()
                rules = data.get('alert_rules', [])
                
                self.log_test_result(
                    "Get Alert Rules",
                    len(rules) > 0,
                    f"Retrieved {len(rules)} alert rules",
                    {'rules_count': len(rules)}
                )
                
                return len(rules) > 0
            else:
                self.log_test_result("Get Alert Rules", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("Alert Rules", False, f"Exception: {str(e)}")
            return False
    
    def test_notification_templates(self) -> bool:
        """Test notification templates."""
        print("🧪 Testing Notification Templates...")
        
        try:
            response = requests.get(f"{self.base_url}/api/alerting/templates")
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('templates', [])
                
                self.log_test_result(
                    "Get Notification Templates",
                    len(templates) > 0,
                    f"Retrieved {len(templates)} templates",
                    {'template_channels': list(set(t.get('channel') for t in templates))}
                )
                
                return len(templates) > 0
            else:
                self.log_test_result("Get Notification Templates", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test_result("Notification Templates", False, f"Exception: {str(e)}")
            return False
    
    def test_alert_correlation(self) -> bool:
        """Test alert correlation and deduplication."""
        print("🧪 Testing Alert Correlation...")
        
        try:
            # Send multiple alerts with same correlation ID
            correlation_id = f"test-correlation-{uuid.uuid4().hex[:8]}"
            
            alerts = [
                {
                    'title': 'First Alert',
                    'description': 'First alert in correlation group',
                    'severity': 'high',
                    'category': 'system',
                    'correlation_id': correlation_id
                },
                {
                    'title': 'Second Alert',
                    'description': 'Second alert in correlation group',
                    'severity': 'critical',
                    'category': 'system',
                    'correlation_id': correlation_id
                }
            ]
            
            results = []
            for alert in alerts:
                response = requests.post(
                    f"{self.base_url}/api/alerting/send",
                    json=alert,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json().get('result', {})
                    results.append(result)
                else:
                    self.log_test_result(
                        f"Alert Correlation: {alert['title']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            
            # Check correlation results
            correlation_actions = [r.get('correlation_result', {}).get('action') for r in results]
            
            self.log_test_result(
                "Alert Correlation",
                'create_new' in correlation_actions and 'update_existing' in correlation_actions,
                f"Correlation actions: {correlation_actions}",
                {'correlation_id': correlation_id, 'actions': correlation_actions}
            )
            
            return len(results) == 2
            
        except Exception as e:
            self.log_test_result("Alert Correlation", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_alert_processing(self) -> bool:
        """Test bulk alert processing."""
        print("🧪 Testing Bulk Alert Processing...")
        
        try:
            bulk_alerts = [
                {
                    'title': 'Bulk Alert 1',
                    'description': 'First bulk alert',
                    'severity': 'medium',
                    'category': 'system'
                },
                {
                    'title': 'Bulk Alert 2',
                    'description': 'Second bulk alert',
                    'severity': 'high',
                    'category': 'performance'
                },
                {
                    'title': 'Bulk Alert 3',
                    'description': 'Third bulk alert',
                    'severity': 'low',
                    'category': 'business'
                }
            ]
            
            response = requests.post(
                f"{self.base_url}/api/alerting/bulk",
                json={'alerts': bulk_alerts},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                summary = data.get('summary', {})
                
                self.log_test_result(
                    "Bulk Alert Processing",
                    summary.get('successful', 0) == len(bulk_alerts),
                    f"Processed {summary.get('successful', 0)}/{summary.get('total', 0)} alerts successfully",
                    summary
                )
                
                return summary.get('successful', 0) == len(bulk_alerts)
            else:
                self.log_test_result(
                    "Bulk Alert Processing",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Bulk Alert Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_incident_updates(self) -> bool:
        """Test incident updates."""
        print("🧪 Testing Incident Updates...")
        
        try:
            if not self.incident_ids:
                self.log_test_result("Incident Updates", False, "No incidents available for update")
                return False
            
            incident_id = self.incident_ids[0]
            update_data = {
                'status': 'acknowledged',
                'assigned_team': 'senior_engineers',
                'severity': 'high'
            }
            
            response = requests.put(
                f"{self.base_url}/api/incident_response/{incident_id}",
                json=update_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                updated_incident = response.json().get('incident', {})
                self.log_test_result(
                    "Incident Updates",
                    True,
                    f"Updated incident {incident_id}",
                    {'updated_fields': list(update_data.keys())}
                )
                return True
            else:
                self.log_test_result(
                    "Incident Updates",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Incident Updates", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary."""
        print("🚀 Starting Day 24: Automated Incident Response System Testing")
        print("=" * 80)
        print()
        
        # Test execution order
        tests = [
            ("Incident Creation", self.test_incident_creation),
            ("Incident Retrieval", self.test_incident_retrieval),
            ("Alert Processing", self.test_alert_processing),
            ("Incident from Alert", self.test_incident_from_alert),
            ("Escalation Workflows", self.test_escalation_workflows),
            ("Response Playbooks", self.test_response_playbooks),
            ("Alert Rules", self.test_alert_rules),
            ("Notification Templates", self.test_notification_templates),
            ("Alert Correlation", self.test_alert_correlation),
            ("Bulk Alert Processing", self.test_bulk_alert_processing),
            ("Incident Updates", self.test_incident_updates)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test_result(test_name, False, f"Test execution error: {str(e)}")
        
        # Generate summary
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'test_results': self.test_results,
            'created_incidents': len(self.incident_ids),
            'processed_alerts': len(self.alert_ids)
        }
        
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Created Incidents: {summary['created_incidents']}")
        print(f"Processed Alerts: {summary['processed_alerts']}")
        print()
        
        if summary['success_rate'] >= 90:
            print("🎉 EXCELLENT! Incident Response System is working perfectly!")
        elif summary['success_rate'] >= 75:
            print("✅ GOOD! Incident Response System is mostly working well.")
        elif summary['success_rate'] >= 50:
            print("⚠️  FAIR! Some issues need to be addressed.")
        else:
            print("❌ POOR! Significant issues need to be fixed.")
        
        return summary


def main():
    """Main test execution."""
    # Test against local development server
    tester = IncidentResponseTester("http://localhost:3000")
    
    try:
        summary = tester.run_all_tests()
        
        # Save results
        with open('day24_test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📁 Test results saved to: day24_test_results.json")
        
        return summary['success_rate'] >= 75
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
