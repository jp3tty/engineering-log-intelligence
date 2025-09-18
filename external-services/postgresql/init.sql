-- Database initialization script for Engineering Log Intelligence System
-- This script creates the necessary tables and indexes for the development environment

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table
CREATE TABLE IF NOT EXISTS users (
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

-- Log sources table
CREATE TABLE IF NOT EXISTS log_sources (
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

-- Log entries table (metadata only, actual logs stored in Elasticsearch)
CREATE TABLE IF NOT EXISTS log_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES log_sources(id),
    log_id VARCHAR(255) NOT NULL, -- External log ID
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    level VARCHAR(20), -- 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'
    message TEXT,
    category VARCHAR(100),
    tags JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN', -- 'OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'CLOSED'
    source_id UUID REFERENCES log_sources(id),
    log_entry_id UUID REFERENCES log_entries(id),
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(id),
    resolved_by UUID REFERENCES users(id),
    metadata JSONB
);

-- Dashboards table
CREATE TABLE IF NOT EXISTS dashboards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id UUID REFERENCES users(id),
    configuration JSONB NOT NULL,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ML models table
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'classification', 'anomaly_detection', 'correlation'
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'TRAINING', -- 'TRAINING', 'READY', 'DEPLOYED', 'FAILED'
    model_path VARCHAR(500),
    accuracy DECIMAL(5,4),
    training_data_size INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System configuration table
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_log_entries_source_id ON log_entries(source_id);
CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_entries_level ON log_entries(level);
CREATE INDEX IF NOT EXISTS idx_log_entries_category ON log_entries(category);
CREATE INDEX IF NOT EXISTS idx_log_entries_created_at ON log_entries(created_at);

CREATE INDEX IF NOT EXISTS idx_alerts_source_id ON alerts(source_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON alerts(triggered_at);

CREATE INDEX IF NOT EXISTS idx_dashboards_user_id ON dashboards(user_id);
CREATE INDEX IF NOT EXISTS idx_dashboards_is_public ON dashboards(is_public);

CREATE INDEX IF NOT EXISTS idx_ml_models_type ON ml_models(type);
CREATE INDEX IF NOT EXISTS idx_ml_models_status ON ml_models(status);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_log_entries_tags_gin ON log_entries USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_log_entries_metadata_gin ON log_entries USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_alerts_metadata_gin ON alerts USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_dashboards_configuration_gin ON dashboards USING GIN(configuration);

-- Insert default data
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@logintelligence.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8.5.2', 'admin'),
('developer', 'dev@logintelligence.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8.5.2', 'developer'),
('analyst', 'analyst@logintelligence.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8.5.2', 'analyst')
ON CONFLICT (username) DO NOTHING;

INSERT INTO log_sources (name, type, description, configuration) VALUES
('SPLUNK Production', 'splunk', 'Main SPLUNK instance for production logs', '{"host": "splunk-prod.company.com", "port": 8089, "index": "main"}'),
('SAP ERP', 'sap', 'SAP ERP system logs', '{"host": "sap-erp.company.com", "port": 8000, "client": "100"}'),
('Application Server', 'application', 'Main application server logs', '{"host": "app-server.company.com", "port": 8080, "service": "webapp"}'),
('Custom System', 'custom', 'Custom internal system logs', '{"host": "custom.company.com", "port": 9000, "protocol": "tcp"}')
ON CONFLICT (name) DO NOTHING;

INSERT INTO system_config (key, value, description) VALUES
('max_log_entries_per_page', '100', 'Maximum number of log entries to return per page'),
('alert_retention_days', '90', 'Number of days to retain alerts'),
('log_retention_days', '365', 'Number of days to retain log entries'),
('ml_model_accuracy_threshold', '0.85', 'Minimum accuracy threshold for ML models'),
('rate_limit_requests_per_hour', '1000', 'Rate limit for API requests per hour')
ON CONFLICT (key) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_log_sources_updated_at BEFORE UPDATE ON log_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dashboards_updated_at BEFORE UPDATE ON dashboards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ml_models_updated_at BEFORE UPDATE ON ml_models FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
