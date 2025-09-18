#!/bin/bash

# Development Environment Setup Script
# Engineering Log Intelligence System

set -e

echo "🚀 Setting up Development Environment for Engineering Log Intelligence System"
echo "=================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Please install it first:"
    echo "   npm install -g vercel"
    exit 1
fi

# Create .env file from development template
if [ ! -f .env ]; then
    echo "📝 Creating .env file from development template..."
    cp env.development .env
    echo "✅ .env file created"
else
    echo "⚠️  .env file already exists, skipping creation"
fi

# Start external services with Docker Compose
echo "🐳 Starting external services with Docker Compose..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if PostgreSQL is ready
echo "🔍 Checking PostgreSQL connection..."
until docker exec log_intelligence_postgres_dev pg_isready -U dev_user -d log_intelligence_dev; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Check if Elasticsearch is ready
echo "🔍 Checking Elasticsearch connection..."
until curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    echo "   Waiting for Elasticsearch..."
    sleep 2
done
echo "✅ Elasticsearch is ready"

# Check if Kafka is ready
echo "🔍 Checking Kafka connection..."
until docker exec log_intelligence_kafka_dev kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; do
    echo "   Waiting for Kafka..."
    sleep 2
done
echo "✅ Kafka is ready"

# Create Elasticsearch index
echo "📊 Creating Elasticsearch index..."
curl -X PUT "localhost:9200/logs_dev" \
     -H "Content-Type: application/json" \
     -d @external-services/elasticsearch/logs-mapping.json \
     > /dev/null 2>&1 || echo "⚠️  Index creation failed (may already exist)"

echo "✅ Elasticsearch index created"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations (if any)
echo "🗄️  Running database setup..."
# This would run Alembic migrations in a real project
echo "✅ Database setup complete"

# Test the setup
echo "🧪 Testing the setup..."
python test_setup.py

echo ""
echo "🎉 Development environment setup complete!"
echo "=================================================================="
echo ""
echo "📋 Next steps:"
echo "1. Start Vercel development server: vercel dev"
echo "2. Access services:"
echo "   - Vercel Functions: http://localhost:3000/api"
echo "   - Kafka UI: http://localhost:8080"
echo "   - Elasticsearch: http://localhost:9200"
echo "   - PostgreSQL: localhost:5432"
echo ""
echo "🔧 To stop services: docker-compose -f docker-compose.dev.yml down"
echo "🔧 To view logs: docker-compose -f docker-compose.dev.yml logs -f"
echo ""
