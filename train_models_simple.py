"""
Simplified ML Model Training Script
===================================
This script trains machine learning models in a way that's easy to understand!

For beginners: This shows you EXACTLY how machine learning works.

Author: Engineering Log Intelligence Team  
Date: October 11, 2025
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import pickle
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv('.env.local')

# Install ML libraries if needed
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import numpy as np
except ImportError:
    print("📦 Installing ML libraries (scikit-learn, numpy)...")
    os.system("pip install scikit-learn numpy")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import numpy as np

print("="*70)
print("🤖 SIMPLIFIED ML TRAINING - Learning Machine Learning!")
print("="*70)
print()
print("💡 What is Machine Learning?")
print("   Imagine teaching a computer to recognize patterns, like teaching")
print("   a child to identify different types of animals.")
print()
print("   We'll train TWO models:")
print("   1. Log Level Classifier - Predicts if a log is ERROR, WARN, INFO, etc.")
print("   2. Anomaly Detector - Finds unusual/abnormal patterns")
print()
# Auto-continue for non-interactive mode
import time
time.sleep(0.5)  # Brief pause to let you read
print()

# =============================================================================
# STEP 1: Connect and Fetch Data
# =============================================================================
print("="*70)
print("STEP 1: Getting Your Log Data")
print("="*70)
print()

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

print("🔄 Connecting to database...")
conn = psycopg2.connect(database_url)
cursor = conn.cursor(cursor_factory=RealDictCursor)
print("✅ Connected!")
print()

print("📊 Fetching 10,000 logs from your database...")
cursor.execute("""
    SELECT 
        log_id, level, message, is_anomaly
    FROM log_entries 
    WHERE message IS NOT NULL 
    AND level IS NOT NULL
    ORDER BY timestamp DESC 
    LIMIT 10000
""")

data = cursor.fetchall()
print(f"✅ Loaded {len(data):,} logs")
cursor.close()
conn.close()
print()

# Check if we have data to work with
if len(data) == 0:
    print("⚠️  No logs found in database")
    print()
    print("This is expected when:")
    print("  • The database is empty")
    print("  • No logs have message and level fields")
    print()
    print("💡 Skipping model training - no training data available")
    print()
    print("="*70)
    print("✅ TRAINING SKIPPED (NO DATA)")
    print("="*70)
    print()
    sys.exit(0)  # Exit gracefully, not an error

# Show sample
print("📋 Sample logs:")
for i in range(min(3, len(data))):
    print(f"   {i+1}. [{data[i]['level']}] {data[i]['message'][:60]}...")
print()
# Auto-continue for non-interactive mode
import time
time.sleep(0.5)  # Brief pause to let you read
print()

# =============================================================================
# STEP 2: Prepare the Data
# =============================================================================
print("="*70)
print("STEP 2: Preparing Data for Machine Learning")
print("="*70)
print()
print("💡 What we're doing:")
print("   Computers don't understand text like 'ERROR' or 'Database failed'")
print("   We need to convert text into numbers that the ML model can understand.")
print()
print("   Think of it like translating from English to Math!")
print()

# Extract messages and labels
messages = [row['message'] for row in data]
levels = [row['level'] for row in data]
is_anomaly = [row['is_anomaly'] if row['is_anomaly'] is not None else False for row in data]

print(f"📊 Data distribution:")
level_counts = {}
for level in levels:
    level_counts[level] = level_counts.get(level, 0) + 1

for level, count in sorted(level_counts.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(levels)) * 100
    print(f"   {level:10} | {count:5,} logs | {pct:5.1f}%")

print()
print(f"   Anomalies: {sum(is_anomaly):,} ({(sum(is_anomaly)/len(is_anomaly)*100):.1f}%)")
print()
# Auto-continue for non-interactive mode
import time
time.sleep(0.5)  # Brief pause to let you read
print()

# =============================================================================
# STEP 3: Convert Text to Numbers (Vectorization)
# =============================================================================
print("="*70)
print("STEP 3: Converting Text to Numbers")
print("="*70)
print()
print("💡 How it works:")
print("   We use something called 'TF-IDF' (Term Frequency-Inverse Document Frequency)")
print("   It's a fancy name for counting how important each word is.")
print()
print("   Example:")
print("     'Database connection failed' becomes:")
print("     [database: 0.6, connection: 0.5, failed: 0.7, ...]")
print()

print("🔄 Converting {Human: 'Loading...'")
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X = vectorizer.fit_transform(messages)
print(f"✅ Converted {len(messages):,} messages into {X.shape[1]} numerical features")
print()
print(f"   💡 What this means:")
print(f"      Each log message is now represented by {X.shape[1]} numbers")
print(f"      The model will learn patterns from these numbers")
print()
# Auto-continue for non-interactive mode
import time
time.sleep(0.5)  # Brief pause to let you read
print()

# =============================================================================
# STEP 4: Train the Log Level Classifier
# =============================================================================
print("="*70)
print("STEP 4: Training Model #1 - Log Level Classifier")
print("="*70)
print()
print("💡 What this model does:")
print("   Given a log message, predict if it's INFO, WARN, ERROR, etc.")
print()
print("🎓 How training works:")
print("   1. Split data: 80% for training, 20% for testing")
print("   2. Show the model examples: 'This message → ERROR level'")
print("   3. The model finds patterns in the numbers")
print("   4. Test it on new data to see how well it learned")
print()

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, levels, test_size=0.2, random_state=42
)

print(f"📊 Training set: {X_train.shape[0]:,} logs")
print(f"📊 Testing set:  {X_test.shape[0]:,} logs")
print()

print("🤖 Training the classifier...")
print("   (This is where the computer 'learns' the patterns)")
print()

# Train classifier
classifier = RandomForestClassifier(
    n_estimators=100,  # Use 100 "decision trees"
    random_state=42,
    n_jobs=-1  # Use all CPU cores
)

classifier.fit(X_train, y_train)
print("✅ Training complete!")
print()

# Test the model
print("🧪 Testing the model on unseen data...")
y_pred = classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"✅ Accuracy: {accuracy*100:.1f}%")
print()
print("💡 What this means:")
print(f"   Out of 100 predictions, the model gets {int(accuracy*100)} right!")
print(f"   That's pretty good for a first attempt!")
print()

# Show detailed results
print("📊 Detailed Results by Log Level:")
print(classification_report(y_test, y_pred))
print()
# Auto-continue for non-interactive mode
import time
time.sleep(0.5)  # Brief pause to let you read
print()

# =============================================================================
# STEP 5: Train the Anomaly Detector
# =============================================================================
print("="*70)
print("STEP 5: Training Model #2 - Anomaly Detector")
print("="*70)
print()
print("💡 What this model does:")
print("   Finds unusual patterns - like a security guard spotting suspicious behavior")
print()

# For anomaly detection, we need to split the same way
X_train_anom, X_test_anom, y_anomaly_train, y_anomaly_test = train_test_split(
    X, is_anomaly, test_size=0.2, random_state=42
)

print(f"📊 Normal logs in training:    {sum([not x for x in y_anomaly_train]):,}")
print(f"📊 Anomalous logs in training: {sum(y_anomaly_train):,}")
print()

print("🤖 Training the anomaly detector...")
anomaly_detector = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'  # Handle imbalanced data
)

anomaly_detector.fit(X_train_anom, y_anomaly_train)
print("✅ Training complete!")
print()

# Test anomaly detector
y_anomaly_pred = anomaly_detector.predict(X_test_anom)
anomaly_accuracy = accuracy_score(y_anomaly_test, y_anomaly_pred)

print(f"✅ Anomaly Detection Accuracy: {anomaly_accuracy*100:.1f}%")
print()
print("💡 What this means:")
print(f"   The model correctly identifies anomalies {int(anomaly_accuracy*100)}% of the time")
print()
# Auto-continue for non-interactive mode
import time
time.sleep(0.5)  # Brief pause to let you read
print()

# =============================================================================
# STEP 6: Save the Models
# =============================================================================
print("="*70)
print("STEP 6: Saving Your Trained Models")
print("="*70)
print()
print("💡 Why save models?")
print("   Training takes time! We save the models so we can use them")
print("   later without retraining.")
print()

# Create models directory
os.makedirs('models', exist_ok=True)

print("💾 Saving models to 'models/' directory...")

# Save classifier
with open('models/log_classifier_simple.pkl', 'wb') as f:
    pickle.dump(classifier, f)
print("   ✅ log_classifier_simple.pkl")

# Save anomaly detector
with open('models/anomaly_detector_simple.pkl', 'wb') as f:
    pickle.dump(anomaly_detector, f)
print("   ✅ anomaly_detector_simple.pkl")

# Save vectorizer (needed to convert new messages)
with open('models/vectorizer_simple.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
print("   ✅ vectorizer_simple.pkl")

# Save metadata
metadata = {
    'trained_at': datetime.now().isoformat(),
    'num_training_samples': X_train.shape[0],
    'classifier_accuracy': float(accuracy),
    'anomaly_detector_accuracy': float(anomaly_accuracy),
    'features': int(X.shape[1]),
    'log_levels': list(set(levels)),
}

with open('models/metadata_simple.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print("   ✅ metadata_simple.json")
print()

# =============================================================================
# STEP 7: Try it Out!
# =============================================================================
print("="*70)
print("STEP 7: Let's Try Your Trained Models!")
print("="*70)
print()
print("💡 Let's test the models on some example messages:")
print()

test_messages = [
    "Database connection failed with error code 500",
    "User logged in successfully",
    "CRITICAL: System running out of memory",
    "Debug trace for request processing",
    "WARNING: Unusual network traffic detected"
]

for i, test_msg in enumerate(test_messages, 1):
    # Convert message to numbers
    X_test_msg = vectorizer.transform([test_msg])
    
    # Predict
    predicted_level = classifier.predict(X_test_msg)[0]
    is_anomaly_pred = anomaly_detector.predict(X_test_msg)[0]
    
    print(f"{i}. Message: \"{test_msg}\"")
    print(f"   → Predicted Level: {predicted_level}")
    print(f"   → Is Anomaly: {'YES' if is_anomaly_pred else 'NO'}")
    print()

print()
print("="*70)
print("🎉 CONGRATULATIONS! You've Trained Your First ML Models!")
print("="*70)
print()
print("📚 What You've Learned:")
print("   1. How to prepare data for machine learning")
print("   2. How to convert text into numbers (vectorization)")
print("   3. How to train classification models")
print("   4. How to evaluate model accuracy")
print("   5. How to save and use trained models")
print()
print("📊 Your Results:")
print(f"   • Log Classifier Accuracy: {accuracy*100:.1f}%")
print(f"   • Anomaly Detector Accuracy: {anomaly_accuracy*100:.1f}%")
print(f"   • Training Data: {len(data):,} logs")
print(f"   • Models Saved: models/ directory")
print()
print("🚀 Next Steps:")
print("   1. Your models are saved and ready to use!")
print("   2. Continue to Step 3 in the ML Enablement Guide")
print("   3. Update your API to use these real models")
print()
print("🎓 You're now a machine learning practitioner! 🎉")
print("="*70)

