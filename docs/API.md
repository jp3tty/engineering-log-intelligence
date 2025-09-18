# API Documentation

## Overview

The Engineering Log Intelligence System provides RESTful API endpoints for log ingestion, search, and system monitoring.

**Base URL**: `https://engineering-log-intelligence.vercel.app/api`

## Authentication

Currently, the API does not require authentication for development. Production deployment will include JWT-based authentication.

## Endpoints

### Health Check

#### GET `/api/health/check`

Check the health status of the system and external services.

**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2025-09-17T16:41:24Z",
  "service": "Engineering Log Intelligence System",
  "version": "0.1.0",
  "environment": "development",
  "checks": {
    "vercel": {
      "status": "ok",
      "message": "Running on Vercel platform"
    },
    "environment": {
      "status": "ok",
      "message": "All required variables present"
    },
    "external_services": {
      "status": "ok",
      "services": {
        "database": true,
        "elasticsearch": true,
        "kafka": true
      }
    }
  }
}
```

### Log Ingestion

#### POST `/api/logs/ingest`

Ingest log data from various sources (SPLUNK, SAP, applications).

**Request Body:**
```json
{
  "source_id": "uuid-string",
  "log_data": {
    "level": "INFO|DEBUG|WARN|ERROR|FATAL",
    "message": "Log message content",
    "timestamp": "2025-09-17T16:41:24Z",
    "category": "application|system|security",
    "tags": ["web", "api", "error"],
    "metadata": {
      "host": "server-01",
      "service": "webapp",
      "user_id": "12345"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "source-123_1758177923859",
  "message": "Log entry ingested successfully",
  "timestamp": "2025-09-17T16:41:24Z"
}
```

### Log Search

#### GET `/api/logs/search`

Search across indexed log data with various filters.

**Query Parameters:**
- `q` (string): Search query
- `level` (string): Log level filter
- `category` (string): Category filter
- `source_id` (string): Source ID filter
- `start_time` (string): Start time filter (ISO format)
- `end_time` (string): End time filter (ISO format)
- `size` (integer): Number of results (default: 10)
- `from` (integer): Offset for pagination (default: 0)

**Example:**
```
GET /api/logs/search?q=error&level=ERROR&size=20&from=0
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "log_id": "source-123_1758177923859",
      "source_id": "source-123",
      "timestamp": "2025-09-17T16:41:24Z",
      "level": "ERROR",
      "message": "Database connection failed",
      "category": "application",
      "tags": ["database", "error"],
      "metadata": {
        "host": "server-01",
        "service": "webapp"
      },
      "score": 0.95
    }
  ],
  "total": 150,
  "size": 20,
  "from": 0,
  "query": {
    "search_query": "error",
    "level": "ERROR",
    "size": 20
  },
  "timestamp": "2025-09-17T16:41:24Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request body",
  "message": "Request body must contain valid JSON"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

- **Development**: 1000 requests per hour
- **Production**: 100 requests per hour

## CORS

The API supports CORS for the following origins:
- **Development**: `http://localhost:3000`, `http://localhost:5173`
- **Production**: `https://engineering-log-intelligence.vercel.app`

## Data Models

### Log Entry
```json
{
  "log_id": "string",
  "source_id": "uuid",
  "timestamp": "datetime",
  "level": "string",
  "message": "string",
  "category": "string",
  "tags": ["string"],
  "metadata": "object",
  "ingested_at": "datetime"
}
```

### Log Source
```json
{
  "id": "uuid",
  "name": "string",
  "type": "splunk|sap|application|custom",
  "description": "string",
  "configuration": "object",
  "is_active": "boolean"
}
```

## Examples

### Ingest a SPLUNK Log
```bash
curl -X POST https://engineering-log-intelligence.vercel.app/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "splunk-prod-001",
    "log_data": {
      "level": "ERROR",
      "message": "Failed to connect to database",
      "timestamp": "2025-09-17T16:41:24Z",
      "category": "application",
      "tags": ["database", "connection", "error"],
      "metadata": {
        "host": "web-server-01",
        "service": "user-service",
        "database": "postgresql"
      }
    }
  }'
```

### Search for Error Logs
```bash
curl "https://engineering-log-intelligence.vercel.app/api/logs/search?q=database&level=ERROR&size=10"
```

### Check System Health
```bash
curl https://engineering-log-intelligence.vercel.app/api/health/check
```

---

**Last Updated**: September 17, 2025  
**Version**: 0.1.0
