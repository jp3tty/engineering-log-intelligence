"""
ML Analysis API Endpoint
========================

This Vercel Function provides ML analysis capabilities for log entries.
It uses our trained models to classify logs and detect anomalies.

For beginners: This is an API endpoint that other parts of our system
can call to get AI analysis of log entries.

Author: Engineering Log Intelligence Team
Date: September 21, 2025
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ML service
ml_service = MLService(model_storage_path="models/")

def handler(request):
    """
    Main handler for the ML analysis API endpoint.
    
    For beginners: This function receives HTTP requests and processes them
    using our AI models, then sends back the results.
    
    Args:
        request: HTTP request object
        
    Returns:
        HTTP response with analysis results
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
        
        # Initialize ML service if not already done
        if not ml_service.is_initialized:
            ml_service.initialize_models()
        
        # Route requests based on method and path
        if request.method == 'GET':
            return handle_get_request(request, headers)
        elif request.method == 'POST':
            return handle_post_request(request, headers)
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        logger.error(f"Error in ML analysis handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def handle_get_request(request, headers):
    """
    Handle GET requests to the ML analysis endpoint.
    
    For beginners: GET requests are used to get information, like checking
    if our AI models are working properly.
    """
    try:
        # Get service status
        status = ml_service.get_service_status()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'ML Analysis Service Status',
                'status': status,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error handling GET request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error getting service status',
                'message': str(e)
            })
        }

def handle_post_request(request, headers):
    """
    Handle POST requests to the ML analysis endpoint.
    
    For beginners: POST requests are used to send data for processing,
    like sending log entries to be analyzed by our AI models.
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
        operation = data.get('operation', 'analyze')
        
        if operation == 'analyze':
            return handle_analyze_request(data, headers)
        elif operation == 'train':
            return handle_train_request(data, headers)
        elif operation == 'batch_analyze':
            return handle_batch_analyze_request(data, headers)
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid operation',
                    'supported_operations': ['analyze', 'train', 'batch_analyze']
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

def handle_analyze_request(data, headers):
    """
    Handle single log analysis requests.
    
    For beginners: This analyzes one log entry at a time using our AI models.
    """
    try:
        log_entry = data.get('log_entry')
        if not log_entry:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing log_entry in request body'
                })
            }
        
        # Analyze the log entry
        analysis = ml_service.analyze_log(log_entry)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Log analysis completed',
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error analyzing log: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error analyzing log entry',
                'message': str(e)
            })
        }

def handle_batch_analyze_request(data, headers):
    """
    Handle batch log analysis requests.
    
    For beginners: This analyzes multiple log entries at once, which is
    more efficient than analyzing them one by one.
    """
    try:
        log_entries = data.get('log_entries', [])
        if not log_entries:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing log_entries in request body'
                })
            }
        
        if len(log_entries) > 100:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Too many log entries. Maximum 100 per batch.'
                })
            }
        
        # Analyze all log entries
        analyses = ml_service.analyze_logs_batch(log_entries)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': f'Batch analysis completed for {len(analyses)} logs',
                'analyses': analyses,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error in batch analysis',
                'message': str(e)
            })
        }

def handle_train_request(data, headers):
    """
    Handle model training requests.
    
    For beginners: This teaches our AI models by showing them lots of
    examples of logs and what they should do with them.
    """
    try:
        training_data = data.get('training_data', [])
        if not training_data:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing training_data in request body'
                })
            }
        
        # Train the models
        training_results = ml_service.train_all_models(training_data)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Model training completed',
                'results': training_results,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error training models',
                'message': str(e)
            })
        }

# For Vercel Functions, we need to export the handler
def main(request):
    """Main entry point for Vercel Functions."""
    return handler(request)
