"""
Elasticsearch connection utilities for the Engineering Log Intelligence System.
Handles Elasticsearch connections with error handling and retry logic.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)


class ElasticsearchManager:
    """Manages Elasticsearch connections and operations."""

    def __init__(self):
        self.client: Optional[Elasticsearch] = None
        self.index_name = os.getenv("ELASTICSEARCH_INDEX", "logs_dev")
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Elasticsearch client."""
        try:
            elasticsearch_url = os.getenv("ELASTICSEARCH_URL")
            username = os.getenv("ELASTICSEARCH_USERNAME")
            password = os.getenv("ELASTICSEARCH_PASSWORD")

            if not elasticsearch_url:
                raise ValueError("ELASTICSEARCH_URL environment variable not set")

            # Configure connection
            config = {
                "hosts": [elasticsearch_url],
                "timeout": 30,
                "max_retries": 3,
                "retry_on_timeout": True,
            }

            # Add authentication if provided
            if username and password:
                config["basic_auth"] = (username, password)

            self.client = Elasticsearch(**config)

            # Test connection
            if self.client.ping():
                logger.info("Elasticsearch client initialized successfully")
            else:
                raise ConnectionError("Failed to ping Elasticsearch")

        except Exception as e:
            logger.error("Failed to initialize Elasticsearch client", error=str(e))
            raise

    def health_check(self) -> Dict[str, Any]:
        """Check Elasticsearch health and return status information."""
        try:
            if not self.client:
                return {"status": "unhealthy", "error": "Client not initialized"}

            # Get cluster health
            health = self.client.cluster.health()

            return {
                "status": "healthy"
                if health["status"] in ["green", "yellow"]
                else "unhealthy",
                "cluster_status": health["status"],
                "number_of_nodes": health["number_of_nodes"],
                "active_shards": health["active_shards"],
                "relocating_shards": health["relocating_shards"],
                "initializing_shards": health["initializing_shards"],
                "unassigned_shards": health["unassigned_shards"],
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def create_index(self, index_name: str, mapping: Dict[str, Any] = None) -> bool:
        """Create an Elasticsearch index with optional mapping."""
        try:
            if not self.client:
                raise RuntimeError("Elasticsearch client not initialized")

            # Check if index already exists
            if self.client.indices.exists(index=index_name):
                logger.info(f"Index {index_name} already exists")
                return True

            # Create index with mapping
            body = {}
            if mapping:
                body["mappings"] = mapping

            self.client.indices.create(index=index_name, body=body)
            logger.info(f"Index {index_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create index {index_name}", error=str(e))
            return False

    def index_document(self, document: Dict[str, Any], doc_id: str = None) -> str:
        """Index a document in Elasticsearch."""
        try:
            if not self.client:
                raise RuntimeError("Elasticsearch client not initialized")

            response = self.client.index(
                index=self.index_name, body=document, id=doc_id
            )

            logger.info("Document indexed successfully", document_id=response["_id"])
            return response["_id"]

        except Exception as e:
            logger.error("Failed to index document", error=str(e))
            raise

    def search_documents(
        self, query: Dict[str, Any], size: int = 10, from_: int = 0
    ) -> Dict[str, Any]:
        """Search documents in Elasticsearch."""
        try:
            if not self.client:
                raise RuntimeError("Elasticsearch client not initialized")

            response = self.client.search(
                index=self.index_name, body=query, size=size, from_=from_
            )

            return {
                "hits": response["hits"]["hits"],
                "total": response["hits"]["total"]["value"],
                "max_score": response["hits"]["max_score"],
            }

        except Exception as e:
            logger.error("Failed to search documents", error=str(e))
            raise

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get a document by ID."""
        try:
            if not self.client:
                raise RuntimeError("Elasticsearch client not initialized")

            response = self.client.get(index=self.index_name, id=doc_id)

            return response["_source"]

        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}", error=str(e))
            raise

    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Update a document in Elasticsearch."""
        try:
            if not self.client:
                raise RuntimeError("Elasticsearch client not initialized")

            self.client.update(index=self.index_name, id=doc_id, body={"doc": document})

            logger.info(f"Document {doc_id} updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update document {doc_id}", error=str(e))
            return False

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from Elasticsearch."""
        try:
            if not self.client:
                raise RuntimeError("Elasticsearch client not initialized")

            self.client.delete(index=self.index_name, id=doc_id)

            logger.info(f"Document {doc_id} deleted successfully")
            return True

        except NotFoundError:
            logger.warning(f"Document {doc_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}", error=str(e))
            return False

    def bulk_index(self, documents: List[Dict[str, Any]]) -> bool:
        """Bulk index multiple documents."""
        try:
            if not self.client:
                raise RuntimeError("Elasticsearch client not initialized")

            from elasticsearch.helpers import bulk

            actions = []
            for doc in documents:
                action = {"_index": self.index_name, "_source": doc}
                if "id" in doc:
                    action["_id"] = doc["id"]
                actions.append(action)

            success, failed = bulk(self.client, actions)
            logger.info(f"Bulk indexed {success} documents, {len(failed)} failed")
            return len(failed) == 0

        except Exception as e:
            logger.error("Failed to bulk index documents", error=str(e))
            return False


# Global Elasticsearch manager instance
es_manager = ElasticsearchManager()


def get_elasticsearch_manager() -> ElasticsearchManager:
    """Get the global Elasticsearch manager instance."""
    return es_manager


# Convenience functions for common operations
def health_check() -> Dict[str, Any]:
    """Check Elasticsearch health using the global manager."""
    return es_manager.health_check()


def index_document(document: Dict[str, Any], doc_id: str = None) -> str:
    """Index a document using the global manager."""
    return es_manager.index_document(document, doc_id)


def search_documents(
    query: Dict[str, Any], size: int = 10, from_: int = 0
) -> Dict[str, Any]:
    """Search documents using the global manager."""
    return es_manager.search_documents(query, size, from_)
