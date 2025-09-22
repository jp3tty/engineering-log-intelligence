"""
Anomaly Detection Model
======================

This module implements a machine learning model that detects unusual patterns
in log data that might indicate problems or security issues.

For beginners: This is like having a smart security guard that watches for
unusual behavior and alerts you when something doesn't look right.

Author: Engineering Log Intelligence Team
Date: September 21, 2025
"""

import logging
import pickle
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import statistics

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    A machine learning model that detects anomalies in log data.
    
    This class handles:
    1. Learning normal patterns from historical data
    2. Detecting unusual patterns in new log entries
    3. Calculating anomaly scores and confidence levels
    4. Providing explanations for detected anomalies
    """
    
    def __init__(self):
        """Initialize the anomaly detector."""
        self.model = None
        self.is_trained = False
        self.normal_patterns = {}
        self.threshold = 0.7  # Anomaly threshold (0-1, higher = more sensitive)
        self.anomaly_types = [
            'unusual_frequency',    # Too many/few logs of a certain type
            'unusual_timing',       # Logs at unexpected times
            'unusual_content',      # Log content that's different from normal
            'unusual_source',       # Logs from unexpected sources
            'unusual_pattern',      # Unusual sequence of log events
            'security_anomaly',     # Potential security threats
            'performance_anomaly'   # Performance issues
        ]
        
        logger.info(f"AnomalyDetector initialized with {len(self.anomaly_types)} anomaly types")
    
    def prepare_training_data(self, logs: List[Dict]) -> Dict[str, List]:
        """
        Prepare training data by analyzing normal patterns.
        
        For beginners: This function looks at historical log data to learn
        what "normal" looks like, so it can later detect when something is unusual.
        
        Args:
            logs: List of historical log entries
            
        Returns:
            Dictionary with learned normal patterns
        """
        logger.info(f"Analyzing {len(logs)} log entries for normal patterns...")
        
        patterns = {
            'frequency_by_hour': {},
            'frequency_by_source': {},
            'common_messages': {},
            'response_times': [],
            'error_rates': [],
            'ip_addresses': set(),
            'user_agents': set()
        }
        
        # Analyze patterns in the data
        for log in logs:
            timestamp = log.get('timestamp', datetime.now())
            hour = timestamp.hour if isinstance(timestamp, datetime) else 0
            
            # Track frequency by hour
            patterns['frequency_by_hour'][hour] = patterns['frequency_by_hour'].get(hour, 0) + 1
            
            # Track frequency by source
            source = log.get('source_type', 'unknown')
            patterns['frequency_by_source'][source] = patterns['frequency_by_source'].get(source, 0) + 1
            
            # Track common messages
            message = log.get('message', '')
            if message:
                patterns['common_messages'][message] = patterns['common_messages'].get(message, 0) + 1
            
            # Track response times
            if 'response_time_ms' in log:
                patterns['response_times'].append(log['response_time_ms'])
            
            # Track IP addresses
            if 'ip_address' in log:
                patterns['ip_addresses'].add(log['ip_address'])
            
            # Track user agents
            if 'user_agent' in log:
                patterns['user_agents'].add(log['user_agent'])
        
        # Calculate statistics
        if patterns['response_times']:
            patterns['avg_response_time'] = statistics.mean(patterns['response_times'])
            patterns['response_time_std'] = statistics.stdev(patterns['response_times'])
        else:
            patterns['avg_response_time'] = 0
            patterns['response_time_std'] = 0
        
        logger.info(f"Learned patterns from {len(logs)} logs")
        return patterns
    
    def train(self, logs: List[Dict]) -> Dict[str, float]:
        """
        Train the anomaly detection model on historical data.
        
        For beginners: This teaches the model what normal behavior looks like
        by analyzing lots of historical log data.
        
        Args:
            logs: List of historical log entries
            
        Returns:
            Dictionary with training metrics
        """
        logger.info("Starting anomaly detection model training...")
        
        try:
            # Learn normal patterns
            self.normal_patterns = self.prepare_training_data(logs)
            self.is_trained = True
            
            # Calculate training metrics
            metrics = {
                'training_samples': len(logs),
                'anomaly_types': len(self.anomaly_types),
                'threshold': self.threshold,
                'training_time': 1.2  # Simulated training time
            }
            
            logger.info(f"Anomaly detection model training completed")
            return metrics
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
    
    def detect_anomaly(self, log: Dict) -> Dict[str, any]:
        """
        Detect if a log entry is anomalous.
        
        For beginners: This function looks at a new log entry and decides
        if it's unusual compared to what we've seen before.
        
        Args:
            log: Log entry to analyze
            
        Returns:
            Dictionary with anomaly detection results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        logger.info(f"Analyzing log for anomalies: {log.get('message', '')[:50]}...")
        
        # Calculate anomaly scores for different aspects
        scores = self._calculate_anomaly_scores(log)
        
        # Determine if this is an anomaly
        max_score = max(scores.values()) if scores else 0
        is_anomaly = max_score > self.threshold
        
        # Determine anomaly type
        anomaly_type = max(scores, key=scores.get) if scores else 'none'
        
        result = {
            'is_anomaly': is_anomaly,
            'anomaly_type': anomaly_type if is_anomaly else 'none',
            'confidence': max_score,
            'scores': scores,
            'timestamp': datetime.now().isoformat(),
            'explanation': self._generate_explanation(log, scores, is_anomaly)
        }
        
        if is_anomaly:
            logger.warning(f"Anomaly detected: {anomaly_type} (confidence: {max_score:.2%})")
        else:
            logger.info(f"No anomaly detected (max score: {max_score:.2%})")
        
        return result
    
    def _calculate_anomaly_scores(self, log: Dict) -> Dict[str, float]:
        """
        Calculate anomaly scores for different aspects of the log.
        
        For beginners: This function checks different aspects of the log
        (timing, content, source, etc.) and gives each a score from 0-1
        where higher scores mean more unusual.
        """
        scores = {}
        
        # Check timing anomaly
        timestamp = log.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        
        hour = timestamp.hour
        expected_frequency = self.normal_patterns['frequency_by_hour'].get(hour, 0)
        total_logs = sum(self.normal_patterns['frequency_by_hour'].values())
        expected_rate = expected_frequency / total_logs if total_logs > 0 else 0
        
        # If this hour normally has very few logs, it's unusual
        scores['unusual_timing'] = 1.0 - expected_rate if expected_rate < 0.1 else 0.0
        
        # Check source anomaly
        source = log.get('source_type', 'unknown')
        source_frequency = self.normal_patterns['frequency_by_source'].get(source, 0)
        total_sources = sum(self.normal_patterns['frequency_by_source'].values())
        source_rate = source_frequency / total_sources if total_sources > 0 else 0
        
        scores['unusual_source'] = 1.0 - source_rate if source_rate < 0.05 else 0.0
        
        # Check content anomaly
        message = log.get('message', '')
        message_frequency = self.normal_patterns['common_messages'].get(message, 0)
        total_messages = sum(self.normal_patterns['common_messages'].values())
        message_rate = message_frequency / total_messages if total_messages > 0 else 0
        
        scores['unusual_content'] = 1.0 - message_rate if message_rate < 0.01 else 0.0
        
        # Check response time anomaly
        response_time = log.get('response_time_ms', 0)
        if response_time > 0 and self.normal_patterns['avg_response_time'] > 0:
            avg_time = self.normal_patterns['avg_response_time']
            std_time = self.normal_patterns['response_time_std']
            
            # If response time is more than 2 standard deviations from average
            if std_time > 0:
                z_score = abs(response_time - avg_time) / std_time
                scores['performance_anomaly'] = min(z_score / 3.0, 1.0)  # Normalize to 0-1
            else:
                scores['performance_anomaly'] = 0.0
        else:
            scores['performance_anomaly'] = 0.0
        
        # Check security anomaly (simple keyword-based)
        message_lower = message.lower()
        security_keywords = ['breach', 'attack', 'unauthorized', 'hack', 'malware', 'virus']
        security_score = sum(1 for keyword in security_keywords if keyword in message_lower)
        scores['security_anomaly'] = min(security_score / len(security_keywords), 1.0)
        
        # Check IP address anomaly
        ip_address = log.get('ip_address', '')
        if ip_address and ip_address not in self.normal_patterns['ip_addresses']:
            scores['unusual_source'] = max(scores.get('unusual_source', 0), 0.8)
        
        return scores
    
    def _generate_explanation(self, log: Dict, scores: Dict[str, float], is_anomaly: bool) -> str:
        """
        Generate a human-readable explanation of the anomaly detection result.
        
        For beginners: This creates a simple explanation of why the system
        thinks something is unusual, so humans can understand what's happening.
        """
        if not is_anomaly:
            return "This log entry appears normal based on historical patterns."
        
        explanations = []
        
        for anomaly_type, score in scores.items():
            if score > self.threshold:
                if anomaly_type == 'unusual_timing':
                    explanations.append(f"Unusual timing (score: {score:.2f}) - logs at this time are rare")
                elif anomaly_type == 'unusual_source':
                    explanations.append(f"Unusual source (score: {score:.2f}) - this source type is uncommon")
                elif anomaly_type == 'unusual_content':
                    explanations.append(f"Unusual content (score: {score:.2f}) - this message is rarely seen")
                elif anomaly_type == 'performance_anomaly':
                    explanations.append(f"Performance issue (score: {score:.2f}) - response time is unusual")
                elif anomaly_type == 'security_anomaly':
                    explanations.append(f"Security concern (score: {score:.2f}) - contains security-related keywords")
        
        return "; ".join(explanations) if explanations else "Anomaly detected but no specific explanation available."
    
    def set_threshold(self, threshold: float) -> None:
        """
        Set the anomaly detection threshold.
        
        For beginners: This controls how sensitive the system is. Higher values
        mean it will only flag very unusual things, lower values mean it will
        flag more things as potentially unusual.
        
        Args:
            threshold: Threshold value between 0 and 1
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        self.threshold = threshold
        logger.info(f"Anomaly detection threshold set to {threshold}")
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'is_trained': self.is_trained,
            'threshold': self.threshold,
            'anomaly_types': self.anomaly_types,
            'model_version': '1.0.0',
            'last_updated': datetime.now().isoformat()
        }
