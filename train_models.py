"""
ML Model Training Script
========================
This script trains machine learning models on your log data.

What it does (in simple terms):
1. Connects to your database (like opening a file)
2. Reads your logs (like reading a book)
3. Teaches AI models to recognize patterns (like teaching a student)
4. Saves the trained models (like saving your work)

Author: Engineering Log Intelligence Team
Date: October 11, 2025
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

# Load environment variables from .env.local file
# (This reads your database connection info)
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv('.env.local')

print("="*70)
print("🤖 ML MODEL TRAINING - Step-by-Step Learning Guide")
print("="*70)
print()

# =============================================================================
# STEP 1: Connect to Database
# =============================================================================
print("📊 STEP 1: Connecting to your database...")
print("-" * 70)

# Get database URL from environment variable
# (This is like getting the address of your database)
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    print("\nTo fix this, run:")
    print("  cd engineering_log_intelligence")
    print("  vercel env pull")
    sys.exit(1)

print(f"✅ Database URL found: {database_url[:30]}...")

# Connect to the database
# (Like opening a connection to your data storage)
try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("✅ Successfully connected to database!")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

print()

# =============================================================================
# STEP 2: Fetch Training Data
# =============================================================================
print("📚 STEP 2: Loading training data from log_entries table...")
print("-" * 70)
print()
print("💡 What we're doing:")
print("   - Fetching your 12,010 logs from the database")
print("   - Each log has information like:")
print("     • The message (what happened)")
print("     • The severity level (INFO, WARN, ERROR, etc.)")
print("     • Whether it's an anomaly (something unusual)")
print("     • And lots of other details")
print()

# SQL query to get training data
# (This is like asking the database: "Give me all the logs with these fields")
query = """
    SELECT 
        log_id, timestamp, level, message, source_type,
        host, service, category, tags, raw_log,
        is_anomaly, anomaly_type, http_status, response_time_ms,
        application_type, transaction_code, splunk_source,
        structured_data
    FROM log_entries 
    ORDER BY timestamp DESC 
    LIMIT 10000
"""

try:
    cursor.execute(query)
    training_data = cursor.fetchall()
    print(f"✅ Loaded {len(training_data):,} log entries for training")
    
    # Show a sample log so you can see what the data looks like
    if training_data:
        print()
        print("📋 Here's a sample log entry:")
        print("-" * 70)
        sample = training_data[0]
        print(f"  Timestamp: {sample['timestamp']}")
        print(f"  Level: {sample['level']}")
        print(f"  Message: {sample['message'][:100]}...")
        print(f"  Source: {sample['source_type']}")
        print(f"  Is Anomaly: {sample['is_anomaly']}")
        print("-" * 70)
        
except Exception as e:
    print(f"❌ Failed to fetch data: {e}")
    cursor.close()
    conn.close()
    sys.exit(1)

# Convert database rows to list of dictionaries
# (Making the data easier to work with)
print()
print("🔄 Converting data to training format...")
training_logs = []
for row in training_data:
    log_dict = dict(row)
    # Convert timestamp to string format
    if log_dict.get('timestamp'):
        log_dict['timestamp'] = log_dict['timestamp'].isoformat()
    # Convert tags from database format if needed
    if isinstance(log_dict.get('tags'), str):
        try:
            log_dict['tags'] = json.loads(log_dict['tags'])
        except:
            log_dict['tags'] = []
    training_logs.append(log_dict)

print(f"✅ Converted {len(training_logs):,} logs to training format")

# Close database connection
cursor.close()
conn.close()
print("✅ Database connection closed")
print()

# =============================================================================
# STEP 3: Prepare Training Data
# =============================================================================
print("🎯 STEP 3: Analyzing the data before training...")
print("-" * 70)
print()
print("💡 What we're checking:")
print("   - How many logs of each type we have (INFO, ERROR, etc.)")
print("   - How many normal vs. anomalous logs")
print("   - This helps us understand if we have good training data")
print()

# Count log levels
level_counts = {}
anomaly_count = 0
for log in training_logs:
    level = log.get('level', 'UNKNOWN')
    level_counts[level] = level_counts.get(level, 0) + 1
    if log.get('is_anomaly'):
        anomaly_count += 1

print("📊 Log Level Distribution:")
for level, count in sorted(level_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(training_logs)) * 100
    print(f"   {level:10} | {count:6,} logs | {percentage:5.1f}%")

print()
print(f"🔍 Anomaly Distribution:")
print(f"   Normal logs:    {len(training_logs) - anomaly_count:6,} ({((len(training_logs) - anomaly_count)/len(training_logs)*100):.1f}%)")
print(f"   Anomalous logs: {anomaly_count:6,} ({(anomaly_count/len(training_logs)*100):.1f}%)")
print()

# =============================================================================
# STEP 4: Train the Models
# =============================================================================
print("🤖 STEP 4: Training the ML models...")
print("-" * 70)
print()
print("💡 What's happening now:")
print("   This is where the 'learning' happens!")
print("   - The models look at all your logs")
print("   - They find patterns (like 'ERROR usually means a problem')")
print("   - They learn to make predictions based on these patterns")
print()
print("   Training TWO models:")
print("   1. Log Classifier - Categorizes logs (security, performance, etc.)")
print("   2. Anomaly Detector - Finds unusual patterns")
print()
print("⏳ This might take 1-2 minutes... Please wait...")
print()

# Import the ML service
try:
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Replace dash with underscore for Python import
    ml_path = os.path.join(project_root, 'external-services', 'ml')
    sys.path.insert(0, ml_path)
    
    # Now we can import from the ml directory directly
    from ml_service import MLService
    
    print("✅ ML service imported successfully!")
    print()
except ImportError as e:
    print(f"❌ Failed to import ML service: {e}")
    print("\nTroubleshooting:")
    print(f"  - Checking if external-services/ml/ exists...")
    ml_dir = os.path.join(os.path.dirname(__file__), 'external-services', 'ml')
    if os.path.exists(ml_dir):
        print(f"  ✅ Directory exists: {ml_dir}")
        print(f"  - Files in directory:")
        for f in os.listdir(ml_dir):
            if f.endswith('.py'):
                print(f"      • {f}")
    else:
        print(f"  ❌ Directory not found: {ml_dir}")
    print()
    print("Detailed error:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Initialize ML service
# (This creates the "teacher" that will train the models)
ml_service = MLService(model_storage_path='models/')

# Train all models
# (This is where the actual learning happens!)
try:
    results = ml_service.train_all_models(training_logs)
    
    print("✅ Training completed successfully!")
    print()
    
    # =============================================================================
    # STEP 5: Display Results
    # =============================================================================
    print("="*70)
    print("🎉 TRAINING RESULTS")
    print("="*70)
    print()
    
    # Log Classifier Results
    if 'log_classifier' in results['models']:
        classifier_results = results['models']['log_classifier']
        print("📊 LOG CLASSIFIER (Categorization Model)")
        print("-" * 70)
        print(f"   Status: ✅ Trained Successfully")
        print(f"   Accuracy: {classifier_results.get('accuracy', 0)*100:.1f}%")
        print()
        print("   💡 What this means:")
        print("   - The model can now predict what category a log belongs to")
        print("   - Examples: security, performance, system, error, etc.")
        print(f"   - It gets it right about {classifier_results.get('accuracy', 0)*100:.0f}% of the time")
        print()
    
    # Anomaly Detector Results
    if 'anomaly_detector' in results['models']:
        anomaly_results = results['models']['anomaly_detector']
        print("🔍 ANOMALY DETECTOR (Pattern Recognition Model)")
        print("-" * 70)
        print(f"   Status: ✅ Trained Successfully")
        print(f"   Accuracy: {anomaly_results.get('accuracy', 0)*100:.1f}%")
        print()
        print("   💡 What this means:")
        print("   - The model can now detect unusual patterns in logs")
        print("   - It spots things like system failures, security issues, etc.")
        print(f"   - It correctly identifies anomalies about {anomaly_results.get('accuracy', 0)*100:.0f}% of the time")
        print()
    
    # Overall Summary
    print("="*70)
    print("✅ SUCCESS! Your models are trained and ready to use!")
    print("="*70)
    print()
    print("📁 Models saved to: models/")
    print("   - log_classifier.pkl")
    print("   - anomaly_detector.pkl")
    print("   - ml_service_metadata.json")
    print()
    print("🚀 Next Steps:")
    print("   1. Your models are now saved and ready to use")
    print("   2. Continue to Step 3 in the ML Enablement Guide")
    print("   3. Update the API to use these real models (instead of mock data)")
    print()
    print("💡 What you've learned:")
    print("   - How to connect to a database and fetch data")
    print("   - How to prepare data for machine learning")
    print("   - How to train classification and anomaly detection models")
    print("   - How to interpret training results")
    print()
    print("🎓 You just trained your first ML models! Great job! 🎉")
    print("="*70)
    
except Exception as e:
    print(f"❌ Training failed: {e}")
    print()
    print("Detailed error:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

