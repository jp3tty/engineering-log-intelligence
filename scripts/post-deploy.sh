#!/bin/bash

# Post-Deployment Script for Vercel
# This script runs after Vercel successfully deploys the project

set -e  # Exit on any error

echo "🎉 Post-Deployment Process Starting..."
echo "====================================="

# Get deployment information
DEPLOYMENT_URL=${VERCEL_URL:-"https://engineering-log-intelligence.vercel.app"}
DEPLOYMENT_ENV=${VERCEL_ENV:-"development"}

echo "📊 Deployment Information:"
echo "-------------------------"
echo "Environment: $DEPLOYMENT_ENV"
echo "URL: $DEPLOYMENT_URL"

echo ""
echo "🏥 Running Health Checks..."
echo "---------------------------"

# Test health endpoint
HEALTH_URL="$DEPLOYMENT_URL/api/health/check"
echo "Testing health endpoint: $HEALTH_URL"

# Wait a moment for deployment to be fully ready
sleep 10

# Test health check with retry logic
for i in {1..3}; do
    if curl -f -s "$HEALTH_URL" > /dev/null; then
        echo "✅ Health check passed!"
        break
    else
        echo "⏳ Health check attempt $i failed, retrying in 5 seconds..."
        sleep 5
    fi
    
    if [ $i -eq 3 ]; then
        echo "❌ Health check failed after 3 attempts"
        exit 1
    fi
done

echo ""
echo "📈 Deployment Summary:"
echo "---------------------"
echo "✅ Deployment: Successful"
echo "✅ Health Check: Passed"
echo "✅ Environment: $DEPLOYMENT_ENV"
echo "✅ URL: $DEPLOYMENT_URL"

# In a real project, you might want to:
# - Send notifications to Slack/Discord
# - Update monitoring dashboards
# - Run integration tests
# - Update documentation

echo ""
echo "🎉 Post-deployment process completed successfully!"
echo "==============================================="
