#!/bin/bash
# Fix Vercel DATABASE_URL Environment Variable
# This script updates the DATABASE_URL on Vercel to fix the production database connection

cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

echo "🔧 Fixing Vercel DATABASE_URL..."
echo ""

# New Railway Hobby Plan connection string
DATABASE_URL="postgresql://postgres:aeEtrFlmEjQZfcoFMQnjnCGcHWZGgpOq@switchyard.proxy.rlwy.net:51941/railway"

echo "Step 1: Removing old DATABASE_URL (if exists)..."
vercel env rm DATABASE_URL production 2>/dev/null || true
vercel env rm DATABASE_URL preview 2>/dev/null || true
vercel env rm DATABASE_URL development 2>/dev/null || true

echo ""
echo "Step 2: Adding new DATABASE_URL for all environments..."
echo ""
echo "💡 When prompted, paste this value:"
echo "$DATABASE_URL"
echo ""

# Add for production
echo "Setting for PRODUCTION..."
echo "$DATABASE_URL" | vercel env add DATABASE_URL production

# Add for preview
echo "Setting for PREVIEW..."
echo "$DATABASE_URL" | vercel env add DATABASE_URL preview

# Add for development
echo "Setting for DEVELOPMENT..."
echo "$DATABASE_URL" | vercel env add DATABASE_URL development

echo ""
echo "Step 3: Redeploying to production..."
vercel --prod --force

echo ""
echo "✅ Done! Your production API should now connect to the database."
echo ""
echo "🧪 Test it:"
echo "curl https://engineeringlogintelligence.vercel.app/api/metrics"

