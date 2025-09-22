"""
ML Model Performance Monitoring
==============================

This module provides monitoring and metrics collection for our machine learning models.
It tracks model performance, accuracy, and usage statistics.

For beginners: This is like a dashboard that shows how well our AI models
are performing and helps us improve them over time.

Author: Engineering Log Intelligence Team
Date: September 21, 2025
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import statistics

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelMonitor:
    """
    Monitor for ML model performance and usage statistics.
    
    This class tracks:
    1. Model accuracy and performance metrics
    2. Prediction latency and throughput
    3. Error rates and failure patterns
    4. Model usage statistics
    5. Performance trends over time
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the ML model monitor.
        
        For beginners: This sets up the monitoring system to track
        how well our AI models are performing.
        
        Args:
            max_history: Maximum number of historical records to keep
        """
        self.max_history = max_history
        self.metrics = {
            'log_classifier': {
                'predictions': deque(maxlen=max_history),
                'accuracy_scores': deque(maxlen=max_history),
                'latency_times': deque(maxlen=max_history),
                'error_count': 0,
                'total_predictions': 0
            },
            'anomaly_detector': {
                'predictions': deque(maxlen=max_history),
                'accuracy_scores': deque(maxlen=max_history),
                'latency_times': deque(maxlen=max_history),
                'error_count': 0,
                'total_predictions': 0
            }
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_latency_ms': 1000,  # Maximum acceptable latency
            'min_accuracy': 0.7,     # Minimum acceptable accuracy
            'max_error_rate': 0.05   # Maximum acceptable error rate
        }
        
        logger.info("ML Model Monitor initialized")
    
    def record_prediction(self, model_name: str, prediction: Dict[str, Any], 
                         actual_label: Optional[str] = None, latency_ms: float = 0.0):
        """
        Record a prediction made by a model.
        
        For beginners: This function records each time our AI models
        make a prediction, so we can track how well they're doing.
        
        Args:
            model_name: Name of the model (log_classifier or anomaly_detector)
            prediction: The prediction result
            actual_label: The correct answer (if known)
            latency_ms: Time taken to make the prediction
        """
        if model_name not in self.metrics:
            logger.warning(f"Unknown model: {model_name}")
            return
        
        # Record the prediction
        prediction_record = {
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'actual_label': actual_label,
            'latency_ms': latency_ms
        }
        
        self.metrics[model_name]['predictions'].append(prediction_record)
        self.metrics[model_name]['total_predictions'] += 1
        self.metrics[model_name]['latency_times'].append(latency_ms)
        
        # Calculate accuracy if we have the actual label
        if actual_label is not None:
            accuracy = self._calculate_accuracy(prediction, actual_label, model_name)
            self.metrics[model_name]['accuracy_scores'].append(accuracy)
        
        logger.debug(f"Recorded prediction for {model_name}: {latency_ms:.2f}ms")
    
    def record_error(self, model_name: str, error_message: str):
        """
        Record an error that occurred in a model.
        
        For beginners: This tracks when our AI models make mistakes
        or encounter problems, so we can fix them.
        
        Args:
            model_name: Name of the model that had an error
            error_message: Description of the error
        """
        if model_name not in self.metrics:
            logger.warning(f"Unknown model: {model_name}")
            return
        
        self.metrics[model_name]['error_count'] += 1
        
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'model': model_name,
            'error': error_message
        }
        
        logger.error(f"Model {model_name} error: {error_message}")
    
    def _calculate_accuracy(self, prediction: Dict[str, Any], actual_label: str, model_name: str) -> float:
        """
        Calculate accuracy for a prediction.
        
        For beginners: This compares what our AI predicted with the correct
        answer to see how accurate it was.
        """
        if model_name == 'log_classifier':
            predicted_category = prediction.get('category', '')
            return 1.0 if predicted_category == actual_label else 0.0
        
        elif model_name == 'anomaly_detector':
            predicted_anomaly = prediction.get('is_anomaly', False)
            actual_anomaly = actual_label.lower() in ['true', 'anomaly', 'yes']
            return 1.0 if predicted_anomaly == actual_anomaly else 0.0
        
        return 0.0
    
    def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific model.
        
        For beginners: This gives you a summary of how well a specific
        AI model is performing.
        
        Args:
            model_name: Name of the model to get metrics for
            
        Returns:
            Dictionary with performance metrics
        """
        if model_name not in self.metrics:
            return {'error': f'Unknown model: {model_name}'}
        
        model_metrics = self.metrics[model_name]
        
        # Calculate current metrics
        total_predictions = model_metrics['total_predictions']
        error_count = model_metrics['error_count']
        
        # Calculate accuracy
        accuracy_scores = list(model_metrics['accuracy_scores'])
        avg_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0.0
        
        # Calculate latency
        latency_times = list(model_metrics['latency_times'])
        avg_latency = statistics.mean(latency_times) if latency_times else 0.0
        max_latency = max(latency_times) if latency_times else 0.0
        min_latency = min(latency_times) if latency_times else 0.0
        
        # Calculate error rate
        error_rate = error_count / total_predictions if total_predictions > 0 else 0.0
        
        # Check if metrics are within thresholds
        performance_status = self._check_performance_status(model_name, avg_accuracy, avg_latency, error_rate)
        
        return {
            'model_name': model_name,
            'total_predictions': total_predictions,
            'error_count': error_count,
            'error_rate': error_rate,
            'accuracy': {
                'average': avg_accuracy,
                'samples': len(accuracy_scores)
            },
            'latency': {
                'average_ms': avg_latency,
                'max_ms': max_latency,
                'min_ms': min_latency,
                'samples': len(latency_times)
            },
            'performance_status': performance_status,
            'last_updated': datetime.now().isoformat()
        }
    
    def _check_performance_status(self, model_name: str, accuracy: float, 
                                 latency: float, error_rate: float) -> str:
        """
        Check if model performance is within acceptable thresholds.
        
        For beginners: This checks if our AI model is performing well enough
        or if it needs attention.
        """
        issues = []
        
        if accuracy < self.thresholds['min_accuracy']:
            issues.append(f"Low accuracy: {accuracy:.2%} < {self.thresholds['min_accuracy']:.2%}")
        
        if latency > self.thresholds['max_latency_ms']:
            issues.append(f"High latency: {latency:.1f}ms > {self.thresholds['max_latency_ms']}ms")
        
        if error_rate > self.thresholds['max_error_rate']:
            issues.append(f"High error rate: {error_rate:.2%} > {self.thresholds['max_error_rate']:.2%}")
        
        if not issues:
            return 'healthy'
        elif len(issues) == 1:
            return 'warning'
        else:
            return 'critical'
    
    def get_overall_status(self) -> Dict[str, Any]:
        """
        Get overall status of all models.
        
        For beginners: This gives you a summary of how all our AI models
        are performing together.
        """
        overall_metrics = {
            'timestamp': datetime.now().isoformat(),
            'models': {},
            'overall_status': 'healthy',
            'total_predictions': 0,
            'total_errors': 0
        }
        
        model_statuses = []
        
        for model_name in self.metrics:
            model_performance = self.get_model_performance(model_name)
            overall_metrics['models'][model_name] = model_performance
            
            overall_metrics['total_predictions'] += model_performance['total_predictions']
            overall_metrics['total_errors'] += model_performance['error_count']
            
            model_statuses.append(model_performance['performance_status'])
        
        # Determine overall status
        if 'critical' in model_statuses:
            overall_metrics['overall_status'] = 'critical'
        elif 'warning' in model_statuses:
            overall_metrics['overall_status'] = 'warning'
        
        return overall_metrics
    
    def get_performance_trends(self, model_name: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance trends over time.
        
        For beginners: This shows how our AI model's performance has
        changed over time, so we can see if it's getting better or worse.
        
        Args:
            model_name: Name of the model
            hours: Number of hours to look back
            
        Returns:
            Dictionary with trend data
        """
        if model_name not in self.metrics:
            return {'error': f'Unknown model: {model_name}'}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        model_metrics = self.metrics[model_name]
        
        # Filter predictions by time
        recent_predictions = [
            p for p in model_metrics['predictions']
            if datetime.fromisoformat(p['timestamp']) > cutoff_time
        ]
        
        if not recent_predictions:
            return {
                'model_name': model_name,
                'period_hours': hours,
                'message': 'No data available for the specified period'
            }
        
        # Calculate trends
        latencies = [p['latency_ms'] for p in recent_predictions]
        accuracies = [p for p in recent_predictions if p.get('actual_label') is not None]
        
        trend_data = {
            'model_name': model_name,
            'period_hours': hours,
            'total_predictions': len(recent_predictions),
            'latency_trend': {
                'average': statistics.mean(latencies) if latencies else 0.0,
                'trend': 'stable'  # Simplified - in real system would calculate slope
            },
            'accuracy_trend': {
                'average': statistics.mean([self._calculate_accuracy(p['prediction'], p['actual_label'], model_name) 
                                         for p in accuracies]) if accuracies else 0.0,
                'samples': len(accuracies),
                'trend': 'stable'  # Simplified - in real system would calculate slope
            }
        }
        
        return trend_data
    
    def reset_metrics(self, model_name: Optional[str] = None):
        """
        Reset metrics for a model or all models.
        
        For beginners: This clears all the performance data, useful when
        you want to start fresh or after making improvements to the model.
        
        Args:
            model_name: Specific model to reset, or None for all models
        """
        if model_name:
            if model_name in self.metrics:
                self.metrics[model_name] = {
                    'predictions': deque(maxlen=self.max_history),
                    'accuracy_scores': deque(maxlen=self.max_history),
                    'latency_times': deque(maxlen=self.max_history),
                    'error_count': 0,
                    'total_predictions': 0
                }
                logger.info(f"Reset metrics for {model_name}")
        else:
            for model in self.metrics:
                self.reset_metrics(model)
            logger.info("Reset metrics for all models")
    
    def export_metrics(self, filepath: str) -> bool:
        """
        Export metrics to a JSON file.
        
        For beginners: This saves all the performance data to a file
        so you can analyze it later or share it with others.
        
        Args:
            filepath: Path to save the metrics file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'metrics': {}
            }
            
            for model_name, model_metrics in self.metrics.items():
                export_data['metrics'][model_name] = {
                    'total_predictions': model_metrics['total_predictions'],
                    'error_count': model_metrics['error_count'],
                    'recent_predictions': list(model_metrics['predictions'])[-100:],  # Last 100 predictions
                    'accuracy_scores': list(model_metrics['accuracy_scores']),
                    'latency_times': list(model_metrics['latency_times'])
                }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Metrics exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")
            return False
