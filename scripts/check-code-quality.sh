#!/bin/bash

# Code Quality Check Script for Engineering Log Intelligence System
# This script runs all code quality tools in sequence

set -e  # Exit on any error

echo "🔍 Running Code Quality Checks..."
echo "================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected. Activating venv..."
    source venv/bin/activate
fi

echo ""
echo "1️⃣  Running Black (Code Formatter)..."
echo "-------------------------------------"
black --check --diff api/ tests/ || {
    echo "❌ Black found formatting issues. Run 'black api/ tests/' to fix them."
    exit 1
}
echo "✅ Black: Code formatting is correct"

echo ""
echo "2️⃣  Running Flake8 (Linter)..."
echo "--------------------------------"
flake8 api/ tests/ || {
    echo "❌ Flake8 found linting issues. Please fix them."
    exit 1
}
echo "✅ Flake8: No linting issues found"

echo ""
echo "3️⃣  Running MyPy (Type Checker)..."
echo "-----------------------------------"
mypy api/ || {
    echo "❌ MyPy found type issues. Please fix them."
    exit 1
}
echo "✅ MyPy: No type issues found"

echo ""
echo "4️⃣  Running Tests..."
echo "--------------------"
pytest tests/ -v || {
    echo "❌ Tests failed. Please fix them."
    exit 1
}
echo "✅ All tests passed"

echo ""
echo "🎉 All code quality checks passed!"
echo "================================="
