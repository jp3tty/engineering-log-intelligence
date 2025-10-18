"""
Business Severity Prediction Model
===================================

This module implements a machine learning model that predicts the business severity
of log entries (CRITICAL, HIGH, MEDIUM, LOW) using multi-feature analysis.

Updated: October 17, 2025 - Enhanced multi-feature model with 96.3% accuracy

Features used:
- Message text (TF-IDF vectorization)
- Service name (categorical)
- Endpoint path (categorical)
- Log level (categorical)
- HTTP status code (numerical)
- Response time (numerical)

Author: Engineering Log Intelligence Team
Date: October 17, 2025
"""

import logging
import pickle
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
from scipy.sparse import csr_matrix, hstack

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogClassifier:
    """
    A machine learning model that predicts business severity of log entries.
    
    This class handles:
    1. Loading pre-trained scikit-learn models (enhanced multi-feature)
    2. Predicting business severity (CRITICAL, HIGH, MEDIUM, LOW)
    3. Processing multiple feature types (text, categorical, numerical)
    4. Managing model lifecycle and caching
    5. Providing confidence scores and detailed predictions
    """
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize the business severity classifier.
        
        Args:
            model_dir: Directory containing the trained model files
        """
        self.model = None  # RandomForest classifier
        self.vectorizer = None  # TF-IDF vectorizer for text
        self.encoders = None  # Label encoders for categorical features
        self.metadata = None  # Model training metadata
        self.is_trained = False
        
        # Set up model paths (using enhanced multi-feature models)
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, 'severity_classifier_enhanced.pkl')
        self.vectorizer_path = os.path.join(model_dir, 'severity_vectorizer_enhanced.pkl')
        self.encoders_path = os.path.join(model_dir, 'severity_encoders_enhanced.pkl')
        self.metadata_path = os.path.join(model_dir, 'severity_metadata_enhanced.json')
        
        # Severity levels (business impact)
        self.severity_levels = ['critical', 'high', 'medium', 'low']
        
        logger.info(f"BusinessSeverityClassifier initialized (model_dir: {model_dir})")
    
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
        Load pre-trained enhanced multi-feature model from disk.
        
        For beginners: This loads the enhanced RandomForest model that was trained
        using train_models_severity_enhanced.py with 96.3% accuracy!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Loading enhanced multi-feature severity model...")
            
            # Check if model files exist
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found: {self.model_path}")
                return False
            
            if not os.path.exists(self.vectorizer_path):
                logger.error(f"Vectorizer file not found: {self.vectorizer_path}")
                return False
            
            if not os.path.exists(self.encoders_path):
                logger.error(f"Encoders file not found: {self.encoders_path}")
                return False
            
            # Load the trained classifier
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"✅ Loaded classifier from {self.model_path}")
            
            # Load the TF-IDF vectorizer (for text features)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            logger.info(f"✅ Loaded text vectorizer from {self.vectorizer_path}")
            
            # Load the label encoders (for categorical features)
            with open(self.encoders_path, 'rb') as f:
                self.encoders = pickle.load(f)
            logger.info(f"✅ Loaded feature encoders from {self.encoders_path}")
            
            # Load metadata (optional, for reporting accuracy)
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                accuracy = self.metadata.get('accuracy', 0) * 100
                logger.info(f"✅ Loaded metadata: {accuracy:.1f}% accuracy on {self.metadata.get('num_test_samples', 0)} test samples")
            
            self.is_trained = True
            logger.info("✅ Enhanced model loaded successfully and ready for severity predictions")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            self.is_trained = False
            return False
    
    def train(self, logs: List[Dict]) -> Dict[str, float]:
        """
        Train the business severity model.
        
        Note: This implementation uses pre-trained models. To retrain from scratch,
        use train_models_severity_enhanced.py in the project root.
        
        For beginners: We're using a pre-trained model, so this method just
        loads it rather than training from scratch.
        
        Args:
            logs: List of training log entries (unused - we load pre-trained model)
            
        Returns:
            Dictionary with training metrics
        """
        logger.info("Loading pre-trained enhanced severity model instead of training from scratch...")
        
        if self.load_pretrained_model():
            # Return metadata from the pre-trained model
            return {
                'training_samples': self.metadata.get('num_training_samples', 0) if self.metadata else 0,
                'test_samples': self.metadata.get('num_test_samples', 0) if self.metadata else 0,
                'accuracy': self.metadata.get('accuracy', 0.0) if self.metadata else 0.0,
                'total_features': self.metadata.get('total_features', 0) if self.metadata else 0,
                'model_type': 'RandomForest_MultiFeature (pre-trained)',
                'trained_at': self.metadata.get('trained_at', '') if self.metadata else '',
                'purpose': self.metadata.get('purpose', 'business_severity_prediction') if self.metadata else ''
            }
        else:
            raise RuntimeError("Failed to load pre-trained model. Run train_models_severity_enhanced.py first.")
    
    def predict(self, log_data: Dict) -> Dict[str, any]:
        """
        Predict the business severity using the enhanced multi-feature ML model.
        
        For beginners: This function uses the enhanced RandomForest model to predict
        business severity (CRITICAL, HIGH, MEDIUM, LOW) based on multiple features.
        
        Args:
            log_data: Dictionary containing:
                - message: The log message text (required)
                - service: Service name (default: 'unknown')
                - endpoint: API endpoint (default: 'unknown')
                - level: Log level (default: 'INFO')
                - http_status: HTTP status code (default: 200)
                - response_time_ms: Response time in ms (default: 0)
            
        Returns:
            Dictionary with prediction results including predicted_severity and confidence
        """
        # Auto-load model if not loaded yet
        if not self.is_trained:
            logger.info("Model not loaded, attempting to load...")
            if not self.load_pretrained_model():
                raise ValueError("Model must be loaded before making predictions. Run train_models_severity_enhanced.py first.")
        
        # Extract features with defaults
        message = log_data.get('message', '')
        service = log_data.get('service', log_data.get('source_type', 'unknown'))
        endpoint = log_data.get('endpoint', 'unknown')
        level = log_data.get('level', 'INFO').upper()
        http_status = log_data.get('http_status', log_data.get('status_code', 200))
        response_time = log_data.get('response_time_ms', log_data.get('response_time', 0))
        
        logger.info(f"Predicting severity: {service}/{endpoint} - {level} - {message[:50]}...")
        
        try:
            # Step 1: Vectorize the message text using TF-IDF
            X_text = self.vectorizer.transform([message])
            
            # Step 2: Encode categorical features (handle unknown categories gracefully)
            try:
                service_encoded = csr_matrix(
                    self.encoders['service_encoder'].transform([service]).reshape(-1, 1)
                )
            except ValueError:
                # Unknown service - use first known service as fallback
                logger.warning(f"Unknown service '{service}', using fallback")
                service_encoded = csr_matrix(
                    self.encoders['service_encoder'].transform([self.encoders['service_encoder'].classes_[0]]).reshape(-1, 1)
                )
            
            try:
                endpoint_encoded = csr_matrix(
                    self.encoders['endpoint_encoder'].transform([endpoint]).reshape(-1, 1)
                )
            except ValueError:
                # Unknown endpoint - use first known endpoint as fallback
                logger.warning(f"Unknown endpoint '{endpoint}', using fallback")
                endpoint_encoded = csr_matrix(
                    self.encoders['endpoint_encoder'].transform([self.encoders['endpoint_encoder'].classes_[0]]).reshape(-1, 1)
                )
            
            try:
                level_encoded = csr_matrix(
                    self.encoders['level_encoder'].transform([level]).reshape(-1, 1)
                )
            except ValueError:
                # Unknown level - use INFO as fallback
                logger.warning(f"Unknown level '{level}', using INFO fallback")
                level_encoded = csr_matrix(
                    self.encoders['level_encoder'].transform(['INFO']).reshape(-1, 1)
                )
            
            # Step 3: Prepare numerical features (standardized)
            http_status_normalized = http_status / 100.0  # Normalize to 0-10 range
            response_time_normalized = min(response_time / 1000.0, 10.0)  # Cap at 10 seconds
            
            # Apply the same scaling as training
            X_numerical_raw = [[http_status_normalized, response_time_normalized]]
            X_numerical_scaled = self.encoders['scaler'].transform(X_numerical_raw)
            X_numerical = csr_matrix(X_numerical_scaled)
            
            # Step 4: Combine all features
            X = hstack([
                X_text,
                service_encoded,
                endpoint_encoded,
                level_encoded,
                X_numerical
            ])
            
            # Step 5: Predict using the trained model
            predicted_severity = self.model.predict(X)[0]
            
            # Step 6: Get prediction probabilities for confidence score
            probabilities = self.model.predict_proba(X)[0]
            confidence = float(max(probabilities))  # Highest probability
            
            # Step 7: Get probability for each severity class
            class_probabilities = {}
            for severity, prob in zip(self.model.classes_, probabilities):
                class_probabilities[severity] = float(prob)
            
            result = {
                'predicted_severity': predicted_severity,
                'confidence': confidence,
                'severity_probabilities': class_probabilities,
                'features_used': {
                    'service': service,
                    'endpoint': endpoint,
                    'level': level,
                    'http_status': http_status,
                    'response_time_ms': response_time
                },
                'timestamp': datetime.now().isoformat(),
                'model_version': '2.0.0-enhanced',
                'model_type': 'RandomForest_MultiFeature'
            }
            
            logger.info(f"Prediction: {predicted_severity.upper()} (confidence: {confidence:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            logger.error(f"Feature values: service={service}, endpoint={endpoint}, level={level}")
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
        Get information about the current enhanced severity model.
        
        Returns:
            Dictionary with model information including real accuracy metrics
        """
        info = {
            'is_trained': self.is_trained,
            'severity_levels': self.severity_levels,
            'model_version': '2.0.0-enhanced',
            'model_type': 'RandomForest_MultiFeature',
            'last_checked': datetime.now().isoformat(),
            'purpose': 'business_severity_prediction'
        }
        
        # Add metadata if available
        if self.metadata:
            info.update({
                'accuracy': self.metadata.get('accuracy', 0.0),
                'training_samples': self.metadata.get('num_training_samples', 0),
                'test_samples': self.metadata.get('num_test_samples', 0),
                'total_features': self.metadata.get('total_features', 0),
                'feature_breakdown': self.metadata.get('feature_breakdown', {}),
                'trained_at': self.metadata.get('trained_at', '')
            })
        
        # Add model-specific info if loaded
        if self.model:
            info['n_estimators'] = getattr(self.model, 'n_estimators', 'N/A')
            info['n_features'] = getattr(self.model, 'n_features_in_', 'N/A')
            info['classes'] = list(self.model.classes_) if hasattr(self.model, 'classes_') else []
        
        return info
