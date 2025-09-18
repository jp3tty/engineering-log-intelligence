#!/bin/bash

# Build Script for Vercel Deployment
# This script runs before Vercel builds the project

set -e  # Exit on any error

echo "🚀 Starting Vercel Build Process..."
echo "=================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 Setting up Python environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

echo ""
echo "🔍 Running Pre-deployment Checks..."
echo "----------------------------------"

# Run code quality checks
echo "1️⃣  Running code quality checks..."
black --check api/ || {
    echo "❌ Code formatting issues found. Please run 'black api/' to fix them."
    exit 1
}

flake8 api/ || {
    echo "❌ Linting issues found. Please fix them."
    exit 1
}

mypy api/ || {
    echo "❌ Type checking issues found. Please fix them."
    exit 1
}

echo "✅ All pre-deployment checks passed!"

echo ""
echo "📋 Build Summary:"
echo "-----------------"
echo "✅ Code formatting: OK"
echo "✅ Linting: OK" 
echo "✅ Type checking: OK"
echo "✅ Dependencies: Installed"

echo ""
echo "🎉 Build process completed successfully!"
echo "======================================"
