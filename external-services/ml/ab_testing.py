"""
A/B Testing Framework for ML Models
==================================

This module provides A/B testing capabilities for machine learning models.
It allows testing multiple models simultaneously and automatically selecting
the best performing one.

For beginners: This is like having a smart system that tests different
AI models and automatically picks the best one based on real performance data.

Author: Engineering Log Intelligence Team
Date: September 23, 2025
"""

import json
import logging
import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import statistics

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Status of an A/B test."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ModelVariant:
    """Represents a model variant in an A/B test."""
    
    def __init__(self, name: str, model_path: str, traffic_percentage: float = 0.0):
        """
        Initialize a model variant.
        
        For beginners: This represents one version of an AI model that we want to test.
        
        Args:
            name: Human-readable name for the variant
            model_path: Path to the model file
            traffic_percentage: Percentage of traffic to send to this variant (0-100)
        """
        self.name = name
        self.model_path = model_path
        self.traffic_percentage = traffic_percentage
        self.model = None
        self.is_loaded = False
        
        # Performance metrics
        self.total_predictions = 0
        self.correct_predictions = 0
        self.accuracy = 0.0
        self.average_response_time = 0.0
        self.error_count = 0
        
        # Response times for calculating average
        self.response_times = []
        
        logger.info(f"Created model variant: {name} ({traffic_percentage}% traffic)")
    
    def load_model(self):
        """Load the model from disk."""
        try:
            # In a real implementation, this would load the actual model
            # For now, we'll simulate model loading
            logger.info(f"Loading model: {self.name}")
            time.sleep(0.1)  # Simulate loading time
            self.is_loaded = True
            logger.info(f"Model loaded successfully: {self.name}")
        except Exception as e:
            logger.error(f"Error loading model {self.name}: {str(e)}")
            self.is_loaded = False
    
    def predict(self, log_entry: Dict) -> Dict[str, Any]:
        """
        Make a prediction using this model variant.
        
        For beginners: This runs the AI model on a log entry and returns the result.
        
        Args:
            log_entry: Log entry to analyze
            
        Returns:
            Prediction result with metadata
        """
        if not self.is_loaded:
            raise ValueError(f"Model {self.name} is not loaded")
        
        start_time = time.time()
        
        try:
            # Simulate model prediction
            # In a real implementation, this would use the actual model
            prediction = self._simulate_prediction(log_entry)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            # Update metrics
            self.total_predictions += 1
            self._update_accuracy(prediction, log_entry)
            self._update_average_response_time()
            
            # Add metadata
            prediction['variant_name'] = self.name
            prediction['response_time'] = response_time
            prediction['timestamp'] = datetime.now().isoformat()
            
            return prediction
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in prediction for {self.name}: {str(e)}")
            return {
                'error': str(e),
                'variant_name': self.name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _simulate_prediction(self, log_entry: Dict) -> Dict[str, Any]:
        """Simulate a model prediction for demonstration."""
        message = log_entry.get('message', '').lower()
        level = log_entry.get('level', 'INFO')
        
        # Simulate different model behaviors
        if 'error' in message or 'failed' in message:
            category = 'error'
            confidence = 0.85 + random.uniform(-0.1, 0.1)
            is_anomaly = random.choice([True, False])
        elif 'security' in message or 'unauthorized' in message:
            category = 'security'
            confidence = 0.90 + random.uniform(-0.05, 0.05)
            is_anomaly = True
        elif 'performance' in message or 'slow' in message:
            category = 'performance'
            confidence = 0.75 + random.uniform(-0.1, 0.1)
            is_anomaly = random.choice([True, False])
        else:
            category = 'system'
            confidence = 0.70 + random.uniform(-0.1, 0.1)
            is_anomaly = False
        
        return {
            'category': category,
            'confidence': round(confidence, 3),
            'is_anomaly': is_anomaly,
            'risk_level': 'high' if confidence > 0.8 else 'medium' if confidence > 0.6 else 'low'
        }
    
    def _update_accuracy(self, prediction: Dict, log_entry: Dict):
        """Update accuracy based on prediction correctness."""
        # In a real implementation, this would compare with ground truth
        # For now, we'll simulate accuracy based on confidence
        confidence = prediction.get('confidence', 0)
        if confidence > 0.7:  # Assume high confidence predictions are correct
            self.correct_predictions += 1
        
        self.accuracy = self.correct_predictions / max(self.total_predictions, 1)
    
    def _update_average_response_time(self):
        """Update average response time."""
        if self.response_times:
            self.average_response_time = statistics.mean(self.response_times[-100:])  # Last 100 predictions
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics for this variant."""
        return {
            'name': self.name,
            'total_predictions': self.total_predictions,
            'correct_predictions': self.correct_predictions,
            'accuracy': round(self.accuracy, 3),
            'average_response_time': round(self.average_response_time, 3),
            'error_count': self.error_count,
            'error_rate': round(self.error_count / max(self.total_predictions, 1), 3),
            'is_loaded': self.is_loaded
        }

@dataclass
class ABTest:
    """Represents an A/B test configuration."""
    
    test_id: str
    name: str
    description: str
    variants: List[ModelVariant] = field(default_factory=list)
    status: TestStatus = TestStatus.DRAFT
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_sample_size: int = 1000
    confidence_level: float = 0.95
    max_duration_hours: int = 24
    
    # Test results
    winner: Optional[str] = None
    statistical_significance: bool = False
    p_value: float = 0.0
    
    def __post_init__(self):
        """Initialize test after creation."""
        logger.info(f"Created A/B test: {self.name} (ID: {self.test_id})")
    
    def add_variant(self, variant: ModelVariant):
        """Add a model variant to the test."""
        self.variants.append(variant)
        logger.info(f"Added variant {variant.name} to test {self.test_id}")
    
    def start_test(self):
        """Start the A/B test."""
        if self.status != TestStatus.DRAFT:
            raise ValueError(f"Cannot start test in status: {self.status}")
        
        if len(self.variants) < 2:
            raise ValueError("A/B test requires at least 2 variants")
        
        # Validate traffic percentages
        total_traffic = sum(v.traffic_percentage for v in self.variants)
        if abs(total_traffic - 100.0) > 0.01:
            raise ValueError(f"Traffic percentages must sum to 100%, got {total_traffic}%")
        
        # Load all models
        for variant in self.variants:
            variant.load_model()
        
        self.status = TestStatus.RUNNING
        self.start_time = datetime.now()
        
        logger.info(f"Started A/B test: {self.name}")
    
    def stop_test(self):
        """Stop the A/B test."""
        if self.status != TestStatus.RUNNING:
            raise ValueError(f"Cannot stop test in status: {self.status}")
        
        self.status = TestStatus.COMPLETED
        self.end_time = datetime.now()
        
        # Determine winner
        self._determine_winner()
        
        logger.info(f"Stopped A/B test: {self.name}, Winner: {self.winner}")
    
    def _determine_winner(self):
        """Determine the winning variant based on performance metrics."""
        if not self.variants:
            return
        
        # Sort variants by accuracy (primary metric)
        sorted_variants = sorted(self.variants, key=lambda v: v.accuracy, reverse=True)
        
        # Check if difference is statistically significant
        if len(sorted_variants) >= 2:
            best = sorted_variants[0]
            second_best = sorted_variants[1]
            
            # Simple significance test (in real implementation, use proper statistical tests)
            accuracy_diff = best.accuracy - second_best.accuracy
            min_samples = min(best.total_predictions, second_best.total_predictions)
            
            if accuracy_diff > 0.05 and min_samples >= self.min_sample_size:
                self.statistical_significance = True
                self.p_value = 0.01  # Simplified
            else:
                self.statistical_significance = False
                self.p_value = 0.5  # Simplified
        
        self.winner = sorted_variants[0].name if sorted_variants else None
    
    def get_test_results(self) -> Dict[str, Any]:
        """Get comprehensive test results."""
        return {
            'test_id': self.test_id,
            'name': self.name,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_hours': self._get_duration_hours(),
            'winner': self.winner,
            'statistical_significance': self.statistical_significance,
            'p_value': self.p_value,
            'variants': [v.get_metrics() for v in self.variants],
            'total_predictions': sum(v.total_predictions for v in self.variants)
        }
    
    def _get_duration_hours(self) -> float:
        """Get test duration in hours."""
        if not self.start_time:
            return 0.0
        
        end_time = self.end_time or datetime.now()
        duration = end_time - self.start_time
        return duration.total_seconds() / 3600

class ABTestingFramework:
    """
    Main A/B testing framework for ML models.
    
    This framework manages multiple A/B tests and provides
    a unified interface for testing different model variants.
    """
    
    def __init__(self):
        """Initialize the A/B testing framework."""
        self.tests: Dict[str, ABTest] = {}
        self.active_tests: List[str] = []
        self.traffic_router = TrafficRouter()
        
        logger.info("A/B Testing Framework initialized")
    
    def create_test(self, test_id: str, name: str, description: str) -> ABTest:
        """
        Create a new A/B test.
        
        For beginners: This creates a new test that will compare different AI models.
        
        Args:
            test_id: Unique identifier for the test
            name: Human-readable name
            description: Description of what the test is for
            
        Returns:
            Created A/B test object
        """
        if test_id in self.tests:
            raise ValueError(f"Test with ID {test_id} already exists")
        
        test = ABTest(test_id=test_id, name=name, description=description)
        self.tests[test_id] = test
        
        logger.info(f"Created A/B test: {name} (ID: {test_id})")
        return test
    
    def add_variant_to_test(self, test_id: str, variant: ModelVariant):
        """Add a variant to an existing test."""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        self.tests[test_id].add_variant(variant)
    
    def start_test(self, test_id: str):
        """Start an A/B test."""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.tests[test_id]
        test.start_test()
        
        if test_id not in self.active_tests:
            self.active_tests.append(test_id)
        
        logger.info(f"Started A/B test: {test.name}")
    
    def stop_test(self, test_id: str):
        """Stop an A/B test."""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.tests[test_id]
        test.stop_test()
        
        if test_id in self.active_tests:
            self.active_tests.remove(test_id)
        
        logger.info(f"Stopped A/B test: {test.name}")
    
    def predict(self, log_entry: Dict) -> Dict[str, Any]:
        """
        Make a prediction using the appropriate model variant.
        
        For beginners: This routes a log entry to the right AI model
        based on the active A/B tests.
        
        Args:
            log_entry: Log entry to analyze
            
        Returns:
            Prediction result with A/B test metadata
        """
        # Route to appropriate variant
        variant = self.traffic_router.route_traffic(log_entry, self.tests, self.active_tests)
        
        if not variant:
            # No active tests, use default model
            return self._default_prediction(log_entry)
        
        # Make prediction using selected variant
        prediction = variant.predict(log_entry)
        
        # Add A/B test metadata
        prediction['ab_test_id'] = self._get_test_id_for_variant(variant)
        prediction['variant_name'] = variant.name
        
        return prediction
    
    def _get_test_id_for_variant(self, variant: ModelVariant) -> Optional[str]:
        """Get the test ID for a given variant."""
        for test_id, test in self.tests.items():
            if variant in test.variants:
                return test_id
        return None
    
    def _default_prediction(self, log_entry: Dict) -> Dict[str, Any]:
        """Make a default prediction when no A/B tests are active."""
        return {
            'category': 'system',
            'confidence': 0.5,
            'is_anomaly': False,
            'risk_level': 'low',
            'variant_name': 'default',
            'ab_test_id': None,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get results for a specific test."""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        return self.tests[test_id].get_test_results()
    
    def get_all_tests(self) -> List[Dict[str, Any]]:
        """Get all tests and their status."""
        return [test.get_test_results() for test in self.tests.values()]
    
    def get_active_tests(self) -> List[Dict[str, Any]]:
        """Get all currently active tests."""
        return [self.tests[test_id].get_test_results() for test_id in self.active_tests]

class TrafficRouter:
    """
    Routes traffic to appropriate model variants based on A/B test configuration.
    
    For beginners: This decides which AI model should analyze each log entry
    based on the active A/B tests.
    """
    
    def route_traffic(self, log_entry: Dict, tests: Dict[str, ABTest], active_tests: List[str]) -> Optional[ModelVariant]:
        """
        Route traffic to the appropriate model variant.
        
        Args:
            log_entry: Log entry to route
            tests: All available tests
            active_tests: List of active test IDs
            
        Returns:
            Selected model variant or None
        """
        if not active_tests:
            return None
        
        # For simplicity, use the first active test
        # In a real implementation, this would be more sophisticated
        test_id = active_tests[0]
        test = tests[test_id]
        
        if not test.variants:
            return None
        
        # Simple round-robin routing based on traffic percentages
        # In a real implementation, this would use proper traffic splitting
        random_value = random.random() * 100
        
        cumulative_percentage = 0
        for variant in test.variants:
            cumulative_percentage += variant.traffic_percentage
            if random_value <= cumulative_percentage:
                return variant
        
        # Fallback to first variant
        return test.variants[0]

# Global framework instance
ab_framework = ABTestingFramework()
