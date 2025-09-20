"""
Kafka connection utilities for the Engineering Log Intelligence System.
Handles Kafka connections with error handling and retry logic.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)


class KafkaManager:
    """Manages Kafka connections and operations."""

    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.logs_topic = os.getenv("KAFKA_TOPIC_LOGS", "log-ingestion-dev")
        self.alerts_topic = os.getenv("KAFKA_TOPIC_ALERTS", "alerts-dev")
        self.group_id = os.getenv("KAFKA_GROUP_ID", "log-processor-dev")
        self.producer = None
        self.consumer = None
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize Kafka producer and consumer connections."""
        try:
            # Import kafka modules
            from kafka import KafkaProducer, KafkaConsumer
            from kafka.errors import KafkaError

            # Initialize producer
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=lambda x: json.dumps(x).encode("utf-8"),
                key_serializer=lambda x: x.encode("utf-8") if x else None,
                retries=3,
                retry_backoff_ms=100,
                request_timeout_ms=30000,
            )

            # Initialize consumer
            self.consumer = KafkaConsumer(
                self.logs_topic,
                bootstrap_servers=[self.bootstrap_servers],
                group_id=self.group_id,
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                key_deserializer=lambda x: x.decode("utf-8") if x else None,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                consumer_timeout_ms=1000,
            )

            logger.info("Kafka connections initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize Kafka connections", error=str(e))
            # Don't raise exception to allow graceful degradation

    def health_check(self) -> Dict[str, Any]:
        """Check Kafka health and return status information."""
        try:
            if not self.producer:
                return {"status": "unhealthy", "error": "Producer not initialized"}

            # Test producer connection
            future = self.producer.send("health-check", {"test": "message"})
            future.get(timeout=5)

            return {
                "status": "healthy",
                "bootstrap_servers": self.bootstrap_servers,
                "logs_topic": self.logs_topic,
                "alerts_topic": self.alerts_topic,
                "group_id": self.group_id,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def send_log_message(self, log_data: Dict[str, Any], key: str = None) -> bool:
        """Send a log message to the logs topic."""
        try:
            if not self.producer:
                logger.error("Kafka producer not initialized")
                return False

            # Add timestamp if not present
            if "timestamp" not in log_data:
                log_data["timestamp"] = datetime.utcnow().isoformat()

            # Send message
            future = self.producer.send(self.logs_topic, value=log_data, key=key)

            # Wait for confirmation
            future.get(timeout=10)
            logger.info("Log message sent successfully", topic=self.logs_topic)
            return True

        except Exception as e:
            logger.error("Failed to send log message", error=str(e))
            return False

    def send_alert_message(self, alert_data: Dict[str, Any], key: str = None) -> bool:
        """Send an alert message to the alerts topic."""
        try:
            if not self.producer:
                logger.error("Kafka producer not initialized")
                return False

            # Add timestamp if not present
            if "timestamp" not in alert_data:
                alert_data["timestamp"] = datetime.utcnow().isoformat()

            # Send message
            future = self.producer.send(self.alerts_topic, value=alert_data, key=key)

            # Wait for confirmation
            future.get(timeout=10)
            logger.info("Alert message sent successfully", topic=self.alerts_topic)
            return True

        except Exception as e:
            logger.error("Failed to send alert message", error=str(e))
            return False

    def consume_log_messages(self, timeout_ms: int = 1000) -> List[Dict[str, Any]]:
        """Consume log messages from the logs topic."""
        try:
            if not self.consumer:
                logger.error("Kafka consumer not initialized")
                return []

            messages = []
            for message in self.consumer:
                messages.append(
                    {
                        "topic": message.topic,
                        "partition": message.partition,
                        "offset": message.offset,
                        "key": message.key,
                        "value": message.value,
                        "timestamp": message.timestamp,
                    }
                )

                # Limit batch size
                if len(messages) >= 100:
                    break

            logger.info(f"Consumed {len(messages)} log messages")
            return messages

        except Exception as e:
            logger.error("Failed to consume log messages", error=str(e))
            return []

    def create_topic(
        self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1
    ) -> bool:
        """Create a Kafka topic."""
        try:
            from kafka.admin import KafkaAdminClient, NewTopic

            admin_client = KafkaAdminClient(bootstrap_servers=[self.bootstrap_servers])

            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            )

            admin_client.create_topics([topic])
            logger.info(f"Topic {topic_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create topic {topic_name}", error=str(e))
            return False

    def get_topic_metadata(self, topic_name: str) -> Dict[str, Any]:
        """Get metadata for a Kafka topic."""
        try:
            from kafka.admin import KafkaAdminClient

            admin_client = KafkaAdminClient(bootstrap_servers=[self.bootstrap_servers])

            metadata = admin_client.describe_topics([topic_name])
            return metadata.get(topic_name, {})

        except Exception as e:
            logger.error(f"Failed to get metadata for topic {topic_name}", error=str(e))
            return {}

    def close_connections(self):
        """Close Kafka connections."""
        try:
            if self.producer:
                self.producer.close()
                logger.info("Kafka producer closed")

            if self.consumer:
                self.consumer.close()
                logger.info("Kafka consumer closed")

        except Exception as e:
            logger.error("Error closing Kafka connections", error=str(e))


# Global Kafka manager instance
kafka_manager = KafkaManager()


def get_kafka_manager() -> KafkaManager:
    """Get the global Kafka manager instance."""
    return kafka_manager


# Convenience functions for common operations
def health_check() -> Dict[str, Any]:
    """Check Kafka health using the global manager."""
    return kafka_manager.health_check()


def send_log_message(log_data: Dict[str, Any], key: str = None) -> bool:
    """Send a log message using the global manager."""
    return kafka_manager.send_log_message(log_data, key)


def send_alert_message(alert_data: Dict[str, Any], key: str = None) -> bool:
    """Send an alert message using the global manager."""
    return kafka_manager.send_alert_message(alert_data, key)
