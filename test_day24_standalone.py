"""
Day 24: Standalone Incident Response System Testing

This script tests the incident response and alerting systems without requiring a running server.
It directly imports and tests the core functionality.
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
try:
    from api.incident_response import IncidentResponseSystem, Incident, EscalationRule
    from api.alerting import AlertingSystem, NotificationService, AlertCorrelationEngine
    print("✅ Successfully imported incident response and alerting modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class StandaloneTester:
    """Standalone test suite for incident response and alerting systems."""
    
    def __init__(self):
        self.test_results = []
        self.incident_system = IncidentResponseSystem()
        self.alerting_system = AlertingSystem()
    
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
            # Test incident data
            incident_data = {
                'title': 'Database Connection Failure',
                'description': 'Multiple database connection timeouts detected',
                'severity': 'critical',
                'category': 'database',
                'source': 'automated'
            }
            
            # Create incident
            incident = Incident(
                title=incident_data['title'],
                description=incident_data['description'],
                severity=incident_data['severity'],
                category=incident_data['category'],
                source=incident_data['source']
            )
            
            # Validate incident
            validation_errors = incident.validate()
            
            self.log_test_result(
                "Incident Creation",
                len(validation_errors) == 0,
                f"Created incident {incident.incident_id}",
                {
                    'incident_id': incident.incident_id,
                    'validation_errors': validation_errors,
                    'severity': incident.severity,
                    'status': incident.status
                }
            )
            
            return len(validation_errors) == 0
            
        except Exception as e:
            self.log_test_result("Incident Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_escalation_rules(self) -> bool:
        """Test escalation rules."""
        print("🧪 Testing Escalation Rules...")
        
        try:
            # Get escalation rules
            rules = self.incident_system.escalation_rules
            
            self.log_test_result(
                "Escalation Rules",
                len(rules) > 0,
                f"Found {len(rules)} escalation rules",
                {
                    'rules_count': len(rules),
                    'rule_conditions': [rule.condition for rule in rules]
                }
            )
            
            # Test rule evaluation
            test_incident = Incident(
                title="Test Critical Incident",
                description="Test incident for escalation",
                severity="critical",
                category="system"
            )
            
            escalation_actions = self.incident_system.check_escalation(test_incident)
            
            self.log_test_result(
                "Escalation Evaluation",
                len(escalation_actions) > 0,
                f"Found {len(escalation_actions)} escalation actions",
                {
                    'escalation_actions': len(escalation_actions),
                    'actions': escalation_actions
                }
            )
            
            return len(rules) > 0 and len(escalation_actions) > 0
            
        except Exception as e:
            self.log_test_result("Escalation Rules", False, f"Exception: {str(e)}")
            return False
    
    def test_response_playbooks(self) -> bool:
        """Test response playbooks."""
        print("🧪 Testing Response Playbooks...")
        
        try:
            # Test playbook retrieval
            test_incident = Incident(
                title="Database Connection Failure",
                description="Database connection issues",
                severity="critical",
                category="database"
            )
            
            playbook = self.incident_system.get_response_playbook(test_incident)
            
            self.log_test_result(
                "Response Playbooks",
                playbook is not None,
                f"Retrieved playbook: {playbook.get('title', 'Unknown')}",
                {
                    'playbook_title': playbook.get('title'),
                    'steps_count': len(playbook.get('steps', [])),
                    'estimated_duration': playbook.get('estimated_duration_minutes')
                }
            )
            
            return playbook is not None
            
        except Exception as e:
            self.log_test_result("Response Playbooks", False, f"Exception: {str(e)}")
            return False
    
    def test_alert_processing(self) -> bool:
        """Test alert processing."""
        print("🧪 Testing Alert Processing...")
        
        try:
            # Test alert data
            alert_data = {
                'title': 'Database Connection Timeout',
                'description': 'Database connection timeout after 30 seconds',
                'severity': 'critical',
                'category': 'system',
                'source': 'monitoring',
                'correlation_id': 'test-correlation-001'
            }
            
            # Process alert
            result = self.alerting_system.process_alert(alert_data)
            
            self.log_test_result(
                "Alert Processing",
                result.get('success', False),
                f"Processed alert {result.get('alert_id', 'Unknown')}",
                {
                    'success': result.get('success'),
                    'alert_id': result.get('alert_id'),
                    'correlation_result': result.get('correlation_result', {}).get('action'),
                    'notifications_sent': len(result.get('notifications_sent', []))
                }
            )
            
            return result.get('success', False)
            
        except Exception as e:
            self.log_test_result("Alert Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_alert_correlation(self) -> bool:
        """Test alert correlation."""
        print("🧪 Testing Alert Correlation...")
        
        try:
            # Create correlation engine
            correlation_engine = AlertCorrelationEngine()
            
            # Test correlation ID
            correlation_id = 'test-correlation-002'
            
            # First alert
            alert1 = {
                'alert_id': 'alert-001',
                'correlation_id': correlation_id,
                'severity': 'high',
                'category': 'system'
            }
            
            result1 = correlation_engine.correlate_alert(alert1)
            
            # Second alert with same correlation ID
            alert2 = {
                'alert_id': 'alert-002',
                'correlation_id': correlation_id,
                'severity': 'critical',
                'category': 'system'
            }
            
            result2 = correlation_engine.correlate_alert(alert2)
            
            # Check correlation results
            action1 = result1.get('action')
            action2 = result2.get('action')
            
            self.log_test_result(
                "Alert Correlation",
                action1 == 'create_new' and action2 == 'update_existing',
                f"Correlation actions: {action1}, {action2}",
                {
                    'first_alert_action': action1,
                    'second_alert_action': action2,
                    'correlation_id': correlation_id
                }
            )
            
            return action1 == 'create_new' and action2 == 'update_existing'
            
        except Exception as e:
            self.log_test_result("Alert Correlation", False, f"Exception: {str(e)}")
            return False
    
    def test_notification_service(self) -> bool:
        """Test notification service."""
        print("🧪 Testing Notification Service...")
        
        try:
            # Create notification service
            notification_service = NotificationService()
            
            # Test notification data
            notification_data = {
                'title': 'Test Alert',
                'description': 'This is a test alert',
                'severity': 'critical',
                'category': 'system',
                'source': 'test',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'alert_id': 'test-alert-001',
                'dashboard_url': 'http://localhost:3000/dashboard'
            }
            
            # Test email notification
            email_result = notification_service.send_notification(
                'critical_alert_email',
                notification_data,
                ['test@example.com']
            )
            
            # Test Slack notification
            slack_result = notification_service.send_notification(
                'high_alert_slack',
                notification_data
            )
            
            email_success = email_result.get('success', False)
            slack_success = slack_result.get('success', False)
            
            self.log_test_result(
                "Notification Service",
                email_success and slack_success,
                f"Email: {email_success}, Slack: {slack_success}",
                {
                    'email_success': email_success,
                    'slack_success': slack_success,
                    'email_channel': email_result.get('channel'),
                    'slack_channel': slack_result.get('channel')
                }
            )
            
            return email_success and slack_success
            
        except Exception as e:
            self.log_test_result("Notification Service", False, f"Exception: {str(e)}")
            return False
    
    def test_incident_from_alert(self) -> bool:
        """Test creating incident from alert."""
        print("🧪 Testing Incident from Alert...")
        
        try:
            # Test alert data
            alert_data = {
                'alert_id': 'alert-003',
                'title': 'Critical System Failure',
                'description': 'Complete system failure detected',
                'severity': 'critical',
                'category': 'system',
                'source': 'monitoring',
                'log_entries': [12345, 12346],
                'correlation_id': 'system-failure-001',
                'triggered_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Create incident from alert
            incident = self.incident_system.create_incident_from_alert(alert_data)
            
            # Check escalation
            escalation_actions = self.incident_system.check_escalation(incident)
            
            # Get playbook
            playbook = self.incident_system.get_response_playbook(incident)
            
            self.log_test_result(
                "Incident from Alert",
                incident is not None and len(escalation_actions) > 0,
                f"Created incident {incident.incident_id} with {len(escalation_actions)} escalation actions",
                {
                    'incident_id': incident.incident_id,
                    'severity': incident.severity,
                    'assigned_team': incident.assigned_team,
                    'escalation_actions': len(escalation_actions),
                    'playbook_title': playbook.get('title') if playbook else None
                }
            )
            
            return incident is not None and len(escalation_actions) > 0
            
        except Exception as e:
            self.log_test_result("Incident from Alert", False, f"Exception: {str(e)}")
            return False
    
    def test_alert_rules(self) -> bool:
        """Test alert rules."""
        print("🧪 Testing Alert Rules...")
        
        try:
            # Get alert rules
            rules = self.alerting_system.alert_rules
            
            self.log_test_result(
                "Alert Rules",
                len(rules) > 0,
                f"Found {len(rules)} alert rules",
                {
                    'rules_count': len(rules),
                    'rule_names': [rule.name for rule in rules],
                    'enabled_rules': len([rule for rule in rules if rule.enabled])
                }
            )
            
            return len(rules) > 0
            
        except Exception as e:
            self.log_test_result("Alert Rules", False, f"Exception: {str(e)}")
            return False
    
    def test_notification_templates(self) -> bool:
        """Test notification templates."""
        print("🧪 Testing Notification Templates...")
        
        try:
            # Get notification service
            notification_service = NotificationService()
            templates = notification_service.templates
            
            self.log_test_result(
                "Notification Templates",
                len(templates) > 0,
                f"Found {len(templates)} notification templates",
                {
                    'templates_count': len(templates),
                    'template_names': list(templates.keys()),
                    'channels': list(set(template.channel for template in templates.values()))
                }
            )
            
            return len(templates) > 0
            
        except Exception as e:
            self.log_test_result("Notification Templates", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary."""
        print("🚀 Starting Day 24: Standalone Incident Response System Testing")
        print("=" * 80)
        print()
        
        # Test execution order
        tests = [
            ("Incident Creation", self.test_incident_creation),
            ("Escalation Rules", self.test_escalation_rules),
            ("Response Playbooks", self.test_response_playbooks),
            ("Alert Processing", self.test_alert_processing),
            ("Alert Correlation", self.test_alert_correlation),
            ("Notification Service", self.test_notification_service),
            ("Incident from Alert", self.test_incident_from_alert),
            ("Alert Rules", self.test_alert_rules),
            ("Notification Templates", self.test_notification_templates)
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
            'test_results': self.test_results
        }
        
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
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
    tester = StandaloneTester()
    
    try:
        summary = tester.run_all_tests()
        
        # Save results
        with open('day24_standalone_test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📁 Test results saved to: day24_standalone_test_results.json")
        
        return summary['success_rate'] >= 75
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
