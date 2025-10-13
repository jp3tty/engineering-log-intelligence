# Kafka Streaming Setup Guide

**Date:** October 13, 2025  
**Goal:** Enable real-time log streaming through Kafka

---

## Overview

This guide walks through enabling Kafka streaming for your log intelligence system. Once complete, logs will flow in real-time through Kafka instead of batch processing.

---

## Architecture

### Current Flow (Batch)
```
populate_database.py → PostgreSQL → Dashboard
```

### New Flow (Streaming)
```
Log Generator → Kafka Topic (log-ingestion) → Consumer → PostgreSQL + Elasticsearch → Dashboard
```

---

## Prerequisites

✅ You already have:
- Confluent Cloud account with credentials
- Environment variables set (`KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_API_KEY`, `KAFKA_API_SECRET`)
- Topic schemas defined in `external-services/kafka/topics.json`

---

## Step 1: Create Kafka Topics in Confluent Cloud

### Option A: Via Confluent Cloud Console (Easiest)

1. **Login to Confluent Cloud**
   - Go to https://confluent.cloud
   - Navigate to your cluster

2. **Create Topics**
   
   Create these topics with the following settings:
   
   **Topic: `log-ingestion`**
   - Partitions: 3 (start small, scale later)
   - Retention: 7 days
   - Cleanup policy: delete
   
   **Topic: `log-processing`** (optional for now)
   - Partitions: 3
   - Retention: 30 days
   
   **Topic: `alerts`** (optional)
   - Partitions: 1
   - Retention: 30 days

### Option B: Via CLI (Advanced)

```bash
# Install Confluent CLI
brew install confluentinc/tap/cli

# Configure
confluent login
confluent environment use <your-env-id>
confluent kafka cluster use <your-cluster-id>

# Create topics
confluent kafka topic create log-ingestion --partitions 3
confluent kafka topic create log-processing --partitions 3
confluent kafka topic create alerts --partitions 1
```

---

## Step 2: Install Kafka Python Client

The streaming scripts need the `confluent-kafka` library:

```bash
# In your project directory
cd engineering_log_intelligence

# Install confluent-kafka
pip install confluent-kafka

# Add to requirements.txt
echo "confluent-kafka>=2.3.0" >> requirements.txt
```

---

## Step 3: Create Kafka Producer (Log Publisher)

I'll create a script that publishes logs to Kafka:

**File: `scripts/kafka_log_producer.py`**

This script will:
- Generate logs (SPLUNK, SAP, Application)
- Publish them to the `log-ingestion` Kafka topic
- Run continuously (real-time streaming)

---

## Step 4: Create Kafka Consumer (Log Processor)

**File: `scripts/kafka_log_consumer.py`**

This script will:
- Subscribe to the `log-ingestion` topic
- Consume logs as they arrive
- Save to PostgreSQL
- Optionally index in Elasticsearch

---

## Step 5: Update Health Check

The health check will detect streaming by:
- Checking if consumer group is active
- Measuring lag (difference between produced and consumed)
- Marking as "healthy" if actively streaming

---

## Step 6: Run Streaming

### Start Consumer (Processor)
```bash
# Terminal 1 - Start the consumer
python scripts/kafka_log_consumer.py
```

### Start Producer (Generator)
```bash
# Terminal 2 - Start the producer
python scripts/kafka_log_producer.py
```

The dashboard will now show:
- ✅ Kafka Streaming: **healthy** (actively streaming)
- Logs appearing in real-time

---

## Testing

### Verify Topics Exist
```bash
# List topics
confluent kafka topic list
```

### Monitor Messages
```bash
# Consume from topic (test)
confluent kafka topic consume log-ingestion --from-beginning
```

### Check Consumer Groups
```bash
# List consumer groups
confluent kafka consumer group list

# Describe group
confluent kafka consumer group describe log-processor-group
```

---

## Deployment Options

### Option 1: Local Development
- Run producer and consumer locally
- Great for testing
- Not 24/7

### Option 2: GitHub Actions (Scheduled)
- Run producer on schedule
- Run consumer continuously
- Free tier limits apply

### Option 3: Dedicated Server
- Deploy to a VPS (DigitalOcean, AWS EC2)
- Run as background services
- True real-time streaming

### Option 4: Serverless (Advanced)
- Use AWS Lambda or Google Cloud Functions
- Triggered by Kafka events
- Auto-scaling

---

## Cost Considerations

### Confluent Cloud Free Tier
- **Throughput:** Up to 1 MB/s
- **Storage:** Up to 5 GB
- **Suitable for:** Development and testing

### Estimated Usage
- **1 log entry:** ~500 bytes
- **1000 logs/day:** ~0.5 MB/day
- **Well within free tier** ✅

---

## Monitoring

Once streaming is active:

1. **Dashboard TreeMap**
   - Kafka Streaming: healthy ✅
   
2. **Confluent Cloud Metrics**
   - Messages produced
   - Messages consumed
   - Consumer lag
   
3. **Application Logs**
   - Producer: "Published X messages"
   - Consumer: "Processed X messages"

---

## Troubleshooting

### "Connection refused" Error
- Check `KAFKA_BOOTSTRAP_SERVERS` is correct
- Verify API key and secret are set
- Ensure Confluent Cloud cluster is running

### "Topic does not exist" Error
- Create the topic in Confluent Cloud
- Verify topic name matches configuration

### "Authentication failed" Error
- Check `KAFKA_API_KEY` and `KAFKA_API_SECRET`
- Verify credentials in Confluent Cloud

### Consumer Not Receiving Messages
- Check producer is running and publishing
- Verify consumer is subscribed to correct topic
- Check consumer group is active

---

## Next Steps

After basic streaming works:

1. **Add ML Processing**
   - Run ML models on streaming data
   - Publish predictions to `ml-predictions` topic

2. **Alert Generation**
   - Detect anomalies in real-time
   - Publish to `alerts` topic
   - Send notifications

3. **Analytics Pipeline**
   - Stream metrics to `analytics` topic
   - Real-time aggregations
   - Live dashboard updates

4. **Multiple Producers**
   - Different log sources
   - Each publishing to Kafka
   - Unified processing

---

## Benefits of Streaming

### Before (Batch)
- ❌ Logs once per day
- ❌ Delayed insights
- ❌ Limited scalability
- ❌ No real-time alerts

### After (Streaming)
- ✅ Real-time log ingestion
- ✅ Immediate insights
- ✅ Highly scalable
- ✅ Instant alerts
- ✅ Event-driven architecture

---

## Ready to Implement?

I can create the producer and consumer scripts right now. Would you like me to:

1. **Create the Kafka producer script** (`kafka_log_producer.py`)
2. **Create the Kafka consumer script** (`kafka_log_consumer.py`)
3. **Update the health check** to detect active streaming
4. **Add installation and startup scripts**

Just say the word and I'll build it! 🚀

