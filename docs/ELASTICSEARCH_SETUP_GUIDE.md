# Elasticsearch Setup Guide - AWS Free Tier

## 🎯 **Goal**
Set up Elasticsearch using AWS free tier for log search and analysis.

## 📋 **Prerequisites**
- AWS Account (free tier eligible)
- Basic understanding of AWS services

## 🚀 **Step-by-Step Setup**

### **Step 1: Create AWS Account**
1. Go to [AWS Console](https://aws.amazon.com/)
2. Click "Create an AWS Account"
3. Follow the signup process
4. **Important**: Use a credit card for verification (won't be charged for free tier)

### **Step 2: Access Elasticsearch Service**
1. Log into AWS Console
2. Search for "Elasticsearch" in the services search
3. Click on "Amazon Elasticsearch Service" (now called "Amazon OpenSearch Service")

### **Step 3: Create Domain**
1. Click "Create domain"
2. Choose "Development and testing" (free tier)
3. **Domain name**: `engineering-log-intelligence`
4. **Version**: Choose latest available (e.g., OpenSearch 2.11)
5. **Instance type**: `t3.small.search` (free tier eligible)
6. **Instance count**: 1
7. **Storage**: 10 GB (free tier limit)

### **Step 4: Configure Access**
1. **Access policy**: Choose "Allow open access to the domain"
2. **Fine-grained access control**: Disable (for simplicity)
3. **Encryption**: Enable at rest (recommended)

### **Step 5: Review and Create**
1. Review all settings
2. Click "Create"
3. Wait 10-15 minutes for domain to be ready

### **Step 6: Get Connection Details**
1. Once domain is active, click on it
2. Note the **Domain endpoint** (e.g., `search-engineering-log-intelligence-xxxxx.us-east-1.es.amazonaws.com`)
3. **Port**: 443 (HTTPS)
4. **Region**: Note your AWS region

## 🔧 **Environment Variables to Add**

Once you have the connection details, we'll add these to Vercel:

```bash
# Elasticsearch Configuration
ELASTICSEARCH_URL=https://search-engineering-log-intelligence-xxxxx.us-east-1.es.amazonaws.com
ELASTICSEARCH_PORT=443
ELASTICSEARCH_INDEX=engineering_logs
ELASTICSEARCH_USERNAME= (leave empty for open access)
ELASTICSEARCH_PASSWORD= (leave empty for open access)
```

## 🧪 **Testing Connection**

After setup, we'll test the connection with a simple Python script.

## 💰 **Cost Information**
- **Free Tier**: 750 hours/month for 12 months
- **Storage**: 10 GB free
- **Data Transfer**: 1 GB/month free
- **Estimated Cost**: $0/month (within free tier limits)

## ⚠️ **Important Notes**
- Free tier is valid for 12 months from account creation
- Monitor usage in AWS Billing Dashboard
- Set up billing alerts to avoid unexpected charges
- Domain takes 10-15 minutes to create

## 🆘 **Troubleshooting**
- If domain creation fails, check your AWS region
- Ensure you're using free tier eligible instance types
- Check AWS service limits in your account

## 📞 **Next Steps**
After completing this setup, we'll:
1. Add environment variables to Vercel
2. Test the connection
3. Set up Kafka (Confluent Cloud free tier)
4. Test the complete system
