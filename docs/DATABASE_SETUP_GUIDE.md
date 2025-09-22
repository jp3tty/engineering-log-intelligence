# Production Database Setup Guide

**Day 14: Security & Compliance - Database Setup**  
**Last Updated:** September 19, 2025

## Overview

This guide walks you through setting up production databases for the Engineering Log Intelligence System. We'll set up PostgreSQL, Elasticsearch, and Kafka for production use.

## 🗄️ Step 1: PostgreSQL Production Database

### Option A: Railway (Recommended for Beginners)

**Why Railway?**
- ✅ Easy setup (5 minutes)
- ✅ Generous free tier (500MB database, 1GB bandwidth)
- ✅ Automatic backups
- ✅ Built-in connection pooling
- ✅ No credit card required

**Setup Steps:**

1. **Go to Railway**: [railway.app](https://railway.app)
2. **Sign up** with your GitHub account
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"** (or "Provision PostgreSQL" for quick setup)
5. **Choose your repository** or create a new one
6. **Add PostgreSQL service**:
   - Click "New" → "Database" → "PostgreSQL"
   - Wait for deployment (2-3 minutes)
7. **Get connection details**:
   - Click on your PostgreSQL service
   - Go to "Connect" tab
   - Copy the connection string

**Connection String Format:**
```
postgresql://postgres:password@host:port/railway
```

### Option B: Supabase (Alternative)

**Why Supabase?**
- ✅ PostgreSQL with additional features
- ✅ Built-in authentication
- ✅ Real-time subscriptions
- ✅ Free tier: 500MB database

**Setup Steps:**

1. **Go to Supabase**: [supabase.com](https://supabase.com)
2. **Sign up** with your GitHub account
3. **Create new project**
4. **Wait for setup** (2-3 minutes)
5. **Get connection string**:
   - Go to Settings → Database
   - Copy the connection string

### Option C: Neon (Serverless PostgreSQL)

**Why Neon?**
- ✅ Serverless PostgreSQL
- ✅ Automatic scaling
- ✅ Free tier: 3GB storage
- ✅ Branching (like Git for databases)

**Setup Steps:**

1. **Go to Neon**: [neon.tech](https://neon.tech)
2. **Sign up** with your GitHub account
3. **Create new project**
4. **Get connection string**:
   - Copy the connection string from dashboard

## 🔍 Step 2: Elasticsearch Production Cluster

### Option A: AWS Elasticsearch (Recommended)

**Why AWS Elasticsearch?**
- ✅ Fully managed service
- ✅ High availability
- ✅ Security built-in
- ✅ Free tier: 1 month free

**Setup Steps:**

1. **Go to AWS Console**: [aws.amazon.com](https://aws.amazon.com)
2. **Sign up** for AWS account (if needed)
3. **Go to Elasticsearch service**
4. **Create domain**:
   - Domain name: `engineering-log-intelligence`
   - Instance type: `t3.small.elasticsearch` (free tier)
   - Storage: 10GB
   - Access policy: Allow access from anywhere (for now)
5. **Wait for deployment** (10-15 minutes)
6. **Get endpoint URL**:
   - Copy the domain endpoint

### Option B: Elastic Cloud (Alternative)

**Why Elastic Cloud?**
- ✅ Official Elastic service
- ✅ Easy setup
- ✅ Free trial: 14 days

**Setup Steps:**

1. **Go to Elastic Cloud**: [cloud.elastic.co](https://cloud.elastic.co)
2. **Sign up** for free trial
3. **Create deployment**
4. **Get endpoint URL**

## 📡 Step 3: Kafka Production Cluster

### Option A: Confluent Cloud (Recommended)

**Why Confluent Cloud?**
- ✅ Fully managed Kafka
- ✅ Easy setup
- ✅ Free tier: 1GB storage

**Setup Steps:**

1. **Go to Confluent Cloud**: [confluent.cloud](https://confluent.cloud)
2. **Sign up** for free account
3. **Create cluster**:
   - Cluster name: `engineering-log-intelligence`
   - Region: Choose closest to you
   - Type: Basic (free)
4. **Create topics**:
   - `log-ingestion-prod`
   - `alerts-prod`
5. **Get bootstrap servers**:
   - Copy the bootstrap server URL

### Option B: AWS MSK (Alternative)

**Why AWS MSK?**
- ✅ Fully managed Kafka on AWS
- ✅ High availability
- ✅ Security built-in

## 🔧 Step 4: Environment Variables Setup

Once you have all your database credentials, we'll add them to Vercel:

### Required Environment Variables

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/database
POSTGRES_HOST=your-postgres-host
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password

# Elasticsearch
ELASTICSEARCH_URL=https://your-elasticsearch-cluster.com:9200
ELASTICSEARCH_USERNAME=your-username
ELASTICSEARCH_PASSWORD=your-password

# Kafka
KAFKA_BOOTSTRAP_SERVERS=your-kafka-cluster.com:9092
```

### Adding to Vercel

```bash
# Add each variable
vercel env add DATABASE_URL production
vercel env add POSTGRES_HOST production
vercel env add POSTGRES_USER production
vercel env add POSTGRES_PASSWORD production
vercel env add ELASTICSEARCH_URL production
vercel env add ELASTICSEARCH_USERNAME production
vercel env add ELASTICSEARCH_PASSWORD production
vercel env add KAFKA_BOOTSTRAP_SERVERS production
```

## 🧪 Step 5: Testing Database Connections

### Test PostgreSQL Connection

```python
# Test database connection
python -c "
from api.utils.database import get_database_connection
conn = get_database_connection()
print('PostgreSQL connected successfully')
"
```

### Test Elasticsearch Connection

```python
# Test Elasticsearch connection
python -c "
from api.utils.elasticsearch import ElasticsearchService
es = ElasticsearchService()
print('Elasticsearch connected successfully')
"
```

### Test Kafka Connection

```python
# Test Kafka connection
python -c "
from api.utils.kafka import KafkaService
kafka = KafkaService()
print('Kafka connected successfully')
"
```

## 📊 Step 6: Database Schema Setup

### PostgreSQL Schema

```sql
-- Create tables
CREATE TABLE IF NOT EXISTS log_entries (
    id SERIAL PRIMARY KEY,
    log_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX idx_log_entries_level ON log_entries(level);
CREATE INDEX idx_log_entries_source_type ON log_entries(source_type);
```

### Elasticsearch Index

```json
{
  "mappings": {
    "properties": {
      "log_id": {"type": "keyword"},
      "timestamp": {"type": "date"},
      "level": {"type": "keyword"},
      "message": {"type": "text"},
      "source_type": {"type": "keyword"}
    }
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Check firewall settings
   - Verify connection string
   - Check network connectivity

2. **Authentication Failed**
   - Verify username/password
   - Check database permissions
   - Ensure user exists

3. **SSL Certificate Issues**
   - Add `?sslmode=require` to PostgreSQL URL
   - Check certificate validity

### Getting Help

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Supabase**: [docs.supabase.com](https://docs.supabase.com)
- **Neon**: [docs.neon.tech](https://docs.neon.tech)
- **AWS Elasticsearch**: [docs.aws.amazon.com/elasticsearch](https://docs.aws.amazon.com/elasticsearch)
- **Confluent Cloud**: [docs.confluent.io](https://docs.confluent.io)

## 📋 Checklist

- [ ] PostgreSQL database created and accessible
- [ ] Elasticsearch cluster created and accessible
- [ ] Kafka cluster created and accessible
- [ ] Environment variables added to Vercel
- [ ] Database connections tested
- [ ] Schema created in PostgreSQL
- [ ] Index created in Elasticsearch
- [ ] Topics created in Kafka

## 🎯 Next Steps

After completing database setup:
1. **Test all connections**
2. **Run database migrations**
3. **Test API endpoints with real databases**
4. **Move to Day 15: Performance & Scalability**

---

**Important Notes:**
- Keep your database credentials secure
- Use strong passwords
- Enable backups
- Monitor usage and costs
- Test everything before going live
