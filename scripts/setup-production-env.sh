#!/bin/bash

# Production Environment Setup Script
# Phase 3, Day 13: Production Infrastructure Setup

set -e  # Exit on any error

echo "🚀 Setting up Production Environment Variables for Vercel"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI is not installed. Please install it first:"
    echo "npm install -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    print_error "Not logged in to Vercel. Please login first:"
    echo "vercel login"
    exit 1
fi

print_status "Vercel CLI is installed and user is logged in"

# Check if project is linked
if [ ! -f ".vercel/project.json" ]; then
    print_warning "Project not linked to Vercel. Linking now..."
    vercel link
fi

print_status "Project is linked to Vercel"

# Function to add environment variable
add_env_var() {
    local var_name=$1
    local var_description=$2
    local is_sensitive=$3
    
    print_status "Setting up $var_name: $var_description"
    
    if [ "$is_sensitive" = "true" ]; then
        echo -n "Enter $var_name (hidden): "
        read -s var_value
        echo
    else
        echo -n "Enter $var_name: "
        read var_value
    fi
    
    if [ -n "$var_value" ]; then
        vercel env add "$var_name" production <<< "$var_value"
        print_success "$var_name set successfully"
    else
        print_warning "$var_name skipped (empty value)"
    fi
}

# Function to generate secure JWT secret
generate_jwt_secret() {
    python3 -c "
import secrets
import base64
secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
print(secret)
"
}

echo
echo "🔐 Setting up Authentication & Security"
echo "======================================"

# Generate and set JWT secret
print_status "Generating secure JWT secret key..."
jwt_secret=$(generate_jwt_secret)
vercel env add JWT_SECRET_KEY production <<< "$jwt_secret"
print_success "JWT_SECRET_KEY generated and set"

# Set other auth variables
add_env_var "JWT_ALGORITHM" "JWT algorithm (default: HS256)" false
add_env_var "JWT_ACCESS_TOKEN_EXPIRE_MINUTES" "Token expiration in minutes (default: 30)" false

echo
echo "🗄️ Setting up Database Configuration"
echo "===================================="

add_env_var "DATABASE_URL" "PostgreSQL connection string" true
add_env_var "POSTGRES_HOST" "PostgreSQL host" false
add_env_var "POSTGRES_PORT" "PostgreSQL port (default: 5432)" false
add_env_var "POSTGRES_DB" "PostgreSQL database name" false
add_env_var "POSTGRES_USER" "PostgreSQL username" false
add_env_var "POSTGRES_PASSWORD" "PostgreSQL password" true

echo
echo "🔍 Setting up Elasticsearch Configuration"
echo "========================================"

add_env_var "ELASTICSEARCH_URL" "Elasticsearch cluster URL" false
add_env_var "ELASTICSEARCH_USERNAME" "Elasticsearch username" false
add_env_var "ELASTICSEARCH_PASSWORD" "Elasticsearch password" true
add_env_var "ELASTICSEARCH_INDEX" "Elasticsearch index name (default: logs_prod)" false

echo
echo "📡 Setting up Kafka Configuration"
echo "================================"

add_env_var "KAFKA_BOOTSTRAP_SERVERS" "Kafka bootstrap servers" false
add_env_var "KAFKA_TOPIC_LOGS" "Kafka logs topic (default: log-ingestion-prod)" false
add_env_var "KAFKA_TOPIC_ALERTS" "Kafka alerts topic (default: alerts-prod)" false
add_env_var "KAFKA_GROUP_ID" "Kafka consumer group ID (default: log-processor-prod)" false

echo
echo "☁️ Setting up AWS Configuration"
echo "=============================="

add_env_var "AWS_ACCESS_KEY_ID" "AWS Access Key ID" true
add_env_var "AWS_SECRET_ACCESS_KEY" "AWS Secret Access Key" true
add_env_var "AWS_S3_BUCKET" "AWS S3 bucket name" false
add_env_var "AWS_REGION" "AWS region (default: us-west-2)" false

echo
echo "🤖 Setting up ML Services Configuration"
echo "======================================"

add_env_var "ML_MODEL_BUCKET" "ML models S3 bucket" false
add_env_var "ML_ENDPOINT_URL" "ML inference endpoint URL" false

echo
echo "⚙️ Setting up Application Configuration"
echo "======================================"

add_env_var "APP_NAME" "Application name (default: Engineering Log Intelligence)" false
add_env_var "APP_VERSION" "Application version (default: 1.2.0)" false
add_env_var "DEBUG" "Debug mode (default: false)" false
add_env_var "LOG_LEVEL" "Log level (default: INFO)" false
add_env_var "ENVIRONMENT" "Environment (default: production)" false

echo
echo "🌐 Setting up CORS Configuration"
echo "==============================="

add_env_var "CORS_ORIGINS" "CORS allowed origins (comma-separated)" false

echo
echo "📊 Setting up Monitoring Configuration"
echo "===================================="

add_env_var "MONITORING_ENABLED" "Enable monitoring (default: true)" false
add_env_var "ALERT_WEBHOOK_URL" "Alert webhook URL (optional)" false

echo
echo "🔍 Verifying Environment Variables"
echo "================================="

print_status "Listing all production environment variables..."
vercel env ls

echo
echo "📋 Next Steps"
echo "============"
print_status "1. Verify all environment variables are set correctly"
print_status "2. Deploy to production: vercel --prod"
print_status "3. Test the deployment: curl https://your-app.vercel.app/api/health/check"
print_status "4. Set up production databases (PostgreSQL, Elasticsearch, Kafka)"
print_status "5. Run database migrations in production"

echo
print_success "Production environment setup complete! 🎉"
echo
print_warning "Remember to:"
echo "- Keep your credentials secure"
echo "- Never commit them to Git"
echo "- Regularly rotate secrets"
echo "- Monitor for security issues"
