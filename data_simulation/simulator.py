"""
Main data simulator for Engineering Log Intelligence System.
Coordinates multiple log generators and manages data simulation.
"""

import time
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import structlog

from .base_generator import BaseLogGenerator
from .splunk_generator import SplunkLogGenerator
from .sap_generator import SAPLogGenerator
from .application_generator import ApplicationLogGenerator

logger = structlog.get_logger(__name__)

class DataSimulator:
    """Main data simulator coordinator."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data simulator.
        
        Args:
            config: Configuration dictionary for the simulator
        """
        self.config = config
        self.generators: Dict[str, BaseLogGenerator] = {}
        self.is_running = False
        self.start_time = None
        self.total_logs_generated = 0
        
        # Initialize generators
        self._initialize_generators()
        
        logger.info(
            "Data simulator initialized",
            generators=list(self.generators.keys()),
            config_keys=list(config.keys())
        )
    
    def _initialize_generators(self):
        """Initialize all log generators."""
        # SPLUNK generator
        if self.config.get('enable_splunk', True):
            splunk_config = self.config.get('splunk', {})
            self.generators['splunk'] = SplunkLogGenerator(splunk_config)
        
        # SAP generator
        if self.config.get('enable_sap', True):
            sap_config = self.config.get('sap', {})
            self.generators['sap'] = SAPLogGenerator(sap_config)
        
        # Application generator
        if self.config.get('enable_application', True):
            app_config = self.config.get('application', {})
            self.generators['application'] = ApplicationLogGenerator(app_config)
    
    def start_simulation(self, duration_minutes: int = 60, logs_per_minute: int = 100):
        """
        Start the data simulation.
        
        Args:
            duration_minutes: Duration of simulation in minutes
            logs_per_minute: Target logs per minute
        """
        if self.is_running:
            logger.warning("Simulation already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now(timezone.utc)
        end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        logger.info(
            "Starting data simulation",
            duration_minutes=duration_minutes,
            logs_per_minute=logs_per_minute,
            generators=list(self.generators.keys())
        )
        
        try:
            while self.is_running and datetime.now(timezone.utc) < end_time:
                # Generate logs for this minute
                logs_this_minute = self._generate_logs_for_minute(logs_per_minute)
                
                # Log progress
                elapsed_minutes = (datetime.now(timezone.utc) - self.start_time).total_seconds() / 60
                logger.info(
                    "Simulation progress",
                    elapsed_minutes=round(elapsed_minutes, 1),
                    logs_this_minute=len(logs_this_minute),
                    total_logs=self.total_logs_generated
                )
                
                # Wait for next minute
                time.sleep(60)
        
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        except Exception as e:
            logger.error("Simulation error", error=str(e), exc_info=True)
        finally:
            self.stop_simulation()
    
    def stop_simulation(self):
        """Stop the data simulation."""
        self.is_running = False
        end_time = datetime.now(timezone.utc)
        
        if self.start_time:
            duration = (end_time - self.start_time).total_seconds() / 60
            
            logger.info(
                "Simulation stopped",
                duration_minutes=round(duration, 1),
                total_logs=self.total_logs_generated,
                avg_logs_per_minute=round(self.total_logs_generated / max(duration, 1), 1)
            )
    
    def _generate_logs_for_minute(self, target_logs: int) -> List[Dict[str, Any]]:
        """Generate logs for one minute."""
        all_logs = []
        
        # Distribute logs across generators
        generator_weights = self.config.get('generator_weights', {})
        if not generator_weights:
            # Equal distribution
            generator_weights = {name: 1.0 for name in self.generators.keys()}
        
        for generator_name, generator in self.generators.items():
            weight = generator_weights.get(generator_name, 1.0)
            logs_for_generator = int(target_logs * weight / sum(generator_weights.values()))
            
            if logs_for_generator > 0:
                try:
                    logs = generator.generate_batch(logs_for_generator)
                    all_logs.extend(logs)
                    self.total_logs_generated += len(logs)
                except Exception as e:
                    logger.error(
                        "Generator error",
                        generator=generator_name,
                        error=str(e)
                    )
        
        return all_logs
    
    def generate_sample_data(self, count: int = 1000) -> List[Dict[str, Any]]:
        """
        Generate a sample of log data.
        
        Args:
            count: Number of log entries to generate
            
        Returns:
            List of log entry dictionaries
        """
        all_logs = []
        
        # Distribute across generators
        generator_names = list(self.generators.keys())
        logs_per_generator = count // len(generator_names) if generator_names else 0
        remaining_logs = count % len(generator_names) if generator_names else 0
        
        for i, (generator_name, generator) in enumerate(self.generators.items()):
            logs_to_generate = logs_per_generator
            if i < remaining_logs:
                logs_to_generate += 1
            
            if logs_to_generate > 0:
                try:
                    logs = generator.generate_batch(logs_to_generate)
                    all_logs.extend(logs)
                except Exception as e:
                    logger.error(
                        "Sample generation error",
                        generator=generator_name,
                        error=str(e)
                    )
        
        logger.info(
            "Sample data generated",
            requested=count,
            generated=len(all_logs),
            generators=len(self.generators)
        )
        
        return all_logs
    
    def generate_anomalies(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate anomalous log entries.
        
        Args:
            count: Number of anomalies to generate
            
        Returns:
            List of anomalous log entry dictionaries
        """
        anomalies = []
        
        for _ in range(count):
            # Select random generator
            generator_name = random.choice(list(self.generators.keys()))
            generator = self.generators[generator_name]
            
            try:
                anomaly = generator.simulate_anomaly()
                anomalies.append(anomaly)
            except Exception as e:
                logger.error(
                    "Anomaly generation error",
                    generator=generator_name,
                    error=str(e)
                )
        
        logger.info(
            "Anomalies generated",
            requested=count,
            generated=len(anomalies)
        )
        
        return anomalies
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics."""
        generator_stats = {}
        for name, generator in self.generators.items():
            generator_stats[name] = generator.get_statistics()
        
        return {
            "simulator": {
                "is_running": self.is_running,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "total_logs_generated": self.total_logs_generated,
                "generators": list(self.generators.keys())
            },
            "generators": generator_stats
        }
    
    def get_generator(self, name: str) -> Optional[BaseLogGenerator]:
        """Get a specific generator by name."""
        return self.generators.get(name)
    
    def list_generators(self) -> List[str]:
        """List all available generators."""
        return list(self.generators.keys())

def create_default_config() -> Dict[str, Any]:
    """Create default configuration for the simulator."""
    return {
        "enable_splunk": True,
        "enable_sap": True,
        "enable_application": True,
        "generator_weights": {
            "splunk": 0.4,
            "sap": 0.3,
            "application": 0.3
        },
        "splunk": {
            "log_levels": ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"],
            "log_level_weights": [0.1, 0.7, 0.15, 0.04, 0.01],
            "categories": ["system", "application", "security", "network"],
            "hosts": ["web-server-01", "web-server-02", "db-server-01", "app-server-01"],
            "services": ["webapp", "database", "api", "auth", "scheduler"],
            "anomaly_rate": 0.05,
            "error_rate": 0.02,
            "environment": "development",
            "random_tags": ["production", "staging", "test", "critical", "monitoring"]
        },
        "sap": {
            "log_levels": ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"],
            "log_level_weights": [0.1, 0.7, 0.15, 0.04, 0.01],
            "categories": ["financial", "sales", "purchase", "inventory", "hr", "system", "security", "performance"],
            "hosts": ["sap-erp-01", "sap-crm-01", "sap-scm-01", "sap-hcm-01"],
            "services": ["sap_erp", "sap_crm", "sap_scm", "sap_hcm"],
            "anomaly_rate": 0.05,
            "error_rate": 0.02,
            "environment": "development",
            "random_tags": ["production", "staging", "test", "critical", "financial"]
        },
        "application": {
            "log_levels": ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"],
            "log_level_weights": [0.1, 0.7, 0.15, 0.04, 0.01],
            "categories": ["application", "security", "performance", "business"],
            "hosts": ["web-server-01", "api-server-01", "auth-server-01", "microservice-01"],
            "services": ["webapp", "api", "auth", "microservice"],
            "anomaly_rate": 0.05,
            "error_rate": 0.02,
            "environment": "development",
            "random_tags": ["production", "staging", "test", "critical", "api"]
        }
    }
