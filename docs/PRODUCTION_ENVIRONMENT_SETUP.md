# Production Environment Setup Guide

**Phase 3, Day 13: Production Infrastructure Setup**  
**Last Updated:** September 19, 2025

## Overview

This guide walks you through setting up production environment variables in Vercel for the Engineering Log Intelligence System. We'll configure all the necessary services and security settings for a production deployment.

## Prerequisites

- Vercel CLI installed (`npm install -g vercel`)
- Vercel account with project access
- Production database credentials
- Production Elasticsearch credentials
- Production Kafka credentials
- AWS credentials (for S3 and ML services)

## Step 1: Vercel Project Setup

### 1.1 Login to Vercel
```bash
vercel login
```

### 1.2 Link Project to Vercel
```bash
cd engineering_log_intelligence
vercel link
```

### 1.3 Verify Project Configuration
```bash
vercel env ls
```

## Step 2: Environment Variables Configuration

### 2.1 Required Environment Variables

We need to set these environment variables in Vercel for production:

#### Database Configuration
```bash
# PostgreSQL Production Database
DATABASE_URL=postgresql://prod_user:secure_password@prod-host:5432/log_intelligence_prod
POSTGRES_HOST=your-production-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=log_intelligence_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=your_secure_production_password
```

#### Elasticsearch Configuration
```bash
# Elasticsearch Production Cluster
ELASTICSEARCH_URL=https://your-elasticsearch-cluster.com:9200
ELASTICSEARCH_USERNAME=prod_user
ELASTICSEARCH_PASSWORD=your_secure_elasticsearch_password
ELASTICSEARCH_INDEX=logs_prod
```

#### Kafka Configuration
```bash
# Kafka Production Cluster
KAFKA_BOOTSTRAP_SERVERS=your-kafka-cluster.com:9092
KAFKA_TOPIC_LOGS=log-ingestion-prod
KAFKA_TOPIC_ALERTS=alerts-prod
KAFKA_GROUP_ID=log-processor-prod
```

#### Authentication & Security
```bash
# JWT Authentication (CRITICAL: Generate a secure key!)
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-256-bits
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### AWS Services
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=engineering-log-intelligence-prod
AWS_REGION=us-west-2
```

#### ML Services
```bash
# Machine Learning Services
ML_MODEL_BUCKET=ml-models-prod
ML_ENDPOINT_URL=https://your-ml-endpoint.com
```

#### Application Settings
```bash
# Application Configuration
APP_NAME=Engineering Log Intelligence
APP_VERSION=1.2.0
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
```

#### CORS Configuration
```bash
# CORS Settings
CORS_ORIGINS=https://engineering-log-intelligence.vercel.app,https://your-domain.com
```

### 2.2 Setting Environment Variables in Vercel

#### Method 1: Using Vercel CLI (Recommended)
```bash
# Set each environment variable
vercel env add DATABASE_URL production
vercel env add POSTGRES_HOST production
vercel env add POSTGRES_PORT production
vercel env add POSTGRES_DB production
vercel env add POSTGRES_USER production
vercel env add POSTGRES_PASSWORD production

vercel env add ELASTICSEARCH_URL production
vercel env add ELASTICSEARCH_USERNAME production
vercel env add ELASTICSEARCH_PASSWORD production
vercel env add ELASTICSEARCH_INDEX production

vercel env add KAFKA_BOOTSTRAP_SERVERS production
vercel env add KAFKA_TOPIC_LOGS production
vercel env add KAFKA_TOPIC_ALERTS production
vercel env add KAFKA_GROUP_ID production

vercel env add JWT_SECRET_KEY production
vercel env add JWT_ALGORITHM production
vercel env add JWT_ACCESS_TOKEN_EXPIRE_MINUTES production

vercel env add AWS_ACCESS_KEY_ID production
vercel env add AWS_SECRET_ACCESS_KEY production
vercel env add AWS_S3_BUCKET production
vercel env add AWS_REGION production

vercel env add ML_MODEL_BUCKET production
vercel env add ML_ENDPOINT_URL production

vercel env add APP_NAME production
vercel env add APP_VERSION production
vercel env add DEBUG production
vercel env add LOG_LEVEL production
vercel env add ENVIRONMENT production

vercel env add CORS_ORIGINS production
```

#### Method 2: Using Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable with:
   - **Name**: The environment variable name
   - **Value**: The production value
   - **Environment**: Production
   - **Encrypt**: Yes (for sensitive values)

### 2.3 Verify Environment Variables
```bash
# List all environment variables
vercel env ls

# Pull environment variables to verify
vercel env pull .env.production
```

## Step 3: Production Database Setup

### 3.1 PostgreSQL Production Database

#### Option A: Railway (Recommended for beginners)
1. Go to [railway.app](https://railway.app)
2. Create new project
3. Add PostgreSQL service
4. Copy connection string to `DATABASE_URL`

#### Option B: Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → Database
4. Copy connection string to `DATABASE_URL`

#### Option C: Neon
1. Go to [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string to `DATABASE_URL`

### 3.2 Database Schema Setup
```bash
# Run database migrations in production
vercel env pull .env.production
python -m api.utils.database migrate
```

## Step 4: Elasticsearch Production Setup

### 4.1 Elasticsearch Service

#### Option A: AWS Elasticsearch
1. Go to AWS Console → Elasticsearch
2. Create domain
3. Configure security groups
4. Get endpoint URL

#### Option B: Elastic Cloud
1. Go to [cloud.elastic.co](https://cloud.elastic.co)
2. Create deployment
3. Get endpoint URL and credentials

### 4.2 Elasticsearch Index Setup
```bash
# Create production index
python -c "
from api.utils.elasticsearch import ElasticsearchService
es = ElasticsearchService()
es.create_index('logs_prod')
"
```

## Step 5: Kafka Production Setup

### 5.1 Kafka Service

#### Option A: Confluent Cloud
1. Go to [confluent.cloud](https://confluent.cloud)
2. Create cluster
3. Get bootstrap servers
4. Create topics

#### Option B: AWS MSK
1. Go to AWS Console → MSK
2. Create cluster
3. Get bootstrap servers
4. Create topics

### 5.2 Kafka Topics Setup
```bash
# Create production topics
python -c "
from api.utils.kafka import KafkaService
kafka = KafkaService()
kafka.create_topic('log-ingestion-prod')
kafka.create_topic('alerts-prod')
"
```

## Step 6: Security Configuration

### 6.1 Generate Secure JWT Secret
```python
import secrets
import base64

# Generate a secure 256-bit secret
secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
print(f"JWT_SECRET_KEY={secret}")
```

### 6.2 Set Security Headers
Update `vercel.production.json`:
```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        }
      ]
    }
  ]
}
```

## Step 7: Production Deployment

### 7.1 Deploy to Production
```bash
# Deploy to production
vercel --prod

# Verify deployment
vercel ls
```

### 7.2 Test Production Environment
```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health/check

# Test authentication
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

## Step 8: Monitoring Setup

### 8.1 Vercel Analytics
```bash
# Enable Vercel Analytics
vercel env add VERCEL_ANALYTICS_ID production
```

### 8.2 Custom Monitoring
```bash
# Add monitoring environment variables
vercel env add MONITORING_ENABLED production true
vercel env add ALERT_WEBHOOK_URL production https://your-webhook.com
```

## Troubleshooting

### Common Issues

1. **Environment Variables Not Loading**
   ```bash
   # Check if variables are set
   vercel env ls
   
   # Redeploy after adding variables
   vercel --prod
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   python -c "
   from api.utils.database import get_database_connection
   conn = get_database_connection()
   print('Database connected successfully')
   "
   ```

3. **Elasticsearch Connection Issues**
   ```bash
   # Test Elasticsearch connection
   python -c "
   from api.utils.elasticsearch import ElasticsearchService
   es = ElasticsearchService()
   print('Elasticsearch connected successfully')
   "
   ```

## Security Checklist

- [ ] JWT secret key is secure and unique
- [ ] Database credentials are strong
- [ ] All sensitive data is encrypted
- [ ] CORS is properly configured
- [ ] Security headers are set
- [ ] Environment variables are not exposed in logs
- [ ] HTTPS is enforced
- [ ] Rate limiting is enabled

## Next Steps

After completing this setup:
1. **Day 14**: Security & Compliance implementation
2. **Day 15**: Performance & Scalability optimization
3. **Day 16**: Monitoring & Operations setup
4. **Days 17-19**: ML Pipeline integration

---

**Important Notes:**
- Never commit production credentials to Git
- Use Vercel's environment variable encryption
- Regularly rotate secrets and passwords
- Monitor for security vulnerabilities
- Keep documentation updated
