"""
A/B Testing API Endpoint
========================

This Vercel Function provides A/B testing capabilities for ML models.
It allows creating, managing, and monitoring A/B tests.

For beginners: This is an API endpoint that lets you create and manage
A/B tests to compare different AI models.

Author: Engineering Log Intelligence Team
Date: September 23, 2025
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# Import will be resolved at runtime
try:
    from external_services.ml.ab_testing import ABTestingFramework, ModelVariant, TestStatus
except ImportError:
    # Fallback for development
    ABTestingFramework = None
    ModelVariant = None
    TestStatus = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global A/B testing framework instance
ab_framework = ABTestingFramework()

def handler(request):
    """
    Main handler for the A/B testing API endpoint.
    
    For beginners: This function receives HTTP requests and handles
    A/B testing operations like creating tests and getting results.
    
    Args:
        request: HTTP request object
        
    Returns:
        HTTP response with operation results
    """
    try:
        # Set CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
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
        
        # Route requests based on method and path
        if request.method == 'GET':
            return handle_get_request(request, headers)
        elif request.method == 'POST':
            return handle_post_request(request, headers)
        elif request.method == 'PUT':
            return handle_put_request(request, headers)
        elif request.method == 'DELETE':
            return handle_delete_request(request, headers)
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        logger.error(f"Error in A/B testing handler: {str(e)}")
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
    Handle GET requests to the A/B testing endpoint.
    
    For beginners: GET requests are used to get information about
    A/B tests and their results.
    """
    try:
        # Parse query parameters
        test_id = request.get('query', {}).get('test_id')
        
        if test_id:
            # Get specific test results
            results = ab_framework.get_test_results(test_id)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'A/B Test Results',
                    'test': results,
                    'timestamp': datetime.now().isoformat()
                })
            }
        else:
            # Get all tests
            all_tests = ab_framework.get_all_tests()
            active_tests = ab_framework.get_active_tests()
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'A/B Testing Status',
                    'all_tests': all_tests,
                    'active_tests': active_tests,
                    'total_tests': len(all_tests),
                    'active_count': len(active_tests),
                    'timestamp': datetime.now().isoformat()
                })
            }
        
    except Exception as e:
        logger.error(f"Error handling GET request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error getting A/B test data',
                'message': str(e)
            })
        }

def handle_post_request(request, headers):
    """
    Handle POST requests to the A/B testing endpoint.
    
    For beginners: POST requests are used to create new A/B tests
    and start existing ones.
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
        operation = data.get('operation', 'create_test')
        
        if operation == 'create_test':
            return handle_create_test(data, headers)
        elif operation == 'start_test':
            return handle_start_test(data, headers)
        elif operation == 'stop_test':
            return handle_stop_test(data, headers)
        elif operation == 'add_variant':
            return handle_add_variant(data, headers)
        elif operation == 'predict':
            return handle_predict(data, headers)
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid operation',
                    'supported_operations': ['create_test', 'start_test', 'stop_test', 'add_variant', 'predict']
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

def handle_create_test(data, headers):
    """
    Handle create test requests.
    
    For beginners: This creates a new A/B test to compare different AI models.
    """
    try:
        test_id = data.get('test_id')
        name = data.get('name')
        description = data.get('description', '')
        
        if not test_id or not name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing required fields: test_id, name'
                })
            }
        
        # Create the test
        test = ab_framework.create_test(test_id, name, description)
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({
                'message': 'A/B test created successfully',
                'test_id': test_id,
                'name': name,
                'status': test.status.value,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Invalid test configuration',
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error creating test: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error creating test',
                'message': str(e)
            })
        }

def handle_start_test(data, headers):
    """
    Handle start test requests.
    
    For beginners: This starts an A/B test so it begins comparing models.
    """
    try:
        test_id = data.get('test_id')
        
        if not test_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing required field: test_id'
                })
            }
        
        # Start the test
        ab_framework.start_test(test_id)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'A/B test started successfully',
                'test_id': test_id,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Cannot start test',
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error starting test: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error starting test',
                'message': str(e)
            })
        }

def handle_stop_test(data, headers):
    """
    Handle stop test requests.
    
    For beginners: This stops an A/B test and determines the winner.
    """
    try:
        test_id = data.get('test_id')
        
        if not test_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing required field: test_id'
                })
            }
        
        # Stop the test
        ab_framework.stop_test(test_id)
        
        # Get results
        results = ab_framework.get_test_results(test_id)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'A/B test stopped successfully',
                'test_id': test_id,
                'results': results,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Cannot stop test',
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error stopping test: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error stopping test',
                'message': str(e)
            })
        }

def handle_add_variant(data, headers):
    """
    Handle add variant requests.
    
    For beginners: This adds a new AI model to an A/B test.
    """
    try:
        test_id = data.get('test_id')
        variant_data = data.get('variant', {})
        
        if not test_id or not variant_data:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing required fields: test_id, variant'
                })
            }
        
        # Create model variant
        variant = ModelVariant(
            name=variant_data.get('name'),
            model_path=variant_data.get('model_path'),
            traffic_percentage=variant_data.get('traffic_percentage', 0.0)
        )
        
        # Add to test
        ab_framework.add_variant_to_test(test_id, variant)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Variant added successfully',
                'test_id': test_id,
                'variant_name': variant.name,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Invalid variant configuration',
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error adding variant: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error adding variant',
                'message': str(e)
            })
        }

def handle_predict(data, headers):
    """
    Handle predict requests.
    
    For beginners: This analyzes a log entry using the active A/B test.
    """
    try:
        log_entry = data.get('log_entry')
        
        if not log_entry:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing required field: log_entry'
                })
            }
        
        # Make prediction using A/B testing framework
        prediction = ab_framework.predict(log_entry)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Prediction completed',
                'prediction': prediction,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error making prediction',
                'message': str(e)
            })
        }

def handle_put_request(request, headers):
    """Handle PUT requests (not implemented yet)."""
    return {
        'statusCode': 501,
        'headers': headers,
        'body': json.dumps({
            'error': 'PUT method not implemented yet'
        })
    }

def handle_delete_request(request, headers):
    """Handle DELETE requests (not implemented yet)."""
    return {
        'statusCode': 501,
        'headers': headers,
        'body': json.dumps({
            'error': 'DELETE method not implemented yet'
        })
    }

# For Vercel Functions, we need to export the handler
def main(request):
    """Main entry point for Vercel Functions."""
    return handler(request)
