"""
ML Service - Machine Learning Pipeline Coordinator
=================================================

This module coordinates all machine learning models and provides a unified
interface for ML operations in the log intelligence system.

For beginners: This is like a manager that coordinates all the AI models
and makes sure they work together properly.

Author: Engineering Log Intelligence Team
Date: September 21, 2025
"""

import logging
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

from .log_classifier import LogClassifier
from .anomaly_detector import AnomalyDetector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLService:
    """
    Main ML service that coordinates all machine learning operations.
    
    This service handles:
    1. Training all ML models
    2. Making predictions with multiple models
    3. Managing model versions and updates
    4. Providing unified ML API for the application
    """
    
    def __init__(self, model_storage_path: str = "models/"):
        """
        Initialize the ML service.
        
        For beginners: This sets up the ML service and tells it where to
        store the trained models.
        
        Args:
            model_storage_path: Directory to store trained models
        """
        self.model_storage_path = model_storage_path
        self.log_classifier = LogClassifier()
        self.anomaly_detector = AnomalyDetector()
        self.is_initialized = False
        
        # Create model storage directory if it doesn't exist
        os.makedirs(model_storage_path, exist_ok=True)
        
        logger.info(f"MLService initialized with storage path: {model_storage_path}")
    
    def initialize_models(self) -> bool:
        """
        Initialize all ML models.
        
        For beginners: This loads any previously trained models from disk
        so we can use them right away.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing ML models...")
            
            # Try to load existing models
            classifier_path = os.path.join(self.model_storage_path, "log_classifier.pkl")
            anomaly_path = os.path.join(self.model_storage_path, "anomaly_detector.pkl")
            
            # Load classifier if it exists
            if os.path.exists(classifier_path):
                self.log_classifier.load_model(classifier_path)
                logger.info("Log classifier loaded from disk")
            
            # Load anomaly detector if it exists
            if os.path.exists(anomaly_path):
                self.anomaly_detector.load_model(anomaly_path)
                logger.info("Anomaly detector loaded from disk")
            
            self.is_initialized = True
            logger.info("ML models initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            return False
    
    def train_all_models(self, training_data: List[Dict]) -> Dict[str, any]:
        """
        Train all ML models with the provided data.
        
        For beginners: This teaches all our AI models by showing them
        lots of examples of logs and what they should do with them.
        
        Args:
            training_data: List of log entries for training
            
        Returns:
            Dictionary with training results for all models
        """
        logger.info(f"Training all models with {len(training_data)} samples...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'training_samples': len(training_data),
            'models': {}
        }
        
        try:
            # Train log classifier
            logger.info("Training log classifier...")
            classifier_results = self.log_classifier.train(training_data)
            results['models']['log_classifier'] = classifier_results
            
            # Train anomaly detector
            logger.info("Training anomaly detector...")
            anomaly_results = self.anomaly_detector.train(training_data)
            results['models']['anomaly_detector'] = anomaly_results
            
            # Save trained models
            self.save_all_models()
            
            # Mark as initialized
            self.is_initialized = True
            
            logger.info("All models trained successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            raise
    
    def analyze_log(self, log_entry: Dict) -> Dict[str, any]:
        """
        Analyze a single log entry using all available models.
        
        For beginners: This takes a single log entry and runs it through
        all our AI models to get a complete analysis.
        
        Args:
            log_entry: Log entry to analyze
            
        Returns:
            Dictionary with complete analysis results
        """
        if not self.is_initialized:
            raise ValueError("ML service must be initialized before analyzing logs")
        
        logger.info(f"Analyzing log entry: {log_entry.get('message', '')[:50]}...")
        
        analysis = {
            'log_id': log_entry.get('log_id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        try:
            # Classify the log
            if self.log_classifier.is_trained:
                classification = self.log_classifier.predict(log_entry.get('message', ''))
                analysis['analysis']['classification'] = classification
            
            # Detect anomalies
            if self.anomaly_detector.is_trained:
                anomaly = self.anomaly_detector.detect_anomaly(log_entry)
                analysis['analysis']['anomaly'] = anomaly
            
            # Combine results
            analysis['summary'] = self._generate_analysis_summary(analysis['analysis'])
            
            logger.info(f"Log analysis completed for {log_entry.get('log_id', 'unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing log: {str(e)}")
            analysis['error'] = str(e)
            return analysis
    
    def analyze_logs_batch(self, log_entries: List[Dict]) -> List[Dict[str, any]]:
        """
        Analyze multiple log entries in batch.
        
        For beginners: This processes many logs at once, which is more
        efficient than analyzing them one by one.
        
        Args:
            log_entries: List of log entries to analyze
            
        Returns:
            List of analysis results
        """
        logger.info(f"Analyzing {len(log_entries)} log entries in batch...")
        
        results = []
        for log_entry in log_entries:
            try:
                analysis = self.analyze_log(log_entry)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing log {log_entry.get('log_id', 'unknown')}: {str(e)}")
                results.append({
                    'log_id': log_entry.get('log_id', 'unknown'),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.info(f"Batch analysis completed: {len(results)} results")
        return results
    
    def _generate_analysis_summary(self, analysis: Dict) -> Dict[str, any]:
        """
        Generate a summary of the analysis results.
        
        For beginners: This creates a simple summary that humans can
        easily understand, combining all the AI analysis results.
        """
        summary = {
            'risk_level': 'low',
            'action_required': False,
            'key_insights': []
        }
        
        # Check classification results
        if 'classification' in analysis:
            classification = analysis['classification']
            category = classification.get('category', 'unknown')
            confidence = classification.get('confidence', 0)
            
            if category in ['security', 'error'] and confidence > 0.8:
                summary['risk_level'] = 'high'
                summary['action_required'] = True
                summary['key_insights'].append(f"High-confidence {category} issue detected")
        
        # Check anomaly results
        if 'anomaly' in analysis:
            anomaly = analysis['anomaly']
            if anomaly.get('is_anomaly', False):
                anomaly_type = anomaly.get('anomaly_type', 'unknown')
                confidence = anomaly.get('confidence', 0)
                
                if confidence > 0.8:
                    summary['risk_level'] = 'high'
                    summary['action_required'] = True
                    summary['key_insights'].append(f"High-confidence {anomaly_type} anomaly detected")
                else:
                    summary['risk_level'] = 'medium'
                    summary['key_insights'].append(f"Potential {anomaly_type} anomaly detected")
        
        return summary
    
    def save_all_models(self) -> bool:
        """
        Save all trained models to disk.
        
        For beginners: This saves all our trained AI models so we can
        use them later without having to train them again.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Saving all models...")
            
            # Save log classifier
            classifier_path = os.path.join(self.model_storage_path, "log_classifier.pkl")
            self.log_classifier.save_model(classifier_path)
            
            # Save anomaly detector
            anomaly_path = os.path.join(self.model_storage_path, "anomaly_detector.pkl")
            self.anomaly_detector.save_model(anomaly_path)
            
            # Save service metadata
            metadata = {
                'version': '1.0.0',
                'last_updated': datetime.now().isoformat(),
                'models': {
                    'log_classifier': self.log_classifier.get_model_info(),
                    'anomaly_detector': self.anomaly_detector.get_model_info()
                }
            }
            
            metadata_path = os.path.join(self.model_storage_path, "ml_service_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("All models saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    def get_service_status(self) -> Dict[str, any]:
        """
        Get the current status of the ML service.
        
        Returns:
            Dictionary with service status information
        """
        return {
            'is_initialized': self.is_initialized,
            'log_classifier': self.log_classifier.get_model_info(),
            'anomaly_detector': self.anomaly_detector.get_model_info(),
            'model_storage_path': self.model_storage_path,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_anomaly_threshold(self, threshold: float) -> bool:
        """
        Update the anomaly detection threshold.
        
        For beginners: This changes how sensitive the anomaly detector is.
        Higher values mean it will only flag very unusual things.
        
        Args:
            threshold: New threshold value (0-1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.anomaly_detector.set_threshold(threshold)
            logger.info(f"Anomaly detection threshold updated to {threshold}")
            return True
        except Exception as e:
            logger.error(f"Error updating threshold: {str(e)}")
            return False
