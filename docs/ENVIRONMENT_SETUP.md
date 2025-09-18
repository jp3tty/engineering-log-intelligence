# Environment Setup Guide

This guide explains how to set up and manage the development and production environments for the Engineering Log Intelligence System.

## Environment Overview

The project uses a hybrid architecture with:
- **Vercel Functions** for serverless API endpoints
- **External Services** for persistent data storage and processing
- **Docker Compose** for local development
- **Cloud Services** for production

## Development Environment (dev)

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+
- Vercel CLI

### Quick Setup

1. **Run the setup script:**
   ```bash
   ./scripts/setup-dev.sh
   ```

2. **Start Vercel development server:**
   ```bash
   vercel dev
   ```

### Manual Setup

1. **Start external services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Set up environment variables:**
   ```bash
   cp env.development .env
   ```

3. **Install dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Start Vercel:**
   ```bash
   vercel dev
   ```

### Development Services

| Service | URL | Purpose |
|---------|-----|---------|
| Vercel Functions | http://localhost:3000/api | API endpoints |
| PostgreSQL | localhost:5432 | Database |
| Elasticsearch | http://localhost:9200 | Log storage and search |
| Kafka | localhost:9092 | Message streaming |
| Kafka UI | http://localhost:8080 | Kafka monitoring |
| Redis | localhost:6379 | Caching |

### Development Features

- **Hot reloading** for Vercel Functions
- **Local database** with sample data
- **Debug logging** enabled
- **CORS** configured for local development
- **Rate limiting** relaxed for testing

## Production Environment (prod)

### Prerequisites

- Vercel CLI installed and authenticated
- External services configured (PostgreSQL, Elasticsearch, Kafka)
- AWS credentials for S3 storage

### Quick Setup

1. **Run the setup script:**
   ```bash
   ./scripts/setup-prod.sh
   ```

2. **Configure environment variables:**
   ```bash
   vercel env add DATABASE_URL
   vercel env add ELASTICSEARCH_URL
   vercel env add KAFKA_BOOTSTRAP_SERVERS
   vercel env add JWT_SECRET_KEY
   ```

### Manual Setup

1. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

2. **Set environment variables:**
   ```bash
   vercel env add <VARIABLE_NAME>
   ```

3. **Configure external services:**
   - Set up PostgreSQL database
   - Configure Elasticsearch cluster
   - Set up Kafka cluster
   - Configure AWS S3 bucket

### Production Services

| Service | Provider | Purpose |
|---------|----------|---------|
| Vercel Functions | Vercel | API endpoints |
| PostgreSQL | Railway/Supabase/Neon | Database |
| Elasticsearch | AWS/GCP | Log storage and search |
| Kafka | Confluent Cloud/AWS MSK | Message streaming |
| S3 | AWS | File storage |

### Production Features

- **Global CDN** for fast content delivery
- **Auto-scaling** based on demand
- **SSL/TLS** encryption
- **Rate limiting** for security
- **Monitoring** and logging

## Environment Variables

### Required Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `DATABASE_URL` | `postgresql://dev_user:dev_password@localhost:5432/log_intelligence_dev` | `postgresql://user:pass@host:port/db` | Database connection string |
| `ELASTICSEARCH_URL` | `http://localhost:9200` | `https://elasticsearch-host:9200` | Elasticsearch endpoint |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | `kafka-host:9092` | Kafka brokers |
| `JWT_SECRET_KEY` | `dev-secret-key` | `production-secret-key` | JWT signing key |

### Optional Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `DEBUG` | `true` | `false` | Debug mode |
| `LOG_LEVEL` | `DEBUG` | `INFO` | Logging level |
| `CORS_ORIGINS` | `http://localhost:3000` | `https://app.vercel.app` | Allowed origins |
| `RATE_LIMIT_REQUESTS` | `1000` | `100` | Rate limit per hour |

## Switching Between Environments

### Development to Production

1. **Stop development services:**
   ```bash
   docker-compose -f docker-compose.dev.yml down
   ```

2. **Switch to production:**
   ```bash
   vercel --prod
   ```

### Production to Development

1. **Switch to development:**
   ```bash
   vercel dev
   ```

2. **Start development services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Check if ports 3000, 5432, 9200, 9092 are available
   - Stop conflicting services

2. **Docker issues:**
   - Ensure Docker is running
   - Check Docker Compose version compatibility

3. **Vercel issues:**
   - Ensure you're logged in: `vercel whoami`
   - Check Vercel CLI version

4. **Database connection:**
   - Verify PostgreSQL is running
   - Check connection string format

5. **Elasticsearch issues:**
   - Check if Elasticsearch is accessible
   - Verify index mapping

### Debug Commands

```bash
# Check service status
docker-compose -f docker-compose.dev.yml ps

# View service logs
docker-compose -f docker-compose.dev.yml logs -f

# Test database connection
docker exec log_intelligence_postgres_dev pg_isready -U dev_user

# Test Elasticsearch
curl http://localhost:9200/_cluster/health

# Test Kafka
docker exec log_intelligence_kafka_dev kafka-topics --bootstrap-server localhost:9092 --list

# Test Vercel Functions
curl http://localhost:3000/api/health/check
```

## Security Considerations

### Development

- Use weak passwords for local services
- Disable SSL/TLS for local development
- Allow all CORS origins
- Enable debug logging

### Production

- Use strong, unique passwords
- Enable SSL/TLS encryption
- Restrict CORS origins
- Disable debug logging
- Use environment variables for secrets
- Enable rate limiting
- Monitor for security issues

## Monitoring and Logging

### Development

- Local logs in terminal
- Docker Compose logs
- Vercel dev logs

### Production

- Vercel function logs
- External service monitoring
- Application performance monitoring
- Error tracking and alerting

---

**Last Updated**: September 17, 2025  
**Version**: 1.0
