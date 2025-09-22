# Vercel Environment Variables - Quick Reference

**Phase 3, Day 13: Production Infrastructure Setup**

## 🚀 Quick Start

### 1. Run the Setup Script
```bash
cd engineering_log_intelligence
./scripts/setup-production-simple.sh
```

### 2. Manual Setup (Alternative)
```bash
# Login to Vercel
vercel login

# Link project
vercel link

# Set environment variables one by one
vercel env add DATABASE_URL production
vercel env add JWT_SECRET_KEY production
# ... (see full list below)
```

## 📋 Complete Environment Variables List

### Required Variables (Must Set)
```bash
# Authentication
JWT_SECRET_KEY=your-super-secure-jwt-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
POSTGRES_HOST=your-postgres-host
POSTGRES_DB=log_intelligence_prod
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password

# Elasticsearch
ELASTICSEARCH_URL=https://your-elasticsearch-cluster.com:9200
ELASTICSEARCH_USERNAME=your-username
ELASTICSEARCH_PASSWORD=your-password
ELASTICSEARCH_INDEX=logs_prod

# Kafka
KAFKA_BOOTSTRAP_SERVERS=your-kafka-cluster.com:9092
KAFKA_TOPIC_LOGS=log-ingestion-prod
KAFKA_TOPIC_ALERTS=alerts-prod
KAFKA_GROUP_ID=log-processor-prod
```

### Optional Variables (Can Set Later)
```bash
# AWS Services
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-s3-bucket
AWS_REGION=us-west-2

# ML Services
ML_MODEL_BUCKET=ml-models-bucket
ML_ENDPOINT_URL=https://your-ml-endpoint.com

# Application Settings
APP_NAME=Engineering Log Intelligence
APP_VERSION=1.2.0
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# CORS
CORS_ORIGINS=https://your-domain.com

# Monitoring
MONITORING_ENABLED=true
ALERT_WEBHOOK_URL=https://your-webhook.com
```

## 🔧 Common Commands

### List Environment Variables
```bash
vercel env ls
```

### Add Single Variable
```bash
vercel env add VARIABLE_NAME production
```

### Remove Variable
```bash
vercel env rm VARIABLE_NAME production
```

### Pull Environment Variables
```bash
vercel env pull .env.production
```

### Deploy to Production
```bash
vercel --prod
```

## 🛠️ Service Setup Guides

### PostgreSQL (Choose One)
- **Railway**: [railway.app](https://railway.app) - Easiest for beginners
- **Supabase**: [supabase.com](https://supabase.com) - Good for full-stack apps
- **Neon**: [neon.tech](https://neon.tech) - Serverless PostgreSQL
- **AWS RDS**: [aws.amazon.com/rds](https://aws.amazon.com/rds) - Enterprise grade

### Elasticsearch (Choose One)
- **AWS Elasticsearch**: [aws.amazon.com/elasticsearch](https://aws.amazon.com/elasticsearch)
- **Elastic Cloud**: [cloud.elastic.co](https://cloud.elastic.co)
- **Self-hosted**: Install on your own servers

### Kafka (Choose One)
- **Confluent Cloud**: [confluent.cloud](https://confluent.cloud) - Managed Kafka
- **AWS MSK**: [aws.amazon.com/msk](https://aws.amazon.com/msk) - Amazon's managed Kafka
- **Self-hosted**: Install on your own servers

## 🔐 Security Best Practices

### JWT Secret Generation
```python
import secrets
import base64

# Generate secure 256-bit secret
secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
print(f"JWT_SECRET_KEY={secret}")
```

### Password Requirements
- **Database passwords**: At least 16 characters, mixed case, numbers, symbols
- **JWT secret**: 256-bit (32 bytes) random key
- **API keys**: Use service-provided keys, rotate regularly

### Environment Variable Security
- ✅ Use Vercel's built-in encryption
- ✅ Never commit secrets to Git
- ✅ Use different secrets for each environment
- ✅ Rotate secrets regularly
- ❌ Don't use default/example values in production
- ❌ Don't log sensitive environment variables

## 🚨 Troubleshooting

### Environment Variables Not Loading
```bash
# Check if variables are set
vercel env ls

# Redeploy after adding variables
vercel --prod

# Check logs for errors
vercel logs
```

### Database Connection Issues
```bash
# Test database connection
python -c "
from api.utils.database import get_database_connection
conn = get_database_connection()
print('Database connected successfully')
"
```

### Elasticsearch Connection Issues
```bash
# Test Elasticsearch connection
python -c "
from api.utils.elasticsearch import ElasticsearchService
es = ElasticsearchService()
print('Elasticsearch connected successfully')
"
```

## 📞 Getting Help

### Vercel Documentation
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Deployment](https://vercel.com/docs/concepts/deployments)
- [Troubleshooting](https://vercel.com/docs/concepts/troubleshooting)

### Project Documentation
- [Production Environment Setup](docs/PRODUCTION_ENVIRONMENT_SETUP.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [API Documentation](docs/VERCEL_FUNCTIONS_API.md)

---

**Remember**: Take your time with the setup. It's better to do it right the first time than to fix security issues later!
