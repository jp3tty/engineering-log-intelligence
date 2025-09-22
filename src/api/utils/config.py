"""
Configuration utilities for the Engineering Log Intelligence System.
Handles environment variables and configuration management.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration management."""

    # Application settings
    APP_NAME = os.getenv("APP_NAME", "Engineering Log Intelligence System")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    # Vercel settings
    VERCEL_URL = os.getenv("VERCEL_URL", "localhost:3000")
    VERCEL_ENV = os.getenv("VERCEL_ENV", "development")

    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "log_intelligence_dev")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "dev_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "dev_password")

    # Elasticsearch configuration
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
    ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "logs_dev")

    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_LOGS = os.getenv("KAFKA_TOPIC_LOGS", "log-ingestion-dev")
    KAFKA_TOPIC_ALERTS = os.getenv("KAFKA_TOPIC_ALERTS", "alerts-dev")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "log-processor-dev")

    # Authentication configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # External services configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
    AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

    # ML services configuration
    ML_MODEL_BUCKET = os.getenv("ML_MODEL_BUCKET")
    ML_ENDPOINT_URL = os.getenv("ML_ENDPOINT_URL")

    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # Rate limiting configuration
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return validation results."""
        validation_results = {"valid": True, "errors": [], "warnings": []}

        # Required environment variables
        required_vars = [
            "DATABASE_URL",
            "ELASTICSEARCH_URL",
            "KAFKA_BOOTSTRAP_SERVERS",
            "JWT_SECRET_KEY",
        ]

        for var in required_vars:
            if not getattr(cls, var):
                validation_results["errors"].append(
                    f"Required environment variable {var} is not set"
                )
                validation_results["valid"] = False

        # Development-specific warnings
        if cls.ENVIRONMENT == "development":
            if cls.JWT_SECRET_KEY == "dev-secret-key":
                validation_results["warnings"].append(
                    "Using default JWT secret key in development"
                )

            if not cls.AWS_ACCESS_KEY_ID:
                validation_results["warnings"].append("AWS credentials not configured")

        # Production-specific validations
        if cls.ENVIRONMENT == "production":
            if cls.DEBUG:
                validation_results["warnings"].append(
                    "DEBUG mode enabled in production"
                )

            if cls.JWT_SECRET_KEY == "dev-secret-key":
                validation_results["errors"].append(
                    "Using default JWT secret key in production"
                )
                validation_results["valid"] = False

        return validation_results

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration as a dictionary."""
        return {
            "url": cls.DATABASE_URL,
            "host": cls.POSTGRES_HOST,
            "port": cls.POSTGRES_PORT,
            "database": cls.POSTGRES_DB,
            "user": cls.POSTGRES_USER,
            "password": cls.POSTGRES_PASSWORD,
        }

    @classmethod
    def get_elasticsearch_config(cls) -> Dict[str, Any]:
        """Get Elasticsearch configuration as a dictionary."""
        return {
            "url": cls.ELASTICSEARCH_URL,
            "username": cls.ELASTICSEARCH_USERNAME,
            "password": cls.ELASTICSEARCH_PASSWORD,
            "index": cls.ELASTICSEARCH_INDEX,
        }

    @classmethod
    def get_kafka_config(cls) -> Dict[str, Any]:
        """Get Kafka configuration as a dictionary."""
        return {
            "bootstrap_servers": cls.KAFKA_BOOTSTRAP_SERVERS,
            "logs_topic": cls.KAFKA_TOPIC_LOGS,
            "alerts_topic": cls.KAFKA_TOPIC_ALERTS,
            "group_id": cls.KAFKA_GROUP_ID,
        }

    @classmethod
    def get_auth_config(cls) -> Dict[str, Any]:
        """Get authentication configuration as a dictionary."""
        return {
            "secret_key": cls.JWT_SECRET_KEY,
            "algorithm": cls.JWT_ALGORITHM,
            "access_token_expire_minutes": cls.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        }

    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Get CORS configuration as a dictionary."""
        return {
            "origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def validate_environment() -> bool:
    """Validate the current environment configuration."""
    validation = config.validate_config()

    if validation["errors"]:
        logger.error("Configuration validation failed", errors=validation["errors"])
        return False

    if validation["warnings"]:
        logger.warning(
            "Configuration validation warnings", warnings=validation["warnings"]
        )

    logger.info("Configuration validation successful")
    return True
