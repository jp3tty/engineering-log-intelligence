#!/bin/bash

# Production Environment Setup Script
# Engineering Log Intelligence System

set -e

echo "🚀 Setting up Production Environment for Engineering Log Intelligence System"
echo "=================================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Please install it first:"
    echo "   npm install -g vercel"
    exit 1
fi

# Check if user is logged into Vercel
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged into Vercel. Please login first:"
    echo "   vercel login"
    exit 1
fi

echo "✅ Vercel CLI is ready"

# Create production environment file
echo "📝 Creating production environment configuration..."
cp env.production .env.production
echo "✅ Production environment file created"

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "🎉 Production environment setup complete!"
echo "=================================================================="
echo ""
echo "📋 Next steps:"
echo "1. Set up external services (PostgreSQL, Elasticsearch, Kafka)"
echo "2. Configure Vercel environment variables:"
echo "   - DATABASE_URL"
echo "   - ELASTICSEARCH_URL"
echo "   - KAFKA_BOOTSTRAP_SERVERS"
echo "   - JWT_SECRET_KEY"
echo "   - AWS credentials"
echo ""
echo "🔧 To set environment variables:"
echo "   vercel env add DATABASE_URL"
echo "   vercel env add ELASTICSEARCH_URL"
echo "   vercel env add KAFKA_BOOTSTRAP_SERVERS"
echo "   vercel env add JWT_SECRET_KEY"
echo ""
echo "🔧 To view production logs:"
echo "   vercel logs --prod"
echo ""
