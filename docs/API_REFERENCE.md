# Engineering Log Intelligence System - API Reference

## Overview

The Engineering Log Intelligence System provides a comprehensive REST API for log analysis, monitoring, and management. The API is built using Vercel Functions and supports JWT authentication.

## Base URL

- **Development**: `https://your-project.vercel.app/api`
- **Production**: `https://your-domain.com/api`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting Started

1. **Register** a new user account
2. **Login** to get access and refresh tokens
3. **Use the access token** for authenticated requests
4. **Refresh the token** when it expires

## API Endpoints

### Authentication Endpoints

#### POST `/auth/login`
Login with username and password.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User",
      "role": "admin",
      "permissions": ["read_logs", "manage_users"],
      "is_verified": true,
      "last_login": "2025-09-19T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "bearer",
      "expires_in": 1800
    }
  }
}
```

#### POST `/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string"
}
```

#### POST `/auth/refresh`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

#### GET `/auth/me`
Get current user information.

**Headers:**
```
Authorization: Bearer <access-token>
```

#### POST `/auth/logout`
Logout (for logging purposes).

### Log Management Endpoints

#### POST `/logs/ingest`
Ingest new log entries.

**Headers:**
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "logs": [
    {
      "log_id": "app-1234567890-abc123",
      "timestamp": "2025-09-19T10:30:00Z",
      "level": "INFO",
      "message": "User login successful",
      "source_type": "application",
      "host": "web-server-01",
      "service": "auth-service",
      "category": "authentication",
      "tags": ["auth", "login"],
      "raw_log": "2025-09-19 10:30:00 INFO User login successful",
      "structured_data": {
        "user_id": 123,
        "ip_address": "192.168.1.100"
      },
      "request_id": "req-1234567890",
      "session_id": "sess-1234567890",
      "correlation_id": "corr-1234567890",
      "ip_address": "192.168.1.100",
      "application_type": "web_app",
      "framework": "Spring Boot",
      "http_method": "POST",
      "http_status": 200,
      "endpoint": "/api/auth/login",
      "response_time_ms": 145.67,
      "is_anomaly": false,
      "performance_metrics": {
        "memory_usage_mb": 256.5,
        "cpu_usage_percent": 45.2
      }
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ingested_count": 1,
    "failed_count": 0,
    "message": "Logs ingested successfully"
  }
}
```

#### GET `/logs/search`
Search log entries with filters.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Query Parameters:**
- `q` (string): Search query text
- `source_type` (string): Filter by source type (splunk, sap, application)
- `level` (string): Filter by log level (DEBUG, INFO, WARN, ERROR, FATAL)
- `host` (string): Filter by host
- `service` (string): Filter by service
- `start_time` (string): Start time (ISO 8601 format)
- `end_time` (string): End time (ISO 8601 format)
- `is_anomaly` (boolean): Filter by anomaly status
- `limit` (integer): Number of results (default: 100)
- `offset` (integer): Offset for pagination (default: 0)

**Example:**
```
GET /api/logs/search?q=error&source_type=application&level=ERROR&limit=50
```

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "log_id": "app-1234567890-abc123",
        "timestamp": "2025-09-19T10:30:00Z",
        "level": "ERROR",
        "message": "Database connection failed",
        "source_type": "application",
        "host": "web-server-01",
        "service": "database-service",
        "is_anomaly": true,
        "anomaly_type": "database_error"
      }
    ],
    "total_count": 1,
    "limit": 50,
    "offset": 0
  }
}
```

#### GET `/logs/{log_id}`
Get a specific log entry by log_id.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "log_id": "app-1234567890-abc123",
    "timestamp": "2025-09-19T10:30:00Z",
    "level": "INFO",
    "message": "User login successful",
    "source_type": "application",
    "host": "web-server-01",
    "service": "auth-service",
    "category": "authentication",
    "tags": ["auth", "login"],
    "raw_log": "2025-09-19 10:30:00 INFO User login successful",
    "structured_data": {
      "user_id": 123,
      "ip_address": "192.168.1.100"
    },
    "request_id": "req-1234567890",
    "session_id": "sess-1234567890",
    "correlation_id": "corr-1234567890",
    "ip_address": "192.168.1.100",
    "application_type": "web_app",
    "framework": "Spring Boot",
    "http_method": "POST",
    "http_status": 200,
    "endpoint": "/api/auth/login",
    "response_time_ms": 145.67,
    "is_anomaly": false,
    "performance_metrics": {
      "memory_usage_mb": 256.5,
      "cpu_usage_percent": 45.2
    },
    "created_at": "2025-09-19T10:30:00Z",
    "updated_at": "2025-09-19T10:30:00Z"
  }
}
```

#### GET `/logs/correlation`
Get logs by correlation key and value.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Query Parameters:**
- `key` (string): Correlation key (request_id, session_id, correlation_id, ip_address)
- `value` (string): Correlation value
- `limit` (integer): Number of results (default: 100)

**Example:**
```
GET /api/logs/correlation?key=request_id&value=req-1234567890
```

#### GET `/logs/statistics`
Get log statistics for a time period.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Query Parameters:**
- `start_time` (string): Start time (ISO 8601 format)
- `end_time` (string): End time (ISO 8601 format)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_logs": 10000,
    "logs_by_level": {
      "INFO": 8000,
      "WARN": 1500,
      "ERROR": 450,
      "FATAL": 50
    },
    "logs_by_source": {
      "application": 6000,
      "splunk": 3000,
      "sap": 1000
    },
    "anomaly_count": 25,
    "error_count": 500,
    "anomaly_rate": 0.25,
    "error_rate": 5.0,
    "start_time": "2025-09-19T00:00:00Z",
    "end_time": "2025-09-19T23:59:59Z"
  }
}
```

### Alert Management Endpoints

#### GET `/alerts`
Get all alerts with optional filters.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Query Parameters:**
- `status` (string): Filter by status (open, acknowledged, resolved, closed)
- `severity` (string): Filter by severity (low, medium, high, critical)
- `category` (string): Filter by category (system, security, performance, business)
- `assigned_to` (integer): Filter by assigned user ID
- `limit` (integer): Number of results (default: 100)
- `offset` (integer): Offset for pagination (default: 0)

#### POST `/alerts`
Create a new alert.

**Headers:**
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "High Error Rate Detected",
  "description": "Error rate has exceeded 5% in the last hour",
  "severity": "high",
  "category": "performance",
  "source": "application",
  "log_entries": [1, 2, 3],
  "correlation_id": "corr-1234567890",
  "metadata": {
    "threshold": 5.0,
    "current_rate": 7.2
  }
}
```

#### GET `/alerts/{alert_id}`
Get a specific alert by ID.

#### PUT `/alerts/{alert_id}/acknowledge`
Acknowledge an alert.

#### PUT `/alerts/{alert_id}/resolve`
Resolve an alert.

**Request Body:**
```json
{
  "resolution_notes": "Fixed the database connection issue"
}
```

### Dashboard Endpoints

#### GET `/dashboards`
Get user's dashboards.

**Headers:**
```
Authorization: Bearer <access-token>
```

#### POST `/dashboards`
Create a new dashboard.

**Headers:**
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "System Overview",
  "description": "Main system monitoring dashboard",
  "layout": {
    "rows": 4,
    "cols": 6
  },
  "widgets": [
    {
      "id": "widget-1",
      "type": "chart",
      "title": "Log Volume",
      "position": {"x": 0, "y": 0, "w": 3, "h": 2},
      "config": {
        "chart_type": "line",
        "data_source": "logs",
        "time_range": "24h"
      }
    }
  ],
  "filters": {
    "source_type": "application",
    "level": ["ERROR", "WARN"]
  },
  "is_public": false,
  "refresh_interval": 30,
  "auto_refresh": true,
  "theme": "default"
}
```

#### GET `/dashboards/{dashboard_id}`
Get a specific dashboard.

#### PUT `/dashboards/{dashboard_id}`
Update a dashboard.

#### DELETE `/dashboards/{dashboard_id}`
Delete a dashboard.

### Health Check Endpoints

#### GET `/health/check`
Check system health.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-09-19T10:30:00Z",
    "version": "1.0.0",
    "services": {
      "database": {
        "status": "healthy",
        "response_time_ms": 15.2
      },
      "elasticsearch": {
        "status": "healthy",
        "response_time_ms": 23.1
      },
      "kafka": {
        "status": "healthy",
        "response_time_ms": 8.7
      }
    }
  }
}
```

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details (optional)"
  }
}
```

### Common Error Codes

- `AUTH_REQUIRED`: Authentication required
- `INVALID_TOKEN`: Invalid or expired token
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `INSUFFICIENT_ROLE`: User lacks required role
- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INTERNAL_ERROR`: Internal server error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour
- **API key users**: 5000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1632000000
```

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

- `limit`: Number of items per page (default: 100, max: 1000)
- `offset`: Number of items to skip (default: 0)

Pagination metadata is included in responses:
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total_count": 1000,
    "limit": 100,
    "offset": 0,
    "has_more": true
  }
}
```

## Data Formats

### Timestamps
All timestamps are in ISO 8601 format with UTC timezone:
```
2025-09-19T10:30:00Z
```

### Log Levels
Supported log levels:
- `DEBUG`: Debug information
- `INFO`: General information
- `WARN`: Warning messages
- `ERROR`: Error messages
- `FATAL`: Fatal errors

### Source Types
Supported source types:
- `splunk`: SPLUNK logs
- `sap`: SAP transaction logs
- `application`: Application logs

### User Roles
Supported user roles:
- `viewer`: Read-only access
- `user`: Basic user access
- `analyst`: Advanced analysis capabilities
- `admin`: Full administrative access

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post('https://your-api.com/api/auth/login', json={
    'username': 'admin',
    'password': 'password'
})
tokens = response.json()['data']['tokens']

# Search logs
headers = {'Authorization': f"Bearer {tokens['access_token']}"}
response = requests.get('https://your-api.com/api/logs/search', 
                       headers=headers,
                       params={'q': 'error', 'limit': 10})
logs = response.json()['data']['logs']
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch('https://your-api.com/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'password'
  })
});
const { tokens } = (await loginResponse.json()).data;

// Search logs
const searchResponse = await fetch('https://your-api.com/api/logs/search?q=error&limit=10', {
  headers: { 'Authorization': `Bearer ${tokens.access_token}` }
});
const { logs } = (await searchResponse.json()).data;
```

### cURL
```bash
# Login
curl -X POST https://your-api.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Search logs
curl -X GET "https://your-api.com/api/logs/search?q=error&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Support

For API support and questions:
- **Documentation**: [API Documentation](https://your-docs.com)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@logintelligence.com
