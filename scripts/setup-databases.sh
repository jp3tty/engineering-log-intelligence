#!/bin/bash

# Database Environment Variables Setup Script
# Day 14: Security & Compliance - Database Setup

set -e  # Exit on any error

echo "🗄️ Engineering Log Intelligence - Database Setup"
echo "================================================"
echo
echo "This script will help you add database environment variables to Vercel."
echo "You'll need your PostgreSQL, Elasticsearch, and Kafka credentials."
echo

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

# Check if logged in
if ! vercel whoami &> /dev/null; then
    print_error "Not logged in to Vercel. Please login first:"
    echo "vercel login"
    exit 1
fi

echo "✅ Vercel CLI is ready"
echo

# Function to add environment variable
add_env() {
    local name=$1
    local description=$2
    local sensitive=$3
    
    echo "Setting: $name"
    echo "Description: $description"
    
    if [ "$sensitive" = "true" ]; then
        echo -n "Enter value (hidden): "
        read -s value
        echo
    else
        echo -n "Enter value: "
        read value
    fi
    
    if [ -n "$value" ]; then
        echo "$value" | vercel env add "$name" production
        print_success "$name set successfully"
    else
        print_warning "$name skipped (empty value)"
    fi
    echo
}

echo "🗄️ Step 1: PostgreSQL Configuration"
echo "==================================="

echo "You'll need your PostgreSQL production database credentials."
echo "Examples: Railway, Supabase, Neon, or AWS RDS"
echo

add_env "DATABASE_URL" "PostgreSQL connection string (postgresql://user:pass@host:port/db)" true
add_env "POSTGRES_HOST" "PostgreSQL host" false
add_env "POSTGRES_USER" "PostgreSQL username" false
add_env "POSTGRES_PASSWORD" "PostgreSQL password" true

echo "🔍 Step 2: Elasticsearch Configuration"
echo "====================================="

echo "You'll need your Elasticsearch production cluster credentials."
echo "Examples: AWS Elasticsearch, Elastic Cloud, or self-hosted"
echo

add_env "ELASTICSEARCH_URL" "Elasticsearch cluster URL" false
add_env "ELASTICSEARCH_USERNAME" "Elasticsearch username" false
add_env "ELASTICSEARCH_PASSWORD" "Elasticsearch password" true

echo "📡 Step 3: Kafka Configuration"
echo "============================="

echo "You'll need your Kafka production cluster credentials."
echo "Examples: Confluent Cloud, AWS MSK, or self-hosted"
echo

add_env "KAFKA_BOOTSTRAP_SERVERS" "Kafka bootstrap servers" false

echo "🔍 Verifying Setup"
echo "================="

print_status "Listing all production environment variables..."
vercel env ls

echo
echo "🎉 Database Environment Setup Complete!"
echo "======================================"
echo
echo "Next steps:"
echo "1. Test database connections"
echo "2. Run database migrations"
echo "3. Test API endpoints with real databases"
echo "4. Move to Day 15: Performance & Scalability"
echo
echo "Important reminders:"
echo "- Keep your database credentials secure"
echo "- Test all connections before going live"
echo "- Monitor database usage and costs"
echo
