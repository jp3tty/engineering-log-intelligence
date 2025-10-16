#!/bin/bash
# Fresh Database Setup Script
# Run this after creating new Railway database

set -e  # Exit on any error

echo "=========================================="
echo "🚀 Fresh Railway Database Setup"
echo "=========================================="
echo ""

# Check if DATABASE_URL is provided
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set"
    echo ""
    echo "Please provide your new Railway DATABASE_URL:"
    echo ""
    echo "Option 1: Set as environment variable"
    echo "  export DATABASE_URL='postgresql://postgres:PASSWORD@HOST:PORT/railway'"
    echo "  ./setup_fresh_database.sh"
    echo ""
    echo "Option 2: Pass as argument"
    echo "  ./setup_fresh_database.sh 'postgresql://postgres:PASSWORD@HOST:PORT/railway'"
    echo ""
    exit 1
fi

# If URL provided as argument, use it
if [ ! -z "$1" ]; then
    export DATABASE_URL="$1"
fi

echo "📋 Configuration:"
echo "  DATABASE_URL: ${DATABASE_URL:0:40}..." 
echo ""

# Test connection
echo "🔍 Step 1: Testing database connection..."
python3 -c "import psycopg2; import os; conn = psycopg2.connect(os.environ['DATABASE_URL']); conn.close(); print('✅ Connection successful!')" || {
    echo "❌ Connection failed! Check your DATABASE_URL"
    exit 1
}
echo ""

# Setup schema
echo "🏗️  Step 2: Setting up database schema..."
if python3 setup_schema_fixed.py; then
    echo "✅ Schema setup complete!"
else
    echo "⚠️  Schema setup had warnings (might be okay if tables already exist)"
fi
echo ""

# Populate data
echo "📊 Step 3: Populating with sample data..."
echo "  Generating 10,000 log entries..."
if python3 populate_database.py 10000; then
    echo "✅ Data population complete!"
else
    echo "❌ Data population failed"
    exit 1
fi
echo ""

# Verify data
echo "🔍 Step 4: Verifying data..."
python3 -c "
import psycopg2
import os

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

# Count logs
cursor.execute('SELECT COUNT(*) FROM log_entries')
count = cursor.fetchone()[0]
print(f'✅ Total logs in database: {count:,}')

# Check database size
cursor.execute(\"SELECT pg_size_pretty(pg_database_size('railway')) as db_size\")
size = cursor.fetchone()[0]
print(f'✅ Database size: {size}')

# Check distribution
cursor.execute(\"\"\"
    SELECT level, COUNT(*) 
    FROM log_entries 
    GROUP BY level 
    ORDER BY COUNT(*) DESC
\"\"\")
print('\\n📊 Log distribution:')
for row in cursor.fetchall():
    print(f'   {row[0]}: {row[1]:,}')

cursor.close()
conn.close()
"
echo ""

# Update .env.local
echo "💾 Step 5: Updating .env.local..."
echo "DATABASE_URL=$DATABASE_URL" > .env.local
echo "✅ Saved to .env.local"
echo ""

echo "=========================================="
echo "✅ Database Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Update Vercel environment variable:"
echo "   vercel env rm DATABASE_URL production"
echo "   vercel env add DATABASE_URL production"
echo "   (paste your DATABASE_URL when prompted)"
echo ""
echo "2. Redeploy to Vercel:"
echo "   vercel --prod --force"
echo ""
echo "3. Test your deployment:"
echo "   curl -s 'https://engineeringlogintelligence.vercel.app/api/metrics'"
echo ""
echo "4. Open in browser:"
echo "   https://engineeringlogintelligence.vercel.app"
echo ""

