"""
Real-time Log Processor
======================

This module handles real-time log processing by consuming logs from Kafka
and analyzing them with our ML models as they arrive.

For beginners: This is like having a smart assistant that watches your
system logs 24/7 and immediately tells you when something important happens.

Author: Engineering Log Intelligence Team
Date: September 22, 2025
"""

import json
import logging
import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import time

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from .ml_service import MLService
from .ml_monitoring import MLMonitoring

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingStats:
    """Statistics for real-time processing."""
    logs_processed: int = 0
    logs_per_second: float = 0.0
    average_processing_time: float = 0.0
    errors_count: int = 0
    start_time: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

class RealTimeProcessor:
    """
    Real-time log processor that consumes logs from Kafka and analyzes them.
    
    This processor:
    1. Listens to Kafka topics for new log entries
    2. Processes logs through ML models in real-time
    3. Sends alerts for high-priority issues
    4. Monitors performance and health
    """
    
    def __init__(self, kafka_config: Dict, ml_service: MLService):
        """
        Initialize the real-time processor.
        
        For beginners: This sets up the processor with the configuration
        it needs to connect to Kafka and use our AI models.
        
        Args:
            kafka_config: Configuration for Kafka connection
            ml_service: Our ML service for analyzing logs
        """
        self.kafka_config = kafka_config
        self.ml_service = ml_service
        self.monitoring = MLMonitoring()
        self.stats = ProcessingStats()
        self.is_running = False
        self.callbacks = []
        
        # Performance tracking
        self.processing_times = []
        self.last_stats_update = time.time()
        
        logger.info("Real-time processor initialized")
    
    def add_callback(self, callback: Callable[[Dict], None]):
        """
        Add a callback function to be called when logs are processed.
        
        For beginners: This lets other parts of our system know when
        important things are detected in the logs.
        
        Args:
            callback: Function to call with processed log data
        """
        self.callbacks.append(callback)
        logger.info(f"Added callback: {callback.__name__}")
    
    async def start_processing(self, topics: List[str]):
        """
        Start real-time processing of logs from Kafka topics.
        
        For beginners: This starts the processor and tells it to listen
        to specific Kafka topics for new log entries.
        
        Args:
            topics: List of Kafka topics to consume from
        """
        logger.info(f"Starting real-time processing for topics: {topics}")
        self.is_running = True
        self.stats.start_time = datetime.now()
        
        try:
            # In a real implementation, this would connect to Kafka
            # For now, we'll simulate real-time processing
            await self._simulate_real_time_processing(topics)
            
        except Exception as e:
            logger.error(f"Error in real-time processing: {str(e)}")
            self.is_running = False
            raise
    
    async def _simulate_real_time_processing(self, topics: List[str]):
        """
        Simulate real-time processing for demonstration.
        
        For beginners: This simulates what would happen in a real system
        where logs come in continuously from Kafka.
        """
        logger.info("Starting simulated real-time processing...")
        
        # Generate sample logs to simulate real-time data
        sample_logs = self._generate_sample_logs(50)
        
        for i, log_entry in enumerate(sample_logs):
            if not self.is_running:
                break
                
            try:
                # Process the log entry
                start_time = time.time()
                result = await self._process_log_entry(log_entry)
                processing_time = time.time() - start_time
                
                # Update statistics
                self._update_stats(processing_time)
                
                # Call callbacks
                for callback in self.callbacks:
                    try:
                        callback(result)
                    except Exception as e:
                        logger.error(f"Error in callback {callback.__name__}: {str(e)}")
                
                # Log progress
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1} logs, {self.stats.logs_per_second:.2f} logs/sec")
                
                # Simulate real-time delay
                await asyncio.sleep(0.1)  # 100ms delay between logs
                
            except Exception as e:
                logger.error(f"Error processing log {i}: {str(e)}")
                self.stats.errors_count += 1
        
        logger.info("Real-time processing simulation completed")
    
    async def _process_log_entry(self, log_entry: Dict) -> Dict:
        """
        Process a single log entry through our ML pipeline.
        
        For beginners: This takes one log entry and runs it through
        all our AI models to get a complete analysis.
        
        Args:
            log_entry: Log entry to process
            
        Returns:
            Complete analysis result
        """
        try:
            # Analyze the log entry
            analysis = self.ml_service.analyze_log(log_entry)
            
            # Add real-time processing metadata
            analysis['real_time_processing'] = {
                'processed_at': datetime.now().isoformat(),
                'processing_time_ms': (time.time() - analysis.get('timestamp', time.time())) * 1000,
                'queue_position': self.stats.logs_processed
            }
            
            # Check if this is a high-priority issue
            if self._is_high_priority(analysis):
                analysis['alert_triggered'] = True
                analysis['alert_level'] = self._determine_alert_level(analysis)
                logger.warning(f"High-priority issue detected: {analysis['log_id']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing log entry: {str(e)}")
            return {
                'log_id': log_entry.get('log_id', 'unknown'),
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    def _is_high_priority(self, analysis: Dict) -> bool:
        """
        Check if the analysis result indicates a high-priority issue.
        
        For beginners: This determines if the log entry contains something
        important that needs immediate attention.
        """
        summary = analysis.get('summary', {})
        
        # Check risk level
        if summary.get('risk_level') == 'high':
            return True
        
        # Check if action is required
        if summary.get('action_required', False):
            return True
        
        # Check for specific high-priority categories
        analysis_data = analysis.get('analysis', {})
        classification = analysis_data.get('classification', {})
        
        if classification.get('category') in ['security', 'error'] and classification.get('confidence', 0) > 0.8:
            return True
        
        # Check for anomalies
        anomaly = analysis_data.get('anomaly', {})
        if anomaly.get('is_anomaly', False) and anomaly.get('confidence', 0) > 0.8:
            return True
        
        return False
    
    def _determine_alert_level(self, analysis: Dict) -> str:
        """
        Determine the alert level for the analysis result.
        
        For beginners: This decides how urgent the issue is and what
        kind of alert should be sent.
        """
        summary = analysis.get('summary', {})
        analysis_data = analysis.get('analysis', {})
        
        # Critical level
        if summary.get('risk_level') == 'high':
            classification = analysis_data.get('classification', {})
            if classification.get('category') == 'security' and classification.get('confidence', 0) > 0.9:
                return 'critical'
            return 'high'
        
        # Medium level
        if summary.get('risk_level') == 'medium':
            return 'medium'
        
        # Low level
        return 'low'
    
    def _update_stats(self, processing_time: float):
        """
        Update processing statistics.
        
        For beginners: This keeps track of how well our system is performing
        so we can monitor it and make improvements.
        """
        self.stats.logs_processed += 1
        self.processing_times.append(processing_time)
        
        # Keep only last 100 processing times for average calculation
        if len(self.processing_times) > 100:
            self.processing_times = self.processing_times[-100:]
        
        # Update average processing time
        self.stats.average_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        # Update logs per second
        current_time = time.time()
        time_elapsed = current_time - self.last_stats_update
        
        if time_elapsed >= 1.0:  # Update every second
            self.stats.logs_per_second = self.stats.logs_processed / (current_time - self.stats.start_time.timestamp())
            self.last_stats_update = current_time
    
    def _generate_sample_logs(self, count: int) -> List[Dict]:
        """
        Generate sample logs for demonstration.
        
        For beginners: This creates fake log entries that look like real ones
        so we can test our system without needing real data.
        """
        sample_logs = []
        
        # Different types of logs to simulate
        log_types = [
            {
                'message': 'User authentication successful',
                'level': 'INFO',
                'source_type': 'application',
                'category': 'authentication'
            },
            {
                'message': 'Database connection timeout after 30 seconds',
                'level': 'ERROR',
                'source_type': 'application',
                'category': 'database'
            },
            {
                'message': 'Unauthorized access attempt from IP 192.168.1.100',
                'level': 'WARN',
                'source_type': 'security',
                'category': 'security'
            },
            {
                'message': 'High CPU usage detected: 95%',
                'level': 'WARN',
                'source_type': 'system',
                'category': 'performance'
            },
            {
                'message': 'Application started successfully',
                'level': 'INFO',
                'source_type': 'application',
                'category': 'system'
            }
        ]
        
        for i in range(count):
            log_type = log_types[i % len(log_types)]
            
            log_entry = {
                'log_id': f'realtime_{i}_{int(time.time())}',
                'timestamp': datetime.now().isoformat(),
                'message': log_type['message'],
                'level': log_type['level'],
                'source_type': log_type['source_type'],
                'host': f'host-{i % 5}',
                'service': f'service-{i % 3}',
                'raw_log': f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{log_type['level']}] {log_type['message']}",
                'structured_data': {
                    'category': log_type['category'],
                    'request_id': f'req_{i}',
                    'session_id': f'session_{i % 10}'
                }
            }
            
            sample_logs.append(log_entry)
        
        return sample_logs
    
    def stop_processing(self):
        """
        Stop the real-time processing.
        
        For beginners: This safely stops the processor when we want to
        shut down the system.
        """
        logger.info("Stopping real-time processing...")
        self.is_running = False
    
    def get_processing_stats(self) -> Dict:
        """
        Get current processing statistics.
        
        For beginners: This gives us information about how well our
        system is performing in real-time.
        """
        return {
            'is_running': self.is_running,
            'logs_processed': self.stats.logs_processed,
            'logs_per_second': self.stats.logs_per_second,
            'average_processing_time': self.stats.average_processing_time,
            'errors_count': self.stats.errors_count,
            'uptime_seconds': (datetime.now() - self.stats.start_time).total_seconds() if self.stats.start_time else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_health_status(self) -> Dict:
        """
        Get the health status of the real-time processor.
        
        For beginners: This tells us if our system is healthy and working
        properly, or if there are any problems.
        """
        stats = self.get_processing_stats()
        
        # Determine health status
        health_status = 'healthy'
        issues = []
        
        # Check error rate
        if stats['errors_count'] > 0:
            error_rate = stats['errors_count'] / max(stats['logs_processed'], 1)
            if error_rate > 0.1:  # More than 10% error rate
                health_status = 'unhealthy'
                issues.append(f"High error rate: {error_rate:.2%}")
        
        # Check processing speed
        if stats['logs_per_second'] < 1.0:  # Less than 1 log per second
            health_status = 'degraded'
            issues.append(f"Low processing speed: {stats['logs_per_second']:.2f} logs/sec")
        
        # Check average processing time
        if stats['average_processing_time'] > 1.0:  # More than 1 second per log
            health_status = 'degraded'
            issues.append(f"Slow processing: {stats['average_processing_time']:.2f}s per log")
        
        return {
            'status': health_status,
            'issues': issues,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }
