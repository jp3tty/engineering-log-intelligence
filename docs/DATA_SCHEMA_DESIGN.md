# Data Schema Design - Engineering Log Intelligence System

**Document Version:** 1.0  
**Last Updated:** September 18, 2025  
**Phase:** 1 - Foundation Complete

## Overview

This document defines the comprehensive data schema design for the Engineering Log Intelligence System across all external services. The system uses a hybrid architecture with PostgreSQL for metadata and relational data, Elasticsearch for log storage and search, and Kafka for real-time streaming.

## Architecture Summary

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │  Elasticsearch  │    │     Kafka       │
│                 │    │                 │    │                 │
│ • User Mgmt     │    │ • Log Storage   │    │ • Log Streaming │
│ • Metadata      │    │ • Full-text     │    │ • Event Proc    │
│ • Config        │    │   Search        │    │ • Data Trans    │
│ • Alerts        │    │ • Analytics     │    │ • Queuing       │
│ • ML Models     │    │ • Aggregations  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## PostgreSQL Schema Design

### Core Tables

#### 1. Users Table
**Purpose:** User management and authentication
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user', -- 'admin', 'developer', 'analyst', 'viewer'
    is_active BOOLEAN DEFAULT true,
    preferences JSONB, -- User-specific settings
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Log Sources Table
**Purpose:** Configuration and metadata for log sources
```sql
CREATE TABLE log_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'splunk', 'sap', 'application', 'custom', 'kafka'
    description TEXT,
    configuration JSONB, -- Connection details, credentials, etc.
    is_active BOOLEAN DEFAULT true,
    health_status VARCHAR(20) DEFAULT 'unknown', -- 'healthy', 'degraded', 'unhealthy'
    last_health_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. Log Entries Table (Metadata Only)
**Purpose:** Metadata and references to actual log data in Elasticsearch
```sql
CREATE TABLE log_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES log_sources(id),
    log_id VARCHAR(255) NOT NULL, -- External log ID
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    level VARCHAR(20), -- 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'
    message TEXT,
    category VARCHAR(100),
    tags JSONB, -- Array of tags
    metadata JSONB, -- Additional metadata
    size_bytes INTEGER, -- Log entry size
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. Alerts Table
**Purpose:** Alert management and tracking
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN', -- 'OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'CLOSED'
    source_id UUID REFERENCES log_sources(id),
    log_entry_id UUID REFERENCES log_entries(id),
    rule_id UUID, -- Reference to alerting rule
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(id),
    resolved_by UUID REFERENCES users(id),
    metadata JSONB,
    escalation_level INTEGER DEFAULT 0
);
```

#### 5. Dashboards Table
**Purpose:** User-created dashboards and visualizations
```sql
CREATE TABLE dashboards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id UUID REFERENCES users(id),
    configuration JSONB NOT NULL, -- Dashboard layout, widgets, filters
    is_public BOOLEAN DEFAULT false,
    tags JSONB, -- Dashboard tags for organization
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. ML Models Table
**Purpose:** Machine learning model management
```sql
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'classification', 'anomaly_detection', 'correlation', 'forecasting'
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'TRAINING', -- 'TRAINING', 'READY', 'DEPLOYED', 'FAILED', 'DEPRECATED'
    model_path VARCHAR(500), -- S3 path or similar
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    training_data_size INTEGER,
    training_duration_seconds INTEGER,
    hyperparameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. System Configuration Table
**Purpose:** System-wide configuration settings
```sql
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'general', 'alerts', 'ml', 'performance', 'security'
    is_encrypted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Extended Tables

#### 8. Alert Rules Table
**Purpose:** Configurable alerting rules
```sql
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    query JSONB NOT NULL, -- Elasticsearch query for matching logs
    conditions JSONB NOT NULL, -- Alert conditions and thresholds
    severity VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 9. User Sessions Table
**Purpose:** User session management
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 10. API Keys Table
**Purpose:** API key management for external access
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    permissions JSONB, -- Array of allowed permissions
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Performance

#### Primary Indexes
```sql
-- Log entries indexes
CREATE INDEX idx_log_entries_source_id ON log_entries(source_id);
CREATE INDEX idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX idx_log_entries_level ON log_entries(level);
CREATE INDEX idx_log_entries_category ON log_entries(category);
CREATE INDEX idx_log_entries_created_at ON log_entries(created_at);
CREATE INDEX idx_log_entries_processing_status ON log_entries(processing_status);

-- Alerts indexes
CREATE INDEX idx_alerts_source_id ON alerts(source_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_triggered_at ON alerts(triggered_at);
CREATE INDEX idx_alerts_rule_id ON alerts(rule_id);

-- Dashboards indexes
CREATE INDEX idx_dashboards_user_id ON dashboards(user_id);
CREATE INDEX idx_dashboards_is_public ON dashboards(is_public);

-- ML models indexes
CREATE INDEX idx_ml_models_type ON ml_models(type);
CREATE INDEX idx_ml_models_status ON ml_models(status);

-- User sessions indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
```

#### GIN Indexes for JSONB
```sql
-- JSONB column indexes
CREATE INDEX idx_log_entries_tags_gin ON log_entries USING GIN(tags);
CREATE INDEX idx_log_entries_metadata_gin ON log_entries USING GIN(metadata);
CREATE INDEX idx_alerts_metadata_gin ON alerts USING GIN(metadata);
CREATE INDEX idx_dashboards_configuration_gin ON dashboards USING GIN(configuration);
CREATE INDEX idx_ml_models_hyperparameters_gin ON ml_models USING GIN(hyperparameters);
```

## Elasticsearch Schema Design

### Index Structure

#### 1. Logs Index (`engineering_logs`)
**Purpose:** Primary log storage and search

```json
{
  "mappings": {
    "properties": {
      "log_id": {
        "type": "keyword"
      },
      "source_id": {
        "type": "keyword"
      },
      "timestamp": {
        "type": "date",
        "format": "strict_date_optional_time||epoch_millis"
      },
      "level": {
        "type": "keyword"
      },
      "message": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "raw_log": {
        "type": "text",
        "analyzer": "standard"
      },
      "category": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "metadata": {
        "type": "object",
        "dynamic": true
      },
      "parsed_fields": {
        "type": "object",
        "properties": {
          "host": {"type": "keyword"},
          "service": {"type": "keyword"},
          "thread": {"type": "keyword"},
          "class": {"type": "keyword"},
          "method": {"type": "keyword"},
          "line_number": {"type": "integer"},
          "stack_trace": {"type": "text"}
        }
      },
      "geo_location": {
        "type": "geo_point"
      },
      "size_bytes": {
        "type": "integer"
      },
      "processing_status": {
        "type": "keyword"
      },
      "created_at": {
        "type": "date"
      }
    }
  },
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "log_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  }
}
```

#### 2. Alerts Index (`engineering_alerts`)
**Purpose:** Alert storage and search

```json
{
  "mappings": {
    "properties": {
      "alert_id": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "description": {
        "type": "text"
      },
      "severity": {
        "type": "keyword"
      },
      "status": {
        "type": "keyword"
      },
      "source_id": {
        "type": "keyword"
      },
      "log_entry_id": {
        "type": "keyword"
      },
      "rule_id": {
        "type": "keyword"
      },
      "triggered_at": {
        "type": "date"
      },
      "acknowledged_at": {
        "type": "date"
      },
      "resolved_at": {
        "type": "date"
      },
      "acknowledged_by": {
        "type": "keyword"
      },
      "resolved_by": {
        "type": "keyword"
      },
      "escalation_level": {
        "type": "integer"
      },
      "metadata": {
        "type": "object",
        "dynamic": true
      }
    }
  }
}
```

#### 3. Analytics Index (`engineering_analytics`)
**Purpose:** Aggregated analytics and metrics

```json
{
  "mappings": {
    "properties": {
      "metric_name": {
        "type": "keyword"
      },
      "metric_type": {
        "type": "keyword"
      },
      "timestamp": {
        "type": "date"
      },
      "value": {
        "type": "float"
      },
      "dimensions": {
        "type": "object",
        "properties": {
          "source_id": {"type": "keyword"},
          "level": {"type": "keyword"},
          "category": {"type": "keyword"},
          "host": {"type": "keyword"},
          "service": {"type": "keyword"}
        }
      },
      "aggregation_period": {
        "type": "keyword"
      }
    }
  }
}
```

### Index Templates

#### Log Index Template
```json
{
  "index_patterns": ["engineering_logs-*"],
  "template": {
    "mappings": {
      "properties": {
        "log_id": {"type": "keyword"},
        "source_id": {"type": "keyword"},
        "timestamp": {"type": "date"},
        "level": {"type": "keyword"},
        "message": {"type": "text"},
        "raw_log": {"type": "text"},
        "category": {"type": "keyword"},
        "tags": {"type": "keyword"},
        "metadata": {"type": "object", "dynamic": true}
      }
    },
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  }
}
```

## Kafka Schema Design

### Topic Structure

#### 1. Log Ingestion Topic (`log-ingestion`)
**Purpose:** Raw log ingestion from various sources

```json
{
  "topic": "log-ingestion",
  "partitions": 12,
  "replication_factor": 3,
  "config": {
    "retention.ms": "604800000", // 7 days
    "compression.type": "lz4",
    "cleanup.policy": "delete"
  }
}
```

**Message Schema:**
```json
{
  "source_id": "uuid",
  "log_id": "string",
  "timestamp": "iso8601",
  "raw_log": "string",
  "metadata": {
    "source_type": "string",
    "host": "string",
    "service": "string",
    "environment": "string"
  }
}
```

#### 2. Log Processing Topic (`log-processing`)
**Purpose:** Processed and enriched log data

```json
{
  "topic": "log-processing",
  "partitions": 12,
  "replication_factor": 3,
  "config": {
    "retention.ms": "2592000000", // 30 days
    "compression.type": "lz4",
    "cleanup.policy": "delete"
  }
}
```

**Message Schema:**
```json
{
  "log_id": "string",
  "source_id": "uuid",
  "timestamp": "iso8601",
  "level": "string",
  "message": "string",
  "raw_log": "string",
  "category": "string",
  "tags": ["string"],
  "parsed_fields": {
    "host": "string",
    "service": "string",
    "thread": "string",
    "class": "string",
    "method": "string",
    "line_number": "integer",
    "stack_trace": "string"
  },
  "metadata": "object",
  "processing_status": "string"
}
```

#### 3. Alerts Topic (`alerts`)
**Purpose:** Alert notifications and updates

```json
{
  "topic": "alerts",
  "partitions": 6,
  "replication_factor": 3,
  "config": {
    "retention.ms": "2592000000", // 30 days
    "compression.type": "lz4",
    "cleanup.policy": "delete"
  }
}
```

**Message Schema:**
```json
{
  "alert_id": "uuid",
  "title": "string",
  "description": "string",
  "severity": "string",
  "status": "string",
  "source_id": "uuid",
  "log_entry_id": "uuid",
  "rule_id": "uuid",
  "triggered_at": "iso8601",
  "metadata": "object"
}
```

#### 4. Analytics Topic (`analytics`)
**Purpose:** Analytics and metrics data

```json
{
  "topic": "analytics",
  "partitions": 6,
  "replication_factor": 3,
  "config": {
    "retention.ms": "2592000000", // 30 days
    "compression.type": "lz4",
    "cleanup.policy": "delete"
  }
}
```

**Message Schema:**
```json
{
  "metric_name": "string",
  "metric_type": "string",
  "timestamp": "iso8601",
  "value": "float",
  "dimensions": {
    "source_id": "uuid",
    "level": "string",
    "category": "string",
    "host": "string",
    "service": "string"
  },
  "aggregation_period": "string"
}
```

## Data Flow Design

### 1. Log Ingestion Flow
```
Log Sources → Kafka (log-ingestion) → Processing Service → Kafka (log-processing) → Elasticsearch
                                                      ↓
                                                 PostgreSQL (metadata)
```

### 2. Search Flow
```
Frontend → Vercel Functions → Elasticsearch → Results
```

### 3. Alert Flow
```
Elasticsearch → Alert Engine → Kafka (alerts) → Notification Service
                              ↓
                         PostgreSQL (alerts)
```

### 4. Analytics Flow
```
Elasticsearch → Analytics Engine → Kafka (analytics) → Elasticsearch (analytics)
```

## Performance Considerations

### PostgreSQL
- **Connection Pooling:** Use PgBouncer for connection management
- **Partitioning:** Partition log_entries by timestamp for better performance
- **Indexing:** Strategic indexing on frequently queried columns
- **Archiving:** Archive old data to reduce table size

### Elasticsearch
- **Sharding:** Distribute data across multiple shards
- **Replicas:** Configure appropriate replica count
- **Index Lifecycle:** Implement index lifecycle management
- **Caching:** Use Elasticsearch query cache and field data cache

### Kafka
- **Partitioning:** Distribute load across partitions
- **Compression:** Use LZ4 compression for better throughput
- **Retention:** Configure appropriate retention policies
- **Monitoring:** Monitor consumer lag and throughput

## Security Considerations

### Data Encryption
- **At Rest:** Encrypt sensitive data in all databases
- **In Transit:** Use TLS for all communications
- **Keys:** Secure key management for encryption

### Access Control
- **Database:** Role-based access control
- **Elasticsearch:** Security plugins and access control
- **Kafka:** SASL authentication and authorization

### Audit Logging
- **All Operations:** Log all data access and modifications
- **User Actions:** Track user activities
- **System Events:** Monitor system-level events

## Backup and Recovery

### PostgreSQL
- **Backup Strategy:** Daily full backups + WAL archiving
- **Recovery Time:** < 1 hour for full recovery
- **Point-in-time Recovery:** Support for specific timestamps

### Elasticsearch
- **Snapshot Strategy:** Daily snapshots to S3
- **Index Recovery:** Fast index recovery from snapshots
- **Cross-cluster Replication:** For disaster recovery

### Kafka
- **Data Retention:** Configurable retention policies
- **Replication:** Multi-broker replication
- **Monitoring:** Consumer lag and data loss monitoring

## Monitoring and Observability

### Database Metrics
- **PostgreSQL:** Connection count, query performance, lock waits
- **Elasticsearch:** Index health, search performance, cluster status
- **Kafka:** Producer/consumer lag, throughput, partition health

### Application Metrics
- **API Performance:** Response times, error rates
- **Data Processing:** Ingestion rates, processing latency
- **User Activity:** Dashboard usage, search patterns

---

**Schema Version:** 1.0  
**Next Review:** Phase 2 Completion  
**Maintainer:** Development Team
