# Kafka Setup Guide - Confluent Cloud Free Tier

## 🎯 **Goal**
Set up Kafka using Confluent Cloud free tier for real-time log streaming.

## 📋 **Prerequisites**
- Email address for Confluent Cloud account
- Basic understanding of messaging systems

## 🚀 **Step-by-Step Setup**

### **Step 1: Create Confluent Cloud Account**
1. Go to [Confluent Cloud](https://www.confluent.io/confluent-cloud/)
2. Click "Start free" or "Sign up"
3. Enter your email and create password
4. Verify your email address

### **Step 2: Create Cluster**
1. After login, you'll see the Confluent Cloud console
2. Click "Create cluster"
3. Choose **"Basic"** plan (free tier)
4. **Cluster name**: `engineering-log-intelligence`
5. **Cloud provider**: Choose AWS (recommended)
6. **Region**: Choose closest to your location (e.g., us-east-1)

### **Step 3: Configure Cluster**
1. **Cluster type**: Basic
2. **Availability**: Single zone (free tier)
3. **Storage**: 5 GB (free tier limit)
4. Click "Create cluster"
5. Wait 2-3 minutes for cluster to be ready

### **Step 4: Get Connection Details**
1. Once cluster is ready, click on it
2. Go to "Cluster settings" → "API Keys"
3. Click "Create API key"
4. **Key name**: `engineering-log-intelligence-key`
5. **Description**: `API key for log intelligence platform`
6. Click "Create key"
7. **IMPORTANT**: Copy and save both:
   - **API Key**: `XXXXXXXXXXXXXX`
   - **API Secret**: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

### **Step 5: Get Bootstrap Servers**
1. In cluster settings, go to "Cluster settings" → "Cluster details"
2. Note the **Bootstrap servers** (e.g., `pkc-xxxxx.us-east-1.aws.confluent.cloud:9092`)
3. Note the **Cluster ID** (e.g., `lkc-xxxxx`)

### **Step 6: Create Topics**
1. Go to "Topics" in the left sidebar
2. Click "Create topic"
3. **Topic name**: `engineering-logs`
4. **Partitions**: 1 (free tier limit)
5. **Replication factor**: 1 (free tier limit)
6. Click "Create topic"
7. Repeat for topic: `engineering-alerts`

## 🔧 **Environment Variables to Add**

Once you have the connection details, we'll add these to Vercel:

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=pkc-xxxxx.us-east-1.aws.confluent.cloud:9092
KAFKA_API_KEY=XXXXXXXXXXXXXX
KAFKA_API_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
KAFKA_TOPIC_LOGS=engineering-logs
KAFKA_TOPIC_ALERTS=engineering-alerts
KAFKA_GROUP_ID=engineering-log-intelligence-group
```

## 🧪 **Testing Connection**

After setup, we'll test the connection with a simple Python script.

## 💰 **Cost Information**
- **Free Tier**: 5 GB storage, 1 MB/s throughput
- **Data Transfer**: 1 GB/month free
- **Topics**: Up to 5 topics
- **Estimated Cost**: $0/month (within free tier limits)

## ⚠️ **Important Notes**
- Free tier has usage limits (5 GB storage, 1 MB/s throughput)
- API keys are sensitive - keep them secure
- Cluster takes 2-3 minutes to create
- Topics are created automatically when first used

## 🆘 **Troubleshooting**
- If cluster creation fails, try a different region
- Ensure you're using the correct API key and secret
- Check Confluent Cloud service status
- Verify your account is not suspended

## 📞 **Next Steps**
After completing this setup, we'll:
1. Add environment variables to Vercel
2. Test the connection
3. Test the complete system with all services
4. Deploy and verify production functionality

## 🔐 **Security Best Practices**
- Never commit API keys to version control
- Use environment variables for all sensitive data
- Rotate API keys regularly
- Monitor usage and set up alerts
