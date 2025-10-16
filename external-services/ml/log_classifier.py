"""
Log Classification Model
========================

This module implements a machine learning model that automatically categorizes log entries
into different log levels (INFO, WARN, ERROR, DEBUG, FATAL).

Updated: October 16, 2025 - Now uses actual trained scikit-learn models

Author: Engineering Log Intelligence Team
Date: September 21, 2025
"""

import logging
import pickle
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogClassifier:
    """
    A machine learning model that classifies log entries into log levels.
    
    This class handles:
    1. Loading pre-trained scikit-learn models
    2. Predicting log levels for new log entries
    3. Managing model lifecycle and caching
    4. Evaluating model performance
    """
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize the log classifier.
        
        Args:
            model_dir: Directory containing the trained model files
        """
        self.model = None  # Will hold the trained RandomForest classifier
        self.vectorizer = None  # Will hold the TF-IDF vectorizer
        self.metadata = None  # Will hold model training metadata
        self.is_trained = False
        
        # Set up model paths (relative to project root)
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, 'log_classifier_simple.pkl')
        self.vectorizer_path = os.path.join(model_dir, 'vectorizer_simple.pkl')
        self.metadata_path = os.path.join(model_dir, 'metadata_simple.json')
        
        # Log levels from trained model
        self.log_levels = ['INFO', 'WARN', 'ERROR', 'DEBUG', 'FATAL']
        
        logger.info(f"LogClassifier initialized (model_dir: {model_dir})")
    
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
    
    def load_pretrained_model(self) -> bool:
        """
        Load pre-trained model from disk.
        
        For beginners: This loads the RandomForest model that was trained
        using train_models_simple.py. We don't need to train again!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Loading pre-trained model...")
            
            # Check if model files exist
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found: {self.model_path}")
                return False
            
            if not os.path.exists(self.vectorizer_path):
                logger.error(f"Vectorizer file not found: {self.vectorizer_path}")
                return False
            
            # Load the trained classifier
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"✅ Loaded classifier from {self.model_path}")
            
            # Load the TF-IDF vectorizer
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            logger.info(f"✅ Loaded vectorizer from {self.vectorizer_path}")
            
            # Load metadata (optional, for reporting accuracy)
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"✅ Loaded metadata: {self.metadata.get('classifier_accuracy', 'N/A')} accuracy")
            
            self.is_trained = True
            logger.info("✅ Model loaded successfully and ready for predictions")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            self.is_trained = False
            return False
    
    def train(self, logs: List[Dict]) -> Dict[str, float]:
        """
        Train the log classification model.
        
        Note: This implementation uses pre-trained models. To retrain from scratch,
        use train_models_simple.py in the project root.
        
        For beginners: We're using a pre-trained model, so this method just
        loads it rather than training from scratch.
        
        Args:
            logs: List of training log entries (unused - we load pre-trained model)
            
        Returns:
            Dictionary with training metrics
        """
        logger.info("Loading pre-trained model instead of training from scratch...")
        
        if self.load_pretrained_model():
            # Return metadata from the pre-trained model
            return {
                'training_samples': self.metadata.get('num_training_samples', 0) if self.metadata else 0,
                'accuracy': self.metadata.get('classifier_accuracy', 0.0) if self.metadata else 0.0,
                'features': self.metadata.get('features', 0) if self.metadata else 0,
                'model_type': 'RandomForest (pre-trained)',
                'trained_at': self.metadata.get('trained_at', '') if self.metadata else ''
            }
        else:
            raise RuntimeError("Failed to load pre-trained model. Run train_models_simple.py first.")
    
    def predict(self, log_message: str) -> Dict[str, any]:
        """
        Predict the log level of a message using the trained ML model.
        
        For beginners: This function uses the RandomForest model to predict
        what log level (INFO, WARN, ERROR, etc.) a message should have.
        
        Args:
            log_message: The log message to classify
            
        Returns:
            Dictionary with prediction results including predicted_level and confidence
        """
        # Auto-load model if not loaded yet
        if not self.is_trained:
            logger.info("Model not loaded, attempting to load...")
            if not self.load_pretrained_model():
                raise ValueError("Model must be loaded before making predictions. Run train_models_simple.py first.")
        
        logger.info(f"Classifying log message: {log_message[:100]}...")
        
        try:
            # Step 1: Vectorize the message using TF-IDF
            X = self.vectorizer.transform([log_message])
            
            # Step 2: Predict using the trained model
            predicted_level = self.model.predict(X)[0]
            
            # Step 3: Get prediction probabilities for confidence score
            probabilities = self.model.predict_proba(X)[0]
            confidence = float(max(probabilities))  # Highest probability
            
            # Step 4: Get probability for each class (optional, for detailed analysis)
            class_probabilities = {}
            for level, prob in zip(self.model.classes_, probabilities):
                class_probabilities[level] = float(prob)
            
            result = {
                'predicted_level': predicted_level,
                'confidence': confidence,
                'class_probabilities': class_probabilities,
                'timestamp': datetime.now().isoformat(),
                'model_version': '1.0.0',
                'model_type': 'RandomForest'
            }
            
            logger.info(f"Prediction: {predicted_level} (confidence: {confidence:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
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
    
    def load_model(self, filepath: str = None) -> bool:
        """
        Load a previously trained model from disk.
        
        For beginners: This is a wrapper that calls load_pretrained_model()
        for compatibility with the old interface.
        
        Args:
            filepath: Path to the saved model (ignored, uses default paths)
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("load_model() called, delegating to load_pretrained_model()")
        return self.load_pretrained_model()
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information including real accuracy metrics
        """
        info = {
            'is_trained': self.is_trained,
            'log_levels': self.log_levels,
            'model_version': '1.0.0',
            'model_type': 'RandomForest',
            'last_checked': datetime.now().isoformat()
        }
        
        # Add metadata if available
        if self.metadata:
            info.update({
                'accuracy': self.metadata.get('classifier_accuracy', 0.0),
                'training_samples': self.metadata.get('num_training_samples', 0),
                'features': self.metadata.get('features', 0),
                'trained_at': self.metadata.get('trained_at', '')
            })
        
        # Add model-specific info if loaded
        if self.model:
            info['n_estimators'] = getattr(self.model, 'n_estimators', 'N/A')
            info['n_features'] = getattr(self.model, 'n_features_in_', 'N/A')
        
        return info
