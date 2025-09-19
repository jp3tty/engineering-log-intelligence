# Vercel Functions API Documentation

## Overview

The Engineering Log Intelligence System provides a comprehensive set of Vercel Functions for log management, user authentication, and system administration. All functions are designed for serverless deployment on Vercel with proper error handling, rate limiting, and security.

## Base URL

```
https://your-domain.vercel.app/api
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

All endpoints are protected by rate limiting:
- **Login**: 5 requests per 5 minutes
- **Register**: 3 requests per hour
- **API**: 1000 requests per hour
- **Search**: 100 requests per 5 minutes
- **Admin**: 200 requests per 5 minutes

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {},
  "timestamp": "2025-09-19T10:30:00Z"
}
```

## Endpoints

### Authentication

#### POST /api/auth/login
Authenticate user and return JWT tokens.

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
    "access_token": "jwt-token",
    "refresh_token": "refresh-token",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "username": "user",
      "email": "user@example.com",
      "role": "user",
      "permissions": ["read_logs", "view_dashboard"]
    }
  }
}
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh-token"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "new-jwt-token",
    "refresh_token": "new-refresh-token",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### User Management

#### POST /api/users/register
Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "user"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "newuser",
      "email": "newuser@example.com",
      "first_name": "New",
      "last_name": "User",
      "role": "user",
      "is_active": true,
      "created_at": "2025-09-19T10:30:00Z"
    },
    "api_key": "eli_abc123...",
    "message": "User registered successfully"
  }
}
```

#### GET /api/users/profile
Get current user's profile.

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "user",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "permissions": ["read_logs", "view_dashboard"],
      "is_active": true,
      "last_login": "2025-09-19T10:30:00Z"
    }
  }
}
```

#### PUT /api/users/profile
Update current user's profile.

**Headers:**
- `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "user",
      "email": "updated@example.com",
      "first_name": "Updated",
      "last_name": "Name",
      "role": "user"
    },
    "message": "Profile updated successfully"
  }
}
```

#### DELETE /api/users/profile
Delete current user's account.

**Headers:**
- `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Account deleted successfully"
  }
}
```

### Admin Functions

#### GET /api/users/admin
List all users (admin only).

**Headers:**
- `Authorization: Bearer <admin-token>`

**Query Parameters:**
- `limit`: Number of users to return (default: 100, max: 1000)
- `offset`: Offset for pagination (default: 0)
- `active_only`: Show only active users (default: true)
- `search`: Search term for username/email/name

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "2025-09-19T10:30:00Z"
      }
    ],
    "total_count": 50,
    "limit": 100,
    "offset": 0
  }
}
```

#### GET /api/users/admin/{user_id}
Get specific user by ID (admin only).

**Headers:**
- `Authorization: Bearer <admin-token>`

**Path Parameters:**
- `user_id`: ID of the user to retrieve

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "role": "user",
      "is_active": true,
      "permissions": ["read_logs", "view_dashboard"]
    }
  }
}
```

#### PUT /api/users/admin/{user_id}
Update user (admin only).

**Headers:**
- `Authorization: Bearer <admin-token>`

**Path Parameters:**
- `user_id`: ID of the user to update

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "role": "string",
  "is_active": boolean,
  "is_verified": boolean
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "user1",
      "email": "updated@example.com",
      "role": "analyst",
      "is_active": true
    },
    "message": "User updated successfully"
  }
}
```

#### DELETE /api/users/admin/{user_id}
Delete user (admin only).

**Headers:**
- `Authorization: Bearer <admin-token>`

**Path Parameters:**
- `user_id`: ID of the user to delete

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "User deleted successfully"
  }
}
```

### Password Management

#### POST /api/auth/password-reset/request
Request password reset.

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "If the email exists, a password reset link has been sent",
    "email": "user@example.com"
  }
}
```

#### POST /api/auth/password-reset/confirm
Confirm password reset.

**Request Body:**
```json
{
  "token": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Password reset successfully",
    "user_id": 1
  }
}
```

#### POST /api/auth/password-change
Change password for authenticated user.

**Headers:**
- `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Password changed successfully"
  }
}
```

### Log Management

#### POST /api/logs/ingest
Ingest log entries.

**Request Body:**
```json
{
  "logs": [
    {
      "log_id": "string",
      "timestamp": "2025-09-19T10:30:00Z",
      "level": "INFO",
      "message": "string",
      "source_type": "application",
      "host": "string",
      "service": "string",
      "category": "string",
      "tags": ["tag1", "tag2"],
      "raw_log": "string",
      "structured_data": {},
      "request_id": "string",
      "session_id": "string",
      "correlation_id": "string",
      "ip_address": "192.168.1.1",
      "application_type": "string",
      "framework": "string",
      "http_method": "GET",
      "http_status": 200,
      "endpoint": "/api/endpoint",
      "response_time_ms": 145.67,
      "is_anomaly": false,
      "anomaly_type": "string",
      "error_details": {},
      "performance_metrics": {},
      "business_context": {}
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
    "postgres_count": 1,
    "elasticsearch_count": 1,
    "failed_count": 0,
    "validation_errors": [],
    "message": "Successfully ingested 1 logs"
  }
}
```

#### GET /api/logs/search
Search log entries.

**Query Parameters:**
- `q`: Search query text
- `source_type`: Filter by source type (splunk, sap, application)
- `level`: Filter by log level (DEBUG, INFO, WARN, ERROR, FATAL)
- `host`: Filter by host
- `service`: Filter by service
- `start_time`: Start time filter (ISO format)
- `end_time`: End time filter (ISO format)
- `is_anomaly`: Filter by anomaly status (true/false)
- `request_id`: Filter by request ID
- `session_id`: Filter by session ID
- `correlation_id`: Filter by correlation ID
- `ip_address`: Filter by IP address
- `limit`: Number of results (default: 100, max: 1000)
- `offset`: Offset for pagination (default: 0)
- `sort_field`: Field to sort by (default: timestamp)
- `sort_order`: Sort order (asc/desc, default: desc)

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "log_id": "log-123",
        "timestamp": "2025-09-19T10:30:00Z",
        "level": "INFO",
        "message": "User login successful",
        "source_type": "application",
        "host": "web-server-01",
        "service": "auth-service",
        "request_id": "req-1234567890",
        "ip_address": "192.168.1.100"
      }
    ],
    "total_count": 1000,
    "max_score": 1.5,
    "limit": 100,
    "offset": 0,
    "query": "login",
    "filters": {
      "level": "INFO",
      "source_type": "application"
    }
  }
}
```

#### GET /api/logs/correlation
Search logs by correlation.

**Query Parameters:**
- `key`: Correlation key (request_id, session_id, correlation_id, ip_address)
- `value`: Correlation value
- `limit`: Number of results (default: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "log_id": "log-123",
        "timestamp": "2025-09-19T10:30:00Z",
        "level": "INFO",
        "message": "Request processed",
        "request_id": "req-1234567890"
      }
    ],
    "correlation_key": "request_id",
    "correlation_value": "req-1234567890",
    "count": 5,
    "limit": 100
  }
}
```

#### GET /api/logs/statistics
Get log statistics and aggregations.

**Query Parameters:**
- `start_time`: Start time filter (ISO format)
- `end_time`: End time filter (ISO format)

**Response:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_logs": 10000,
      "logs_by_level": {
        "INFO": 8000,
        "WARN": 1500,
        "ERROR": 400,
        "FATAL": 100
      },
      "logs_by_source": {
        "application": 6000,
        "splunk": 3000,
        "sap": 1000
      },
      "anomaly_count": 50,
      "error_count": 500,
      "anomaly_rate": 0.5,
      "error_rate": 5.0,
      "avg_response_time_ms": 145.67,
      "top_endpoints": {
        "/api/users": 2000,
        "/api/logs": 1500,
        "/api/auth": 1000
      }
    }
  }
}
```

### System Health

#### GET /api/health
Check system health.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-09-19T10:30:00Z",
    "services": {
      "database": {
        "status": "healthy",
        "response_time_ms": 15
      },
      "elasticsearch": {
        "status": "healthy",
        "cluster_status": "green"
      },
      "rate_limiter": {
        "status": "healthy"
      }
    },
    "version": "1.1.0"
  }
}
```

## SDK Examples

### Python SDK

```python
import requests

class LogIntelligenceAPI:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def login(self, username, password):
        response = self.session.post(f'{self.base_url}/api/auth/login', json={
            'username': username,
            'password': password
        })
        return response.json()
    
    def search_logs(self, query, **filters):
        params = {'q': query, **filters}
        response = self.session.get(f'{self.base_url}/api/logs/search', params=params)
        return response.json()
    
    def ingest_logs(self, logs):
        response = self.session.post(f'{self.base_url}/api/logs/ingest', json={
            'logs': logs
        })
        return response.json()

# Usage
api = LogIntelligenceAPI('https://your-domain.vercel.app')
login_result = api.login('username', 'password')
api.session.headers.update({
    'Authorization': f'Bearer {login_result["data"]["access_token"]}'
})

# Search logs
results = api.search_logs('error', level='ERROR', limit=50)
print(f"Found {results['data']['total_count']} logs")

# Ingest logs
logs = [{
    'log_id': 'log-123',
    'timestamp': '2025-09-19T10:30:00Z',
    'level': 'INFO',
    'message': 'Test log entry',
    'source_type': 'application'
}]
ingest_result = api.ingest_logs(logs)
print(f"Ingested {ingest_result['data']['ingested_count']} logs")
```

### JavaScript SDK

```javascript
class LogIntelligenceAPI {
    constructor(baseUrl, apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.headers = {
            'Content-Type': 'application/json'
        };
        
        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/api/auth/login`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ username, password })
        });
        return response.json();
    }
    
    async searchLogs(query, filters = {}) {
        const params = new URLSearchParams({ q: query, ...filters });
        const response = await fetch(`${this.baseUrl}/api/logs/search?${params}`, {
            headers: this.headers
        });
        return response.json();
    }
    
    async ingestLogs(logs) {
        const response = await fetch(`${this.baseUrl}/api/logs/ingest`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ logs })
        });
        return response.json();
    }
}

// Usage
const api = new LogIntelligenceAPI('https://your-domain.vercel.app');
const loginResult = await api.login('username', 'password');
api.headers['Authorization'] = `Bearer ${loginResult.data.access_token}`;

// Search logs
const results = await api.searchLogs('error', { level: 'ERROR', limit: 50 });
console.log(`Found ${results.data.total_count} logs`);

// Ingest logs
const logs = [{
    log_id: 'log-123',
    timestamp: '2025-09-19T10:30:00Z',
    level: 'INFO',
    message: 'Test log entry',
    source_type: 'application'
}];
const ingestResult = await api.ingestLogs(logs);
console.log(`Ingested ${ingestResult.data.ingested_count} logs`);
```

## Error Codes

| Code | Description |
|------|-------------|
| `MISSING_FIELDS` | Required fields are missing |
| `INVALID_JSON` | Invalid JSON in request body |
| `VALIDATION_FAILED` | Data validation failed |
| `AUTHENTICATION_FAILED` | Authentication failed |
| `AUTHORIZATION_FAILED` | Insufficient permissions |
| `USER_NOT_FOUND` | User not found |
| `EMAIL_EXISTS` | Email already exists |
| `USERNAME_EXISTS` | Username already exists |
| `INVALID_TOKEN` | Invalid or expired token |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |

## Rate Limiting

Rate limits are applied per user and per endpoint:

- **Login**: 5 requests per 5 minutes
- **Register**: 3 requests per hour
- **API**: 1000 requests per hour
- **Search**: 100 requests per 5 minutes
- **Admin**: 200 requests per 5 minutes

When rate limits are exceeded, a 429 status code is returned with retry information.

## Security

- All passwords are hashed using PBKDF2 with 100,000 iterations
- JWT tokens are signed with HS256 algorithm
- API keys are cryptographically secure random strings
- Sensitive data is excluded from API responses
- Rate limiting prevents abuse
- Input validation prevents injection attacks

## Monitoring

All functions include comprehensive logging and monitoring:

- Request/response logging
- Performance metrics
- Error tracking
- Rate limit monitoring
- Security event logging

## Deployment

Functions are deployed to Vercel with the following configuration:

- **Runtime**: Python 3.9
- **Memory**: 1024MB
- **Timeout**: 30 seconds
- **Environment Variables**: Required for database and external service connections

## Support

For API support and questions:
- Check the error codes and messages
- Review the rate limiting headers
- Ensure proper authentication
- Validate request formats
