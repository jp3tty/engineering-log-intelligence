"""
Base log generator class for data simulation.
Provides common functionality for all log generators.
"""

import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)

class BaseLogGenerator:
    """Base class for all log generators."""
    
    def __init__(self, source_type: str, config: Dict[str, Any]):
        """
        Initialize the log generator.
        
        Args:
            source_type: Type of log source (splunk, sap, application, etc.)
            config: Configuration dictionary for the generator
        """
        self.source_type = source_type
        self.config = config
        self.log_id_counter = 0
        self.start_time = datetime.now(timezone.utc)
        
        # Load configuration
        self.log_levels = config.get('log_levels', ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'])
        self.log_level_weights = config.get('log_level_weights', [0.1, 0.7, 0.15, 0.04, 0.01])
        self.categories = config.get('categories', ['system', 'application', 'security', 'network'])
        self.hosts = config.get('hosts', ['server-01', 'server-02', 'server-03'])
        self.services = config.get('services', ['webapp', 'database', 'api', 'auth'])
        
        # Anomaly configuration
        self.anomaly_rate = config.get('anomaly_rate', 0.05)  # 5% anomaly rate
        self.error_rate = config.get('error_rate', 0.02)  # 2% error rate
        
        logger.info(
            "Log generator initialized",
            source_type=source_type,
            config_keys=list(config.keys())
        )
    
    def generate_log_id(self) -> str:
        """Generate a unique log ID."""
        self.log_id_counter += 1
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        return f"{self.source_type}-{timestamp}-{self.log_id_counter:06d}"
    
    def generate_timestamp(self, base_time: Optional[datetime] = None) -> str:
        """
        Generate a realistic timestamp.
        
        Args:
            base_time: Base time for timestamp generation
            
        Returns:
            ISO format timestamp string
        """
        if base_time is None:
            base_time = datetime.now(timezone.utc)
        
        # Add some random variation (±5 minutes)
        variation = timedelta(minutes=random.randint(-5, 5))
        timestamp = base_time + variation
        
        return timestamp.isoformat()
    
    def select_log_level(self) -> str:
        """Select a log level based on configured weights."""
        return random.choices(self.log_levels, weights=self.log_level_weights)[0]
    
    def select_category(self) -> str:
        """Select a random category."""
        return random.choice(self.categories)
    
    def select_host(self) -> str:
        """Select a random host."""
        return random.choice(self.hosts)
    
    def select_service(self) -> str:
        """Select a random service."""
        return random.choice(self.services)
    
    def should_generate_anomaly(self) -> bool:
        """Determine if an anomaly should be generated."""
        return random.random() < self.anomaly_rate
    
    def should_generate_error(self) -> bool:
        """Determine if an error should be generated."""
        return random.random() < self.error_rate
    
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata for the log entry."""
        return {
            "generator": self.source_type,
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "host": self.select_host(),
            "service": self.select_service(),
            "environment": self.config.get('environment', 'development')
        }
    
    def generate_tags(self) -> List[str]:
        """Generate tags for the log entry."""
        tags = [self.source_type, self.select_category()]
        
        # Add random tags
        random_tags = self.config.get('random_tags', [])
        if random_tags:
            num_tags = random.randint(0, min(3, len(random_tags)))
            tags.extend(random.sample(random_tags, num_tags))
        
        return tags
    
    def generate_log(self) -> Dict[str, Any]:
        """
        Generate a single log entry.
        Must be implemented by subclasses.
        
        Returns:
            Dictionary containing log entry data
        """
        raise NotImplementedError("Subclasses must implement generate_log method")
    
    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """
        Generate multiple log entries.
        
        Args:
            count: Number of log entries to generate
            
        Returns:
            List of log entry dictionaries
        """
        logs = []
        for _ in range(count):
            try:
                log_entry = self.generate_log()
                logs.append(log_entry)
            except Exception as e:
                logger.error("Failed to generate log entry", error=str(e))
                continue
        
        logger.info(
            "Generated log batch",
            count=len(logs),
            requested=count,
            source_type=self.source_type
        )
        
        return logs
    
    def simulate_anomaly(self) -> Dict[str, Any]:
        """
        Generate an anomalous log entry.
        Must be implemented by subclasses.
        
        Returns:
            Dictionary containing anomalous log entry data
        """
        raise NotImplementedError("Subclasses must implement simulate_anomaly method")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generator statistics."""
        return {
            "source_type": self.source_type,
            "logs_generated": self.log_id_counter,
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "log_levels": self.log_levels,
                "log_level_weights": self.log_level_weights,
                "categories": self.categories,
                "hosts": self.hosts,
                "services": self.services,
                "anomaly_rate": self.anomaly_rate,
                "error_rate": self.error_rate
            }
        }
