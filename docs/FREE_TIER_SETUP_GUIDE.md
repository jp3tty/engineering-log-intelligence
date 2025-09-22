# Free Tier Production Setup Guide

## 🎯 **Goal**
Set up a complete production environment using free tier services for minimal cost.

## 💰 **Cost Breakdown**
- **PostgreSQL (Railway)**: $5/month ✅ Already set up
- **Elasticsearch (AWS)**: $0/month (free tier)
- **Kafka (Confluent Cloud)**: $0/month (free tier)
- **Total Cost**: $5/month

## 🚀 **Step-by-Step Setup**

### **Phase 1: Elasticsearch Setup (AWS Free Tier)**

#### **Step 1.1: Create AWS Account**
1. Go to [AWS Console](https://aws.amazon.com/)
2. Click "Create an AWS Account"
3. Follow the signup process
4. **Important**: Use a credit card for verification (won't be charged for free tier)

#### **Step 1.2: Access Elasticsearch Service**
1. Log into AWS Console
2. Search for "Elasticsearch" in the services search
3. Click on "Amazon Elasticsearch Service" (now called "Amazon OpenSearch Service")

#### **Step 1.3: Create Domain**
1. Click "Create domain"
2. Choose "Development and testing" (free tier)
3. **Domain name**: `eng-log-intel` (must be 3-28 characters, lowercase, a-z, 0-9, and - only)
4. **Version**: Choose latest available (e.g., OpenSearch 2.11)
5. **Instance type**: `t3.small.search` (free tier eligible)
6. **Instance count**: 1
7. **Storage**: 10 GB (free tier limit)

#### **Step 1.4: Configure Access**
1. **Access policy**: Choose "Allow open access to the domain"
2. **Fine-grained access control**: Disable (for simplicity)
3. **Encryption**: Enable at rest (recommended)

#### **Step 1.5: Review and Create**
1. Review all settings
2. Click "Create"
3. Wait 10-15 minutes for domain to be ready

#### **Step 1.6: Get Connection Details**
1. Once domain is active, click on it
2. Note the **Domain endpoint** (e.g., `search-eng-log-intel-xxxxx.us-east-1.es.amazonaws.com`)
3. **Port**: 443 (HTTPS)
4. **Region**: Note your AWS region

### **Phase 2: Kafka Setup (Confluent Cloud Free Tier)**

#### **Step 2.1: Create Confluent Cloud Account**
1. Go to [Confluent Cloud](https://www.confluent.io/confluent-cloud/)
2. Click "Start free" or "Sign up"
3. Enter your email and create password
4. Verify your email address

#### **Step 2.2: Create Cluster**
1. After login, you'll see the Confluent Cloud console
2. Click "Create cluster"
3. Choose **"Basic"** plan (free tier)
4. **Cluster name**: `engineering-log-intelligence`
5. **Cloud provider**: Choose AWS (recommended)
6. **Region**: Choose closest to your location (e.g., us-east-1)

#### **Step 2.3: Configure Cluster**
1. **Cluster type**: Basic
2. **Availability**: Single zone (free tier)
3. **Storage**: 5 GB (free tier limit)
4. Click "Create cluster"
5. Wait 2-3 minutes for cluster to be ready

#### **Step 2.4: Get Connection Details**
1. Once cluster is ready, click on it
2. Go to "Cluster settings" → "API Keys"
3. Click "Create API key"
4. **Key name**: `engineering-log-intelligence-key`
5. **Description**: `API key for log intelligence platform`
6. Click "Create key"
7. **IMPORTANT**: Copy and save both:
   - **API Key**: `XXXXXXXXXXXXXX`
   - **API Secret**: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

#### **Step 2.5: Get Bootstrap Servers**
1. In cluster settings, go to "Cluster settings" → "Cluster details"
2. Note the **Bootstrap servers** (e.g., `pkc-xxxxx.us-east-1.aws.confluent.cloud:9092`)
3. Note the **Cluster ID** (e.g., `lkc-xxxxx`)

#### **Step 2.6: Create Topics**
1. Go to "Topics" in the left sidebar
2. Click "Create topic"
3. **Topic name**: `engineering-logs`
4. **Partitions**: 1 (free tier limit)
5. **Replication factor**: 1 (free tier limit)
6. Click "Create topic"
7. Repeat for topic: `engineering-alerts`

### **Phase 3: Add Environment Variables to Vercel**

#### **Step 3.1: Run the Setup Script**
```bash
cd engineering_log_intelligence
./scripts/setup-elasticsearch-kafka.sh
```

#### **Step 3.2: Manual Setup (Alternative)**
If you prefer to add variables manually:

```bash
# Elasticsearch
echo "https://search-eng-log-intel-xxxxx.us-east-1.es.amazonaws.com" | vercel env add ELASTICSEARCH_URL production
echo "443" | vercel env add ELASTICSEARCH_PORT production
echo "engineering_logs" | vercel env add ELASTICSEARCH_INDEX production
echo "" | vercel env add ELASTICSEARCH_USERNAME production
echo "" | vercel env add ELASTICSEARCH_PASSWORD production

# Kafka
echo "pkc-xxxxx.us-east-1.aws.confluent.cloud:9092" | vercel env add KAFKA_BOOTSTRAP_SERVERS production
echo "XXXXXXXXXXXXXX" | vercel env add KAFKA_API_KEY production
echo "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" | vercel env add KAFKA_API_SECRET production
echo "engineering-logs" | vercel env add KAFKA_TOPIC_LOGS production
echo "engineering-alerts" | vercel env add KAFKA_TOPIC_ALERTS production
echo "engineering-log-intelligence-group" | vercel env add KAFKA_GROUP_ID production
```

### **Phase 4: Test All Connections**

#### **Step 4.1: Test Locally**
```bash
python3 test_connections.py
```

#### **Step 4.2: Deploy and Test Production**
```bash
vercel --prod
```

## 🧪 **Testing Your Setup**

### **Test 1: Local Connection Test**
```bash
python3 test_connections.py
```

Expected output:
```
🧪 Production Service Connection Test
====================================

🐘 Testing PostgreSQL...
   ✅ PostgreSQL connected successfully!
   📊 Database version: PostgreSQL 17.6...

🔍 Testing Elasticsearch...
   ✅ Elasticsearch connected successfully!
   📊 Cluster name: eng-log-intel
   📊 Version: 2.11.0

📡 Testing Kafka...
   ✅ Kafka connected successfully!
   📊 Cluster ID: lkc-xxxxx
   📊 Cluster name: eng-log-intel

📊 Test Results Summary
=======================
   POSTGRESQL: ✅ PASS
   ELASTICSEARCH: ✅ PASS
   KAFKA: ✅ PASS

🎉 All services connected successfully!
   Your production environment is ready!
```

### **Test 2: Production Deployment Test**
```bash
vercel --prod
```

Check your production URL and verify all services are working.

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Elasticsearch Issues**
- **Domain creation fails**: Try a different AWS region
- **Connection timeout**: Check security groups and access policies
- **Authentication error**: Verify access policy allows open access

#### **Kafka Issues**
- **Cluster creation fails**: Try a different region
- **API key error**: Verify you copied both key and secret correctly
- **Connection timeout**: Check network connectivity

#### **Vercel Issues**
- **Environment variable not found**: Ensure you're adding to production environment
- **Deployment fails**: Check all required environment variables are set

### **Getting Help**
1. Check the individual setup guides:
   - `docs/ELASTICSEARCH_SETUP_GUIDE.md`
   - `docs/KAFKA_SETUP_GUIDE.md`
2. Run the test script: `python3 test_connections.py`
3. Check Vercel logs: `vercel logs`

## 📊 **Monitoring Your Usage**

### **AWS Elasticsearch**
- Monitor usage in AWS Billing Dashboard
- Set up billing alerts
- Check Elasticsearch service metrics

### **Confluent Cloud**
- Monitor usage in Confluent Cloud console
- Check cluster metrics and storage usage
- Set up usage alerts

### **Railway PostgreSQL**
- Monitor usage in Railway dashboard
- Check database metrics and storage

## 🎉 **Success!**

Once all tests pass, you'll have:
- ✅ PostgreSQL database (Railway) - $5/month
- ✅ Elasticsearch cluster (AWS) - $0/month
- ✅ Kafka cluster (Confluent Cloud) - $0/month
- ✅ Complete production environment
- ✅ All services connected and tested

**Total monthly cost: $5** 🎉

## 🚀 **Next Steps**

After successful setup:
1. Deploy your application to production
2. Test all API endpoints
3. Set up monitoring and alerts
4. Configure log ingestion
5. Test the complete system end-to-end

Your production environment is now ready for Phase 3 development! 🚀
