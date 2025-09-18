#!/bin/bash

# GitHub Secrets Setup Script
# This script helps you set up the necessary secrets for GitHub Actions

echo "🔐 GitHub Secrets Setup for CI/CD Pipeline"
echo "=========================================="

echo ""
echo "To enable the CI/CD pipeline, you need to set up the following secrets in your GitHub repository:"
echo ""

echo "1️⃣  VERCEL_TOKEN"
echo "   - Go to https://vercel.com/account/tokens"
echo "   - Create a new token with appropriate permissions"
echo "   - Add it as a repository secret named 'VERCEL_TOKEN'"
echo ""

echo "2️⃣  Optional: External Service Credentials"
echo "   - DATABASE_URL (PostgreSQL connection string)"
echo "   - ELASTICSEARCH_URL (Elasticsearch endpoint)"
echo "   - KAFKA_BROKERS (Kafka broker URLs)"
echo "   - REDIS_URL (Redis connection string)"
echo ""

echo "📋 Steps to add secrets:"
echo "1. Go to your GitHub repository"
echo "2. Click on 'Settings' tab"
echo "3. Click on 'Secrets and variables' → 'Actions'"
echo "4. Click 'New repository secret'"
echo "5. Add each secret with the name and value"
echo ""

echo "🔗 Useful Links:"
echo "- GitHub Secrets: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "- Vercel Tokens: https://vercel.com/account/tokens"
echo ""

echo "✅ After setting up secrets, your CI/CD pipeline will automatically:"
echo "   - Run tests on every push and pull request"
echo "   - Deploy to development when pushing to 'develop' branch"
echo "   - Deploy to production when pushing to 'main' branch"
echo "   - Run code quality checks and security scans"
