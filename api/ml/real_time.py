"""
Real-time ML Processing API Endpoint
====================================

This Vercel Function provides real-time ML processing capabilities.
It can start, stop, and monitor real-time log analysis.

For beginners: This is an API endpoint that lets us start and stop
real-time log analysis, and check how it's performing.

Author: Engineering Log Intelligence Team
Date: September 22, 2025
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from external_services.ml.ml_service import MLService
from external_services.ml.real_time_processor import RealTimeProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global processor instance (in production, this would be managed differently)
processor = None
ml_service = None

def initialize_services():
    """Initialize ML service and processor."""
    global ml_service, processor
    
    if ml_service is None:
        ml_service = MLService(model_storage_path="models/")
        ml_service.initialize_models()
    
    if processor is None:
        # Kafka configuration (in production, this would come from environment variables)
        kafka_config = {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'group_id': 'log_intelligence_realtime',
            'auto_offset_reset': 'latest'
        }
        processor = RealTimeProcessor(kafka_config, ml_service)
        
        # Add alert callback
        processor.add_callback(handle_alert)
    
    return ml_service, processor

def handle_alert(analysis_result: Dict):
    """
    Handle alerts from real-time processing.
    
    For beginners: This function is called whenever our AI detects
    something important in the logs that needs attention.
    """
    if analysis_result.get('alert_triggered', False):
        alert_level = analysis_result.get('alert_level', 'low')
        log_id = analysis_result.get('log_id', 'unknown')
        
        logger.warning(f"ALERT [{alert_level.upper()}]: {log_id}")
        
        # In a real system, this would send notifications, create tickets, etc.
        # For now, we'll just log the alert
        logger.info(f"Alert details: {json.dumps(analysis_result, indent=2)}")

def handler(request):
    """
    Main handler for the real-time ML processing API endpoint.
    
    For beginners: This function receives HTTP requests and handles
    real-time processing operations.
    
    Args:
        request: HTTP request object
        
    Returns:
        HTTP response with operation results
    """
    try:
        # Set CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Content-Type': 'application/json'
        }
        
        # Handle preflight requests
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight successful'})
            }
        
        # Initialize services
        ml_service, processor = initialize_services()
        
        # Route requests based on method and path
        if request.method == 'GET':
            return handle_get_request(request, headers, processor)
        elif request.method == 'POST':
            return handle_post_request(request, headers, processor)
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        logger.error(f"Error in real-time handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def handle_get_request(request, headers, processor):
    """
    Handle GET requests to the real-time endpoint.
    
    For beginners: GET requests are used to get information about
    the real-time processing status.
    """
    try:
        # Get processing statistics
        stats = processor.get_processing_stats()
        health = processor.get_health_status()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Real-time Processing Status',
                'stats': stats,
                'health': health,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error handling GET request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error getting processing status',
                'message': str(e)
            })
        }

def handle_post_request(request, headers, processor):
    """
    Handle POST requests to the real-time endpoint.
    
    For beginners: POST requests are used to control the real-time
    processing (start, stop, etc.).
    """
    try:
        # Parse request body
        if hasattr(request, 'body'):
            body = request.body
        else:
            body = request.get('body', '{}')
        
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        # Determine the operation type
        operation = data.get('operation', 'status')
        
        if operation == 'start':
            return handle_start_processing(data, headers, processor)
        elif operation == 'stop':
            return handle_stop_processing(data, headers, processor)
        elif operation == 'status':
            return handle_get_status(data, headers, processor)
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid operation',
                    'supported_operations': ['start', 'stop', 'status']
                })
            }
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Invalid JSON in request body',
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error handling POST request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error processing request',
                'message': str(e)
            })
        }

def handle_start_processing(data, headers, processor):
    """
    Handle start processing requests.
    
    For beginners: This starts the real-time log analysis.
    """
    try:
        topics = data.get('topics', ['logs'])
        
        if processor.is_running:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Processing is already running',
                    'current_stats': processor.get_processing_stats()
                })
            }
        
        # Start processing (in a real implementation, this would be async)
        logger.info(f"Starting real-time processing for topics: {topics}")
        
        # For demonstration, we'll simulate starting
        processor.is_running = True
        processor.stats.start_time = datetime.now()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Real-time processing started',
                'topics': topics,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error starting processing: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error starting processing',
                'message': str(e)
            })
        }

def handle_stop_processing(data, headers, processor):
    """
    Handle stop processing requests.
    
    For beginners: This stops the real-time log analysis.
    """
    try:
        if not processor.is_running:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Processing is not running'
                })
            }
        
        # Stop processing
        processor.stop_processing()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Real-time processing stopped',
                'final_stats': processor.get_processing_stats(),
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error stopping processing: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error stopping processing',
                'message': str(e)
            })
        }

def handle_get_status(data, headers, processor):
    """
    Handle status requests.
    
    For beginners: This gets detailed information about the current
    processing status and health.
    """
    try:
        stats = processor.get_processing_stats()
        health = processor.get_health_status()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Real-time Processing Status',
                'stats': stats,
                'health': health,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error getting status',
                'message': str(e)
            })
        }

# For Vercel Functions, we need to export the handler
def main(request):
    """Main entry point for Vercel Functions."""
    return handler(request)
