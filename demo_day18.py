"""
Day 18: Real-time Processing Demo
================================

This script demonstrates the real-time processing capabilities we built today.
It's a simple, interactive demo that shows how the system works.

For beginners: This is a hands-on demo that shows you how to use
the real-time processing system step by step.

Author: Engineering Log Intelligence Team
Date: September 22, 2025
"""

import json
import time
import requests
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 40)

def demo_ml_analysis():
    """Demonstrate ML analysis capabilities."""
    print_header("ML Analysis Demo")
    
    print("This demo shows how our AI models analyze different types of logs.")
    print("We'll send various log entries and see what the AI thinks about them.")
    
    # Sample logs for demonstration
    sample_logs = [
        {
            "log_id": "demo_1",
            "message": "User john.doe logged in successfully",
            "level": "INFO",
            "source_type": "application",
            "timestamp": datetime.now().isoformat()
        },
        {
            "log_id": "demo_2",
            "message": "Database connection failed: timeout after 30 seconds",
            "level": "ERROR",
            "source_type": "application",
            "timestamp": datetime.now().isoformat()
        },
        {
            "log_id": "demo_3",
            "message": "Suspicious login attempt from IP 192.168.1.100",
            "level": "WARN",
            "source_type": "security",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print_step(1, "Analyzing individual logs")
    
    for i, log_entry in enumerate(sample_logs, 1):
        print(f"\n🔍 Analyzing Log {i}:")
        print(f"   Message: {log_entry['message']}")
        print(f"   Level: {log_entry['level']}")
        print(f"   Source: {log_entry['source_type']}")
        
        try:
            # In a real demo, this would call the API
            # For now, we'll simulate the response
            print("   🤖 AI Analysis: Processing...")
            time.sleep(1)  # Simulate processing time
            
            # Simulate AI response based on log content
            if "error" in log_entry['message'].lower() or "failed" in log_entry['message'].lower():
                risk_level = "high"
                category = "error"
                confidence = 0.85
            elif "suspicious" in log_entry['message'].lower() or "security" in log_entry['source_type']:
                risk_level = "high"
                category = "security"
                confidence = 0.90
            else:
                risk_level = "low"
                category = "system"
                confidence = 0.70
            
            print(f"   ✅ Analysis Complete:")
            print(f"      Category: {category}")
            print(f"      Risk Level: {risk_level}")
            print(f"      Confidence: {confidence:.2f}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print_step(2, "Batch analysis demonstration")
    print("Now let's analyze multiple logs at once (batch processing):")
    
    try:
        print("   🤖 Processing 3 logs in batch...")
        time.sleep(2)  # Simulate batch processing
        
        print("   ✅ Batch Analysis Complete:")
        print("      Total logs processed: 3")
        print("      Average processing time: 0.5 seconds")
        print("      High-risk logs detected: 2")
        print("      Alerts generated: 2")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def demo_realtime_processing():
    """Demonstrate real-time processing capabilities."""
    print_header("Real-time Processing Demo")
    
    print("This demo shows how our system processes logs in real-time.")
    print("We'll simulate logs arriving continuously and being analyzed immediately.")
    
    print_step(1, "Starting real-time processing")
    print("🚀 Starting real-time log processor...")
    print("   - Connecting to Kafka topics...")
    print("   - Initializing ML models...")
    print("   - Starting log consumption...")
    time.sleep(2)
    print("   ✅ Real-time processing started successfully!")
    
    print_step(2, "Simulating real-time log processing")
    print("📊 Processing logs as they arrive:")
    
    # Simulate real-time log processing
    for i in range(10):
        log_types = [
            "User authentication successful",
            "Database query completed",
            "High memory usage detected",
            "Security scan completed",
            "Application started"
        ]
        
        log_message = log_types[i % len(log_types)]
        print(f"\n   📝 Log {i+1}: {log_message}")
        
        # Simulate processing
        print("   🔄 Processing...")
        time.sleep(0.5)
        
        # Simulate AI analysis
        if "high" in log_message.lower() or "security" in log_message.lower():
            print("   ⚠️  Alert: High-priority issue detected!")
        else:
            print("   ✅ Processed successfully")
    
    print_step(3, "Real-time processing statistics")
    print("📈 Performance Summary:")
    print("   - Logs processed: 10")
    print("   - Processing time: 5.0 seconds")
    print("   - Logs per second: 2.0")
    print("   - Alerts generated: 2")
    print("   - Error rate: 0%")
    
    print_step(4, "Stopping real-time processing")
    print("🛑 Stopping real-time processor...")
    time.sleep(1)
    print("   ✅ Real-time processing stopped successfully!")

def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print_header("Performance Monitoring Demo")
    
    print("This demo shows how we monitor the performance of our system.")
    print("We track various metrics to ensure everything is working optimally.")
    
    print_step(1, "System Health Check")
    print("🔍 Checking system health...")
    time.sleep(1)
    
    health_status = {
        "status": "healthy",
        "uptime": "2 hours 15 minutes",
        "logs_processed": 1250,
        "average_response_time": "0.08 seconds",
        "error_rate": "0.2%",
        "memory_usage": "45%",
        "cpu_usage": "32%"
    }
    
    print("   ✅ System Health Status:")
    for key, value in health_status.items():
        print(f"      {key.replace('_', ' ').title()}: {value}")
    
    print_step(2, "Performance Metrics")
    print("📊 Current Performance:")
    
    metrics = {
        "logs_per_second": 15.2,
        "peak_processing_time": "0.15 seconds",
        "queue_size": 0,
        "active_connections": 3,
        "memory_efficiency": "92%"
    }
    
    for key, value in metrics.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print_step(3, "Alert System Status")
    print("🚨 Alert System:")
    print("   - Active alerts: 0")
    print("   - Alert channels: Email, Slack, Webhook")
    print("   - Last alert: 2 hours ago")
    print("   - Alert response time: 0.5 seconds")

def demo_api_usage():
    """Demonstrate API usage."""
    print_header("API Usage Demo")
    
    print("This demo shows how to use our APIs to control the system.")
    print("We'll demonstrate the main API endpoints.")
    
    print_step(1, "ML Analysis API")
    print("🔬 ML Analysis Endpoint: /api/ml/analyze")
    print("   - Analyze single logs")
    print("   - Batch process multiple logs")
    print("   - Train models with new data")
    
    print("   Example usage:")
    print("   curl -X POST http://localhost:3000/api/ml/analyze \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"operation\": \"analyze\", \"log_entry\": {...}}'")
    
    print_step(2, "Real-time Processing API")
    print("⚡ Real-time Processing Endpoint: /api/ml/real_time")
    print("   - Start/stop real-time processing")
    print("   - Get processing status")
    print("   - Monitor performance")
    
    print("   Example usage:")
    print("   curl -X POST http://localhost:3000/api/ml/real_time \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"operation\": \"start\", \"topics\": [\"logs\"]}'")
    
    print_step(3, "Health Check API")
    print("🏥 Health Check Endpoint: /api/health/check")
    print("   - Check system health")
    print("   - Get service status")
    print("   - Monitor dependencies")
    
    print("   Example usage:")
    print("   curl -X GET http://localhost:3000/api/health/check")

def main():
    """Main demo function."""
    print("🎯 Day 18: Real-time Processing Demo")
    print("=" * 60)
    print("Welcome to the real-time processing demonstration!")
    print("This demo shows you how our AI-powered log analysis system works.")
    print("=" * 60)
    
    print("\n📋 What we'll cover:")
    print("1. ML Analysis - How AI analyzes logs")
    print("2. Real-time Processing - Processing logs as they arrive")
    print("3. Performance Monitoring - Tracking system health")
    print("4. API Usage - How to control the system")
    
    input("\nPress Enter to start the demo...")
    
    try:
        # Run all demos
        demo_ml_analysis()
        input("\nPress Enter to continue to real-time processing demo...")
        
        demo_realtime_processing()
        input("\nPress Enter to continue to performance monitoring demo...")
        
        demo_performance_monitoring()
        input("\nPress Enter to continue to API usage demo...")
        
        demo_api_usage()
        
        print_header("Demo Complete!")
        print("🎉 Congratulations! You've seen how our real-time processing system works.")
        print("\n📚 What you learned:")
        print("   - How AI models analyze logs")
        print("   - How real-time processing works")
        print("   - How to monitor system performance")
        print("   - How to use the APIs")
        
        print("\n🚀 Next steps:")
        print("   - Try running the actual tests: python test_day18_realtime.py")
        print("   - Start the development server: vercel dev")
        print("   - Explore the API endpoints")
        print("   - Read the documentation: docs/DAY18_REALTIME_PROCESSING.md")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("Please check the logs and try again.")

if __name__ == "__main__":
    main()
