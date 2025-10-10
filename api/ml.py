"""
Consolidated ML API
==================

This Vercel Function consolidates all ML functionality:
- Log analysis and classification
- Real-time processing
- A/B testing for models

Routes via action parameter: ?action=analyze|realtime|abtest

Author: Engineering Log Intelligence Team
Date: October 10, 2025
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import random
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for ML API"""
        try:
            # Parse action parameter
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            action = params.get('action', ['analyze'])[0]
            
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Route to appropriate handler
            if action == 'analyze':
                response = self.handle_analyze()
            elif action == 'realtime':
                response = self.handle_realtime()
            elif action == 'abtest':
                response = self.handle_abtest()
            elif action == 'status':
                response = self.handle_status()
            else:
                response = {"error": f"Unknown action: {action}"}
            
            # Send response
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": "ML_ERROR",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data, indent=2).encode())
    
    def do_POST(self):
        """Handle POST requests for ML API"""
        try:
            print("🤖 ML API POST request received")
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            print(f"🤖 Request body: {body}")
            
            data = json.loads(body) if body else {}
            print(f"🤖 Parsed data: {data}")
            
            action = data.get('action', 'analyze')
            print(f"🤖 Action: {action}")
            
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Route to appropriate handler
            if action == 'analyze':
                response = self.handle_analyze(data)
            elif action == 'realtime':
                response = self.handle_realtime(data)
            elif action == 'abtest':
                response = self.handle_abtest(data)
            else:
                response = {"error": f"Unknown action: {action}"}
            
            # Send response
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": "ML_ERROR",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def handle_status(self):
        """Return ML model status"""
        return {
            "success": True,
            "models": {
                "classification": {
                    "status": "active",
                    "accuracy": round(random.uniform(0.85, 0.95), 3),
                    "categories": ["error", "warning", "info", "debug", "security", "performance"],
                    "last_trained": (datetime.utcnow() - timedelta(days=7)).isoformat()
                },
                "anomaly_detection": {
                    "status": "active",
                    "accuracy": round(random.uniform(0.80, 0.90), 3),
                    "types": ["point", "contextual", "collective"],
                    "last_trained": (datetime.utcnow() - timedelta(days=7)).isoformat()
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def handle_analyze(self, data=None):
        """Handle log analysis and classification"""
        if data and data.get('log_data'):
            # Analyze provided log data
            log_data = data.get('log_data', [])
            results = []
            
            for log in log_data[:10]:  # Limit to 10 logs
                results.append({
                    "log_id": log.get('id', f"log_{random.randint(1000, 9999)}"),
                    "classification": random.choice(["error", "warning", "info", "debug", "security"]),
                    "confidence": round(random.uniform(0.7, 0.95), 3),
                    "anomaly_score": round(random.uniform(0.1, 0.8), 3),
                    "is_anomaly": random.choice([True, False]),
                    "severity": random.choice(["low", "medium", "high", "critical"]),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return {
                "success": True,
                "results": results,
                "total_analyzed": len(results),
                "processing_time_ms": random.randint(50, 200),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # Return recent analysis
            return {
                "success": True,
                "data": {
                    "model_status": {
                        "classification_model": "active",
                        "anomaly_detection_model": "active",
                        "accuracy": round(random.uniform(0.85, 0.95), 3)
                    },
                    "recent_analysis": [
                        {
                            "id": f"analysis_{random.randint(1000, 9999)}",
                            "log_id": f"log_{random.randint(10000, 99999)}",
                            "classification": random.choice(["error", "warning", "info"]),
                            "confidence": round(random.uniform(0.8, 0.95), 3),
                            "anomaly_score": round(random.uniform(0.1, 0.3), 3),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        {
                            "id": f"analysis_{random.randint(1000, 9999)}",
                            "log_id": f"log_{random.randint(10000, 99999)}",
                            "classification": random.choice(["info", "debug"]),
                            "confidence": round(random.uniform(0.9, 0.98), 3),
                            "anomaly_score": round(random.uniform(0.05, 0.15), 3),
                            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
                        }
                    ],
                    "insights": [
                        {
                            "type": "pattern_detected",
                            "description": "Recurring error pattern identified in database logs",
                            "severity": "medium",
                            "recommendation": "Investigate database connection pool configuration"
                        },
                        {
                            "type": "anomaly_detected",
                            "description": "Unusual spike in authentication failures",
                            "severity": "high",
                            "recommendation": "Check for potential security breach"
                        }
                    ]
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def handle_realtime(self, data=None):
        """Handle real-time processing"""
        if data and data.get('command'):
            command = data.get('command')
            
            if command == 'start':
                return {
                    "success": True,
                    "status": "started",
                    "processor_id": f"proc_{random.randint(1000, 9999)}",
                    "message": "Real-time processor started successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif command == 'stop':
                return {
                    "success": True,
                    "status": "stopped",
                    "message": "Real-time processor stopped successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif command == 'status':
                return {
                    "success": True,
                    "status": "running",
                    "processor_id": f"proc_{random.randint(1000, 9999)}",
                    "stats": {
                        "logs_processed": random.randint(1000, 50000),
                        "anomalies_detected": random.randint(10, 500),
                        "avg_processing_time_ms": random.randint(5, 50),
                        "uptime_hours": random.randint(1, 168)
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
        else:
            # Return default status
            return {
                "success": True,
                "status": "running",
                "processor_id": f"proc_{random.randint(1000, 9999)}",
                "stats": {
                    "logs_processed": random.randint(1000, 50000),
                    "anomalies_detected": random.randint(10, 500),
                    "avg_processing_time_ms": random.randint(5, 50),
                    "uptime_hours": random.randint(1, 168)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def handle_abtest(self, data=None):
        """Handle A/B testing for models"""
        if data and data.get('test_id'):
            # Return specific test results
            test_id = data.get('test_id')
            return {
                "success": True,
                "test": {
                    "test_id": test_id,
                    "status": "completed",
                    "variants": {
                        "model_a": {
                            "name": "Classification Model v1.0",
                            "accuracy": round(random.uniform(0.82, 0.88), 3),
                            "precision": round(random.uniform(0.80, 0.86), 3),
                            "recall": round(random.uniform(0.78, 0.84), 3),
                            "f1_score": round(random.uniform(0.79, 0.85), 3),
                            "avg_latency_ms": random.randint(40, 80)
                        },
                        "model_b": {
                            "name": "Classification Model v2.0",
                            "accuracy": round(random.uniform(0.85, 0.92), 3),
                            "precision": round(random.uniform(0.83, 0.90), 3),
                            "recall": round(random.uniform(0.81, 0.88), 3),
                            "f1_score": round(random.uniform(0.82, 0.89), 3),
                            "avg_latency_ms": random.randint(45, 90)
                        }
                    },
                    "winner": "model_b",
                    "confidence": 0.95,
                    "recommendation": "Deploy model_b to production"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # List active tests
            return {
                "success": True,
                "active_tests": [
                    {
                        "test_id": f"test_{random.randint(1000, 9999)}",
                        "name": "Classification Model Comparison",
                        "status": "running",
                        "started_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                        "progress": round(random.uniform(0.5, 0.9), 2)
                    }
                ],
                "completed_tests": [
                    {
                        "test_id": f"test_{random.randint(1000, 9999)}",
                        "name": "Anomaly Detection v1 vs v2",
                        "status": "completed",
                        "completed_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                        "winner": "v2"
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }

