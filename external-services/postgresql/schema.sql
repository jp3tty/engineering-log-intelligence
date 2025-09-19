-- Engineering Log Intelligence System Database Schema
-- PostgreSQL database schema for log analysis platform

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE log_level AS ENUM ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL');
CREATE TYPE source_type AS ENUM ('splunk', 'sap', 'application');
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_status AS ENUM ('open', 'acknowledged', 'resolved', 'closed');
CREATE TYPE user_role AS ENUM ('user', 'admin', 'analyst', 'viewer');
CREATE TYPE correlation_type AS ENUM ('request', 'session', 'ip', 'timestamp', 'pattern');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    permissions JSONB DEFAULT '[]',
    api_key VARCHAR(255) UNIQUE,
    api_key_created TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Log entries table
CREATE TABLE log_entries (
    id SERIAL PRIMARY KEY,
    log_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    level log_level NOT NULL,
    message TEXT NOT NULL,
    source_type source_type NOT NULL,
    host VARCHAR(255),
    service VARCHAR(255),
    category VARCHAR(100),
    tags JSONB DEFAULT '[]',
    raw_log TEXT,
    structured_data JSONB DEFAULT '{}',
    
    -- Correlation fields
    request_id UUID,
    session_id VARCHAR(255),
    correlation_id VARCHAR(255),
    ip_address INET,
    
    -- Application-specific fields
    application_type VARCHAR(100),
    framework VARCHAR(100),
    http_method VARCHAR(10),
    http_status INTEGER,
    endpoint VARCHAR(500),
    response_time_ms DECIMAL(10,2),
    
    -- SAP-specific fields
    transaction_code VARCHAR(20),
    sap_system VARCHAR(100),
    department VARCHAR(100),
    amount DECIMAL(15,2),
    currency VARCHAR(3),
    document_number VARCHAR(50),
    
    -- SPLUNK-specific fields
    splunk_source VARCHAR(255),
    splunk_host VARCHAR(255),
    
    -- Anomaly and error information
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_type VARCHAR(100),
    error_details JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    business_context JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity alert_severity DEFAULT 'medium',
    category VARCHAR(100) DEFAULT 'system',
    source VARCHAR(100) NOT NULL,
    status alert_status DEFAULT 'open',
    assigned_to INTEGER REFERENCES users(id),
    log_entries JSONB DEFAULT '[]',
    correlation_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    resolved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dashboards table
CREATE TABLE dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    layout JSONB DEFAULT '{"rows": 4, "cols": 6}',
    widgets JSONB DEFAULT '[]',
    filters JSONB DEFAULT '{}',
    owner_id INTEGER REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    shared_with JSONB DEFAULT '[]',
    refresh_interval INTEGER DEFAULT 30,
    auto_refresh BOOLEAN DEFAULT TRUE,
    theme VARCHAR(50) DEFAULT 'default',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Correlations table
CREATE TABLE correlations (
    id SERIAL PRIMARY KEY,
    correlation_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    correlation_type correlation_type NOT NULL,
    log_entry_ids JSONB DEFAULT '[]',
    source_systems JSONB DEFAULT '[]',
    correlation_key VARCHAR(255) NOT NULL,
    correlation_value VARCHAR(500) NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    pattern_type VARCHAR(100),
    pattern_data JSONB DEFAULT '{}',
    first_seen TIMESTAMP WITH TIME ZONE,
    last_seen TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance

-- Log entries indexes
CREATE INDEX idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX idx_log_entries_level ON log_entries(level);
CREATE INDEX idx_log_entries_source_type ON log_entries(source_type);
CREATE INDEX idx_log_entries_host ON log_entries(host);
CREATE INDEX idx_log_entries_service ON log_entries(service);
CREATE INDEX idx_log_entries_request_id ON log_entries(request_id);
CREATE INDEX idx_log_entries_session_id ON log_entries(session_id);
CREATE INDEX idx_log_entries_correlation_id ON log_entries(correlation_id);
CREATE INDEX idx_log_entries_ip_address ON log_entries(ip_address);
CREATE INDEX idx_log_entries_is_anomaly ON log_entries(is_anomaly);
CREATE INDEX idx_log_entries_http_status ON log_entries(http_status);
CREATE INDEX idx_log_entries_transaction_code ON log_entries(transaction_code);
CREATE INDEX idx_log_entries_sap_system ON log_entries(sap_system);
CREATE INDEX idx_log_entries_splunk_source ON log_entries(splunk_source);

-- Composite indexes for common queries
CREATE INDEX idx_log_entries_timestamp_source ON log_entries(timestamp, source_type);
CREATE INDEX idx_log_entries_level_timestamp ON log_entries(level, timestamp);
CREATE INDEX idx_log_entries_anomaly_timestamp ON log_entries(is_anomaly, timestamp);

-- Full-text search indexes
CREATE INDEX idx_log_entries_message_gin ON log_entries USING gin(to_tsvector('english', message));
CREATE INDEX idx_log_entries_raw_log_gin ON log_entries USING gin(to_tsvector('english', raw_log));

-- JSON indexes for structured data
CREATE INDEX idx_log_entries_structured_data_gin ON log_entries USING gin(structured_data);
CREATE INDEX idx_log_entries_tags_gin ON log_entries USING gin(tags);
CREATE INDEX idx_log_entries_error_details_gin ON log_entries USING gin(error_details);
CREATE INDEX idx_log_entries_performance_metrics_gin ON log_entries USING gin(performance_metrics);

-- Users indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_api_key ON users(api_key);

-- Alerts indexes
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_category ON alerts(category);
CREATE INDEX idx_alerts_triggered_at ON alerts(triggered_at);
CREATE INDEX idx_alerts_assigned_to ON alerts(assigned_to);
CREATE INDEX idx_alerts_correlation_id ON alerts(correlation_id);

-- Dashboards indexes
CREATE INDEX idx_dashboards_owner_id ON dashboards(owner_id);
CREATE INDEX idx_dashboards_is_public ON dashboards(is_public);
CREATE INDEX idx_dashboards_shared_with_gin ON dashboards USING gin(shared_with);

-- Correlations indexes
CREATE INDEX idx_correlations_type ON correlations(correlation_type);
CREATE INDEX idx_correlations_key ON correlations(correlation_key);
CREATE INDEX idx_correlations_value ON correlations(correlation_value);
CREATE INDEX idx_correlations_confidence ON correlations(confidence_score);
CREATE INDEX idx_correlations_first_seen ON correlations(first_seen);
CREATE INDEX idx_correlations_log_entry_ids_gin ON correlations USING gin(log_entry_ids);
CREATE INDEX idx_correlations_source_systems_gin ON correlations USING gin(source_systems);

-- Create triggers for updated_at timestamps

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_log_entries_updated_at BEFORE UPDATE ON log_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dashboards_updated_at BEFORE UPDATE ON dashboards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_correlations_updated_at BEFORE UPDATE ON correlations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries

-- View for recent high-priority logs
CREATE VIEW recent_high_priority_logs AS
SELECT 
    id, log_id, timestamp, level, message, source_type, host, service,
    is_anomaly, anomaly_type, http_status, response_time_ms,
    request_id, session_id, correlation_id, ip_address
FROM log_entries
WHERE 
    (level IN ('ERROR', 'FATAL') OR is_anomaly = TRUE OR http_status >= 500)
    AND timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- View for alert statistics
CREATE VIEW alert_statistics AS
SELECT 
    status,
    severity,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - triggered_at))/60) as avg_resolution_minutes
FROM alerts
WHERE triggered_at >= NOW() - INTERVAL '30 days'
GROUP BY status, severity;

-- View for log volume by source
CREATE VIEW log_volume_by_source AS
SELECT 
    source_type,
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as log_count,
    COUNT(CASE WHEN is_anomaly = TRUE THEN 1 END) as anomaly_count,
    COUNT(CASE WHEN level IN ('ERROR', 'FATAL') THEN 1 END) as error_count
FROM log_entries
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY source_type, hour
ORDER BY hour DESC, source_type;

-- Create functions for common operations

-- Function to get log entries by correlation
CREATE OR REPLACE FUNCTION get_logs_by_correlation(corr_key VARCHAR, corr_value VARCHAR)
RETURNS TABLE (
    id INTEGER,
    log_id VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    level log_level,
    message TEXT,
    source_type source_type,
    host VARCHAR,
    service VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        le.id, le.log_id, le.timestamp, le.level, le.message, 
        le.source_type, le.host, le.service
    FROM log_entries le
    WHERE 
        (corr_key = 'request_id' AND le.request_id::TEXT = corr_value) OR
        (corr_key = 'session_id' AND le.session_id = corr_value) OR
        (corr_key = 'correlation_id' AND le.correlation_id = corr_value) OR
        (corr_key = 'ip_address' AND le.ip_address::TEXT = corr_value)
    ORDER BY le.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to search logs by text
CREATE OR REPLACE FUNCTION search_logs(search_text TEXT, limit_count INTEGER DEFAULT 100)
RETURNS TABLE (
    id INTEGER,
    log_id VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE,
    level log_level,
    message TEXT,
    source_type source_type,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        le.id, le.log_id, le.timestamp, le.level, le.message, 
        le.source_type, ts_rank(to_tsvector('english', le.message), plainto_tsquery('english', search_text)) as rank
    FROM log_entries le
    WHERE 
        to_tsvector('english', le.message) @@ plainto_tsquery('english', search_text) OR
        to_tsvector('english', le.raw_log) @@ plainto_tsquery('english', search_text)
    ORDER BY rank DESC, le.timestamp DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Insert default admin user
INSERT INTO users (username, email, password_hash, salt, first_name, last_name, role, is_active, is_verified, permissions)
VALUES (
    'admin',
    'admin@logintelligence.com',
    'pbkdf2_sha256$100000$default_salt$default_hash', -- This should be replaced with actual hash
    'default_salt', -- This should be replaced with actual salt
    'System',
    'Administrator',
    'admin',
    TRUE,
    TRUE,
    '["read_logs", "view_dashboard", "create_alerts", "analyze_logs", "export_data", "manage_users", "manage_system", "configure_alerts"]'
);

-- Create sample data for testing (optional)
-- This can be uncommented for development/testing purposes
/*
INSERT INTO log_entries (log_id, timestamp, level, message, source_type, host, service, category, tags, raw_log, structured_data)
VALUES 
    ('test-1', NOW(), 'INFO', 'Test log entry', 'application', 'test-server', 'webapp', 'application', '["test"]', 'Raw log data', '{"test": true}'),
    ('test-2', NOW(), 'ERROR', 'Test error entry', 'splunk', 'test-server', 'system', 'system', '["test", "error"]', 'Raw error data', '{"error": true}');
*/

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO logintelligence_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO logintelligence_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO logintelligence_user;
