#!/bin/bash

# Elasticsearch and Kafka Setup Script
# This script helps you add environment variables to Vercel

echo "🔍 Elasticsearch and Kafka Setup Script"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: Please run this script from the engineering_log_intelligence directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: /path/to/engineering_log_intelligence"
    exit 1
fi

echo "✅ Found vercel.json - we're in the right directory"
echo ""

# Function to add environment variable
add_env_var() {
    local var_name=$1
    local var_description=$2
    local current_value=$3
    
    echo "🔧 Adding $var_name to Vercel..."
    echo "   Description: $var_description"
    
    if [ -n "$current_value" ]; then
        echo "$current_value" | vercel env add "$var_name" production
        if [ $? -eq 0 ]; then
            echo "   ✅ $var_name added successfully"
        else
            echo "   ❌ Failed to add $var_name"
        fi
    else
        echo "   ⚠️  No value provided for $var_name - skipping"
    fi
    echo ""
}

# Elasticsearch setup
echo "🔍 ELASTICSEARCH SETUP"
echo "======================"
echo "Please provide your Elasticsearch connection details:"
echo ""

read -p "Elasticsearch URL (e.g., https://search-xxx.us-east-1.es.amazonaws.com): " ELASTICSEARCH_URL
read -p "Elasticsearch Port (usually 443): " ELASTICSEARCH_PORT
read -p "Elasticsearch Index (e.g., engineering_logs): " ELASTICSEARCH_INDEX
read -p "Elasticsearch Username (leave empty for open access): " ELASTICSEARCH_USERNAME
read -p "Elasticsearch Password (leave empty for open access): " ELASTICSEARCH_PASSWORD

echo ""
echo "Adding Elasticsearch environment variables..."

add_env_var "ELASTICSEARCH_URL" "Elasticsearch cluster URL" "$ELASTICSEARCH_URL"
add_env_var "ELASTICSEARCH_PORT" "Elasticsearch port" "$ELASTICSEARCH_PORT"
add_env_var "ELASTICSEARCH_INDEX" "Elasticsearch index name" "$ELASTICSEARCH_INDEX"
add_env_var "ELASTICSEARCH_USERNAME" "Elasticsearch username" "$ELASTICSEARCH_USERNAME"
add_env_var "ELASTICSEARCH_PASSWORD" "Elasticsearch password" "$ELASTICSEARCH_PASSWORD"

echo ""
echo "📡 KAFKA SETUP"
echo "=============="
echo "Please provide your Kafka connection details:"
echo ""

read -p "Kafka Bootstrap Servers (e.g., pkc-xxx.us-east-1.aws.confluent.cloud:9092): " KAFKA_BOOTSTRAP_SERVERS
read -p "Kafka API Key: " KAFKA_API_KEY
read -p "Kafka API Secret: " KAFKA_API_SECRET
read -p "Kafka Topic for Logs (e.g., engineering-logs): " KAFKA_TOPIC_LOGS
read -p "Kafka Topic for Alerts (e.g., engineering-alerts): " KAFKA_TOPIC_ALERTS
read -p "Kafka Group ID (e.g., engineering-log-intelligence-group): " KAFKA_GROUP_ID

echo ""
echo "Adding Kafka environment variables..."

add_env_var "KAFKA_BOOTSTRAP_SERVERS" "Kafka bootstrap servers" "$KAFKA_BOOTSTRAP_SERVERS"
add_env_var "KAFKA_API_KEY" "Kafka API key" "$KAFKA_API_KEY"
add_env_var "KAFKA_API_SECRET" "Kafka API secret" "$KAFKA_API_SECRET"
add_env_var "KAFKA_TOPIC_LOGS" "Kafka topic for logs" "$KAFKA_TOPIC_LOGS"
add_env_var "KAFKA_TOPIC_ALERTS" "Kafka topic for alerts" "$KAFKA_TOPIC_ALERTS"
add_env_var "KAFKA_GROUP_ID" "Kafka consumer group ID" "$KAFKA_GROUP_ID"

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Test the connections with: python3 test_connections.py"
echo "2. Deploy to production: vercel --prod"
echo "3. Verify all services are working"
echo ""
echo "To view all environment variables: vercel env ls"
echo "To test connections: python3 test_connections.py"
