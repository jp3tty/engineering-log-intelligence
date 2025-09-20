#!/bin/bash

# Simple Production Environment Setup
# Phase 3, Day 13: Production Infrastructure Setup

echo "🚀 Engineering Log Intelligence - Production Setup"
echo "================================================="
echo
echo "This script will help you set up production environment variables in Vercel."
echo "You'll need your production database, Elasticsearch, and Kafka credentials."
echo

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed."
    echo "Please install it first: npm install -g vercel"
    exit 1
fi

# Check if logged in
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel."
    echo "Please login first: vercel login"
    exit 1
fi

echo "✅ Vercel CLI is ready"
echo

# Link project if needed
if [ ! -f ".vercel/project.json" ]; then
    echo "🔗 Linking project to Vercel..."
    vercel link
fi

echo "✅ Project is linked to Vercel"
echo

# Function to set environment variable
set_env() {
    local name=$1
    local description=$2
    local default=$3
    local sensitive=$4
    
    echo "Setting: $name"
    echo "Description: $description"
    if [ -n "$default" ]; then
        echo "Default: $default"
    fi
    
    if [ "$sensitive" = "true" ]; then
        echo -n "Enter value (hidden): "
        read -s value
        echo
    else
        echo -n "Enter value: "
        read value
    fi
    
    # Use default if empty
    if [ -z "$value" ] && [ -n "$default" ]; then
        value="$default"
    fi
    
    if [ -n "$value" ]; then
        echo "$value" | vercel env add "$name" production
        echo "✅ $name set"
    else
        echo "⏭️  $name skipped"
    fi
    echo
}

echo "🔐 Step 1: Authentication & Security"
echo "===================================="

# Generate JWT secret
echo "Generating secure JWT secret..."
jwt_secret=$(python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8'))")
echo "$jwt_secret" | vercel env add JWT_SECRET_KEY production
echo "✅ JWT_SECRET_KEY generated and set"
echo

set_env "JWT_ALGORITHM" "JWT algorithm" "HS256" false
set_env "JWT_ACCESS_TOKEN_EXPIRE_MINUTES" "Token expiration in minutes" "30" false

echo "🗄️ Step 2: Database Configuration"
echo "================================="

echo "You'll need your PostgreSQL production database credentials."
echo "Examples: Railway, Supabase, Neon, or AWS RDS"
echo

set_env "DATABASE_URL" "PostgreSQL connection string (postgresql://user:pass@host:port/db)" "" true
set_env "POSTGRES_HOST" "PostgreSQL host" "" false
set_env "POSTGRES_PORT" "PostgreSQL port" "5432" false
set_env "POSTGRES_DB" "PostgreSQL database name" "log_intelligence_prod" false
set_env "POSTGRES_USER" "PostgreSQL username" "" false
set_env "POSTGRES_PASSWORD" "PostgreSQL password" "" true

echo "🔍 Step 3: Elasticsearch Configuration"
echo "====================================="

echo "You'll need your Elasticsearch production cluster credentials."
echo "Examples: AWS Elasticsearch, Elastic Cloud, or self-hosted"
echo

set_env "ELASTICSEARCH_URL" "Elasticsearch cluster URL" "" false
set_env "ELASTICSEARCH_USERNAME" "Elasticsearch username" "" false
set_env "ELASTICSEARCH_PASSWORD" "Elasticsearch password" "" true
set_env "ELASTICSEARCH_INDEX" "Elasticsearch index name" "logs_prod" false

echo "📡 Step 4: Kafka Configuration"
echo "============================="

echo "You'll need your Kafka production cluster credentials."
echo "Examples: Confluent Cloud, AWS MSK, or self-hosted"
echo

set_env "KAFKA_BOOTSTRAP_SERVERS" "Kafka bootstrap servers" "" false
set_env "KAFKA_TOPIC_LOGS" "Kafka logs topic" "log-ingestion-prod" false
set_env "KAFKA_TOPIC_ALERTS" "Kafka alerts topic" "alerts-prod" false
set_env "KAFKA_GROUP_ID" "Kafka consumer group ID" "log-processor-prod" false

echo "☁️ Step 5: AWS Configuration (Optional)"
echo "====================================="

echo "AWS is used for S3 storage and ML services."
echo "You can skip this if you don't have AWS credentials yet."
echo

set_env "AWS_ACCESS_KEY_ID" "AWS Access Key ID" "" true
set_env "AWS_SECRET_ACCESS_KEY" "AWS Secret Access Key" "" true
set_env "AWS_S3_BUCKET" "AWS S3 bucket name" "" false
set_env "AWS_REGION" "AWS region" "us-west-2" false

echo "🤖 Step 6: ML Services (Optional)"
echo "==============================="

echo "ML services are used for machine learning inference."
echo "You can skip this for now and add later."
echo

set_env "ML_MODEL_BUCKET" "ML models S3 bucket" "" false
set_env "ML_ENDPOINT_URL" "ML inference endpoint URL" "" false

echo "⚙️ Step 7: Application Settings"
echo "============================="

set_env "APP_NAME" "Application name" "Engineering Log Intelligence" false
set_env "APP_VERSION" "Application version" "1.2.0" false
set_env "DEBUG" "Debug mode" "false" false
set_env "LOG_LEVEL" "Log level" "INFO" false
set_env "ENVIRONMENT" "Environment" "production" false

echo "🌐 Step 8: CORS Configuration"
echo "============================"

set_env "CORS_ORIGINS" "CORS allowed origins (comma-separated)" "https://engineering-log-intelligence.vercel.app" false

echo "📊 Step 9: Monitoring (Optional)"
echo "==============================="

set_env "MONITORING_ENABLED" "Enable monitoring" "true" false
set_env "ALERT_WEBHOOK_URL" "Alert webhook URL" "" false

echo "🔍 Verifying Setup"
echo "================="

echo "Listing all production environment variables..."
vercel env ls

echo
echo "🎉 Production Environment Setup Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Deploy to production: vercel --prod"
echo "2. Test deployment: curl https://your-app.vercel.app/api/health/check"
echo "3. Set up your production databases"
echo "4. Run database migrations"
echo
echo "Important reminders:"
echo "- Keep your credentials secure"
echo "- Never commit them to Git"
echo "- Test everything before going live"
echo
