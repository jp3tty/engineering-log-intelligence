#!/bin/bash
# ML Batch Analysis Runner
# ========================
# This script runs ML batch analysis to populate the ml_predictions table
# with real predictions from your trained models.
#
# Usage:
#   ./run_ml_analysis.sh
#
# Prerequisites:
#   1. Trained models in models/ directory
#   2. DATABASE_URL environment variable set
#   3. Python dependencies installed

set -e  # Exit on error

echo "=================================================================="
echo "🤖 ML BATCH ANALYSIS RUNNER"
echo "=================================================================="
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if we're in the right directory
if [ ! -f "scripts/ml_batch_analysis.py" ]; then
    echo "❌ Error: scripts/ml_batch_analysis.py not found"
    echo "   Make sure you're running this from the engineering_log_intelligence directory"
    exit 1
fi

# Check if models exist
if [ ! -d "models" ] || [ ! -f "models/log_classifier_simple.pkl" ]; then
    echo "❌ Error: Trained models not found in models/ directory"
    echo ""
    echo "You need to train your models first:"
    echo "  python train_models_simple.py"
    echo ""
    exit 1
fi

echo "✅ Found trained models in models/ directory"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set in environment"
    echo "   Checking for .env.local file..."
    
    if [ -f ".env.local" ]; then
        echo "✅ Found .env.local file"
        export $(cat .env.local | grep DATABASE_URL | xargs)
    else
        echo "❌ Error: DATABASE_URL not found"
        echo ""
        echo "Set it with:"
        echo "  export DATABASE_URL='your-postgres-connection-string'"
        echo ""
        echo "Or create .env.local file with:"
        echo "  DATABASE_URL=your-postgres-connection-string"
        echo ""
        exit 1
    fi
fi

echo "✅ DATABASE_URL configured"
echo ""

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import psycopg2; import sklearn; import numpy" 2>/dev/null || {
    echo "⚠️  Some dependencies missing. Installing..."
    pip install psycopg2-binary scikit-learn numpy python-dotenv
}

echo "✅ All dependencies ready"
echo ""

# Run the batch analysis
echo "=================================================================="
echo "🚀 RUNNING ML BATCH ANALYSIS"
echo "=================================================================="
echo ""

python3 scripts/ml_batch_analysis.py

echo ""
echo "=================================================================="
echo "✅ ML BATCH ANALYSIS COMPLETE!"
echo "=================================================================="
echo ""

# Check if results file was created
if [ -f "analysis_results.json" ]; then
    echo "📊 Analysis Results Summary:"
    echo ""
    python3 -c "
import json
with open('analysis_results.json') as f:
    results = json.load(f)
    print(f\"  Logs Analyzed:      {results['logs_analyzed']:,}\")
    print(f\"  Predictions Stored: {results['predictions_stored']:,}\")
    print(f\"  Anomalies Detected: {results['statistics']['anomalies_detected']:,}\")
    print(f\"  Anomaly Rate:       {results['statistics']['anomaly_rate']*100:.2f}%\")
    print(f\"  Timestamp:          {results['timestamp']}\")
    print()
    print('Severity Distribution:')
    for severity in results['statistics']['severity']:
        print(f\"    {severity['severity']:10} | {severity['count']:,} logs\")
"
    echo ""
    echo "📄 Full results saved to: analysis_results.json"
    echo ""
fi

echo "🎉 Your ML predictions are now available in the database!"
echo "   The Log Analysis tab will now show real predictions."
echo ""

