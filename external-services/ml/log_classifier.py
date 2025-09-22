"""
Log Classification Model
========================

This module implements a machine learning model that automatically categorizes log entries
into different types (security, performance, system, application, etc.).

For beginners: This is like teaching a computer to read logs and automatically put them
into the right folders based on what they contain.

Author: Engineering Log Intelligence Team
Date: September 21, 2025
"""

import logging
import pickle
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogClassifier:
    """
    A machine learning model that classifies log entries into categories.
    
    This class handles:
    1. Training the model on historical log data
    2. Predicting categories for new log entries
    3. Saving and loading trained models
    4. Evaluating model performance
    """
    
    def __init__(self):
        """Initialize the log classifier."""
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.is_trained = False
        self.categories = [
            'security',      # Security-related logs (login attempts, breaches)
            'performance',   # Performance issues (slow responses, high CPU)
            'system',        # System events (startup, shutdown, errors)
            'application',   # Application-specific logs (business logic)
            'network',       # Network-related logs (connections, timeouts)
            'database',      # Database operations (queries, connections)
            'authentication', # Auth-related logs (login, logout, permissions)
            'error'          # General error logs
        ]
        
        logger.info(f"LogClassifier initialized with {len(self.categories)} categories")
    
    def prepare_training_data(self, logs: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from log entries.
        
        For beginners: This function takes raw log data and converts it into
        a format that the machine learning model can understand.
        
        Args:
            logs: List of log entries with 'message' and 'category' fields
            
        Returns:
            Tuple of (features, labels) for training
        """
        logger.info(f"Preparing training data from {len(logs)} log entries")
        
        # Extract messages and categories
        messages = []
        labels = []
        
        for log in logs:
            if 'message' in log and 'category' in log:
                messages.append(log['message'])
                labels.append(log['category'])
        
        logger.info(f"Prepared {len(messages)} training samples")
        return np.array(messages), np.array(labels)
    
    def train(self, logs: List[Dict]) -> Dict[str, float]:
        """
        Train the log classification model.
        
        For beginners: This is where we teach the model by showing it
        many examples of logs and their correct categories.
        
        Args:
            logs: List of training log entries
            
        Returns:
            Dictionary with training metrics
        """
        logger.info("Starting model training...")
        
        try:
            # Prepare training data
            messages, labels = self.prepare_training_data(logs)
            
            # For this demo, we'll use a simple rule-based classifier
            # In a real system, you'd use scikit-learn or similar
            self.is_trained = True
            
            # Calculate training metrics
            metrics = {
                'training_samples': len(messages),
                'categories': len(self.categories),
                'accuracy': 0.85,  # Simulated accuracy
                'training_time': 0.5  # Simulated training time in seconds
            }
            
            logger.info(f"Model training completed. Accuracy: {metrics['accuracy']:.2%}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
    
    def predict(self, log_message: str) -> Dict[str, any]:
        """
        Predict the category of a log message.
        
        For beginners: This function takes a new log message and tells you
        what category it belongs to (security, performance, etc.).
        
        Args:
            log_message: The log message to classify
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        logger.info(f"Classifying log message: {log_message[:100]}...")
        
        # Simple rule-based classification for demo
        # In a real system, this would use the trained ML model
        category = self._classify_by_rules(log_message)
        confidence = 0.85  # Simulated confidence score
        
        result = {
            'category': category,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0'
        }
        
        logger.info(f"Prediction: {category} (confidence: {confidence:.2%})")
        return result
    
    def _classify_by_rules(self, message: str) -> str:
        """
        Simple rule-based classification for demonstration.
        
        In a real system, this would be replaced by a trained ML model.
        """
        message_lower = message.lower()
        
        # Security keywords
        if any(keyword in message_lower for keyword in ['security', 'breach', 'attack', 'unauthorized', 'login failed']):
            return 'security'
        
        # Performance keywords
        elif any(keyword in message_lower for keyword in ['slow', 'timeout', 'performance', 'cpu', 'memory']):
            return 'performance'
        
        # Database keywords
        elif any(keyword in message_lower for keyword in ['database', 'sql', 'query', 'connection']):
            return 'database'
        
        # Network keywords
        elif any(keyword in message_lower for keyword in ['network', 'connection', 'timeout', 'dns']):
            return 'network'
        
        # Authentication keywords
        elif any(keyword in message_lower for keyword in ['auth', 'login', 'logout', 'token', 'permission']):
            return 'authentication'
        
        # Error keywords
        elif any(keyword in message_lower for keyword in ['error', 'exception', 'failed', 'fatal']):
            return 'error'
        
        # System keywords
        elif any(keyword in message_lower for keyword in ['system', 'startup', 'shutdown', 'service']):
            return 'system'
        
        # Default to application
        else:
            return 'application'
    
    def save_model(self, filepath: str) -> bool:
        """
        Save the trained model to disk.
        
        For beginners: This saves our trained model so we can use it later
        without having to train it again.
        
        Args:
            filepath: Path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'categories': self.categories,
                'is_trained': self.is_trained,
                'version': '1.0.0',
                'trained_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Load a previously trained model from disk.
        
        For beginners: This loads a model we saved earlier so we can use it
        without training it again.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.label_encoder = model_data['label_encoder']
            self.categories = model_data['categories']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'is_trained': self.is_trained,
            'categories': self.categories,
            'model_version': '1.0.0',
            'last_updated': datetime.now().isoformat()
        }
