"""
Train Business Severity Prediction Model
=========================================

This script trains an ML model to predict business severity
(critical/high/medium/low) based on log messages.

Unlike predicting log levels (which servers already provide),
this predicts actual business impact.

Author: Engineering Log Intelligence Team
Date: October 16, 2025
"""

import os
import sys
import json
import pickle
from datetime import datetime

# Install ML libraries if needed
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    import numpy as np
except ImportError:
    print("📦 Installing ML libraries (scikit-learn, numpy)...")
    os.system("pip install scikit-learn numpy")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    import numpy as np

print("="*70)
print("🤖 TRAINING BUSINESS SEVERITY PREDICTION MODEL")
print("="*70)
print()

# =============================================================================
# STEP 1: Load Training Data
# =============================================================================
print("📂 Loading labeled training data...")
training_file = 'severity_training_data.json'

if not os.path.exists(training_file):
    print(f"❌ Training data not found: {training_file}")
    print("   Run generate_severity_training_data.py first!")
    sys.exit(1)

with open(training_file, 'r') as f:
    data = json.load(f)

print(f"✅ Loaded {len(data):,} labeled records")
print()

# =============================================================================
# STEP 2: Prepare Training Data
# =============================================================================
print("🔧 Preparing data for ML training...")

# Extract messages and severity labels
messages = [row['message'] for row in data]
severities = [row['severity'] for row in data]

# Show distribution
from collections import Counter
severity_dist = Counter(severities)
print(f"📊 Severity distribution in training data:")
for severity in ['critical', 'high', 'medium', 'low']:
    count = severity_dist.get(severity, 0)
    pct = (count / len(severities) * 100) if len(severities) > 0 else 0
    print(f"   {severity.capitalize():8}: {count:5,} ({pct:5.1f}%)")
print()

# =============================================================================
# STEP 3: Vectorize Messages (Text → Numbers)
# =============================================================================
print("🔢 Converting text to numerical features (TF-IDF)...")
print()

vectorizer = TfidfVectorizer(
    max_features=1000,  # Top 1000 most important words
    stop_words='english',  # Remove common words like 'the', 'a', etc.
    ngram_range=(1, 2)  # Use single words and 2-word phrases
)

X = vectorizer.fit_transform(messages)
y = np.array(severities)

print(f"✅ Converted {len(messages):,} messages into {X.shape[1]} numerical features")
print()

# =============================================================================
# STEP 4: Split into Training and Testing Sets
# =============================================================================
print("✂️  Splitting data: 80% training, 20% testing...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Training set: {X_train.shape[0]:,} samples")
print(f"   Testing set:  {X_test.shape[0]:,} samples")
print()

# =============================================================================
# STEP 5: Train the Model
# =============================================================================
print("🎓 Training RandomForest Classifier...")
print()

classifier = RandomForestClassifier(
    n_estimators=100,  # Use 100 decision trees
    max_depth=20,  # Limit tree depth to prevent overfitting
    min_samples_split=5,  # Need at least 5 samples to split
    class_weight='balanced',  # Handle imbalanced classes (few critical, many medium)
    random_state=42,
    n_jobs=-1  # Use all CPU cores
)

classifier.fit(X_train, y_train)
print("✅ Training complete!")
print()

# =============================================================================
# STEP 6: Evaluate the Model
# =============================================================================
print("🧪 Evaluating model on test set...")
print()

y_pred = classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"📊 Overall Accuracy: {accuracy*100:.1f}%")
print()

print("📋 Detailed Performance by Severity:")
print("-" * 70)
print(classification_report(y_test, y_pred, zero_division=0))
print()

# Confusion matrix
print("🔀 Confusion Matrix:")
print("   (Rows = Actual, Columns = Predicted)")
print()
cm = confusion_matrix(y_test, y_pred, labels=['critical', 'high', 'medium', 'low'])
labels = ['critical', 'high', 'medium', 'low']

# Print header
print("   " + " ".join(f"{label:>8}" for label in labels))
for i, label in enumerate(labels):
    print(f"{label:>8}  " + " ".join(f"{cm[i][j]:>8}" for j in range(len(labels))))
print()

# =============================================================================
# STEP 7: Feature Importance
# =============================================================================
print("🔍 Top 20 Most Important Words for Severity Prediction:")
print("-" * 70)

feature_names = vectorizer.get_feature_names_out()
importances = classifier.feature_importances_

# Get top 20 features
top_indices = np.argsort(importances)[::-1][:20]
for i, idx in enumerate(top_indices, 1):
    word = feature_names[idx]
    importance = importances[idx]
    print(f"   {i:2}. {word:20} | importance: {importance:.4f}")
print()

# =============================================================================
# STEP 8: Test with Sample Messages
# =============================================================================
print("🔮 Testing with sample messages:")
print("-" * 70)

test_messages = [
    "Payment processor connection timeout",
    "Test database connection failed",
    "User API response time degraded to 2000ms",
    "Health check endpoint returned 200 OK",
    "ERROR: Critical system failure in production",
    "DEBUG: Cache warming completed successfully"
]

for msg in test_messages:
    X_test_msg = vectorizer.transform([msg])
    predicted_severity = classifier.predict(X_test_msg)[0]
    probabilities = classifier.predict_proba(X_test_msg)[0]
    confidence = max(probabilities)
    
    print(f"  Message: '{msg}'")
    print(f"  → Predicted: {predicted_severity.upper()} (confidence: {confidence:.2%})")
    print()

# =============================================================================
# STEP 9: Save the Model
# =============================================================================
print("💾 Saving trained model...")
os.makedirs('models', exist_ok=True)

# Save classifier
with open('models/severity_classifier.pkl', 'wb') as f:
    pickle.dump(classifier, f)
print("   ✅ models/severity_classifier.pkl")

# Save vectorizer (IMPORTANT: needed to process new messages)
with open('models/severity_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
print("   ✅ models/severity_vectorizer.pkl")

# Save metadata
metadata = {
    'trained_at': datetime.now().isoformat(),
    'num_training_samples': X_train.shape[0],
    'num_test_samples': X_test.shape[0],
    'accuracy': float(accuracy),
    'features': int(X.shape[1]),
    'severity_levels': list(set(severities)),
    'severity_distribution': {
        severity: int(severity_dist.get(severity, 0))
        for severity in ['critical', 'high', 'medium', 'low']
    },
    'model_type': 'RandomForestClassifier',
    'n_estimators': 100,
    'purpose': 'business_severity_prediction'
}

with open('models/severity_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print("   ✅ models/severity_metadata.json")
print()

# =============================================================================
# DONE!
# =============================================================================
print("="*70)
print("🎉 MODEL TRAINING COMPLETE!")
print("="*70)
print()
print(f"📊 Final Metrics:")
print(f"   Accuracy:        {accuracy*100:.1f}%")
print(f"   Training samples: {X_train.shape[0]:,}")
print(f"   Features:        {X.shape[1]}")
print()
print("📁 Saved Files:")
print("   • models/severity_classifier.pkl - Trained model")
print("   • models/severity_vectorizer.pkl - Text vectorizer")
print("   • models/severity_metadata.json  - Model info")
print()
print("🚀 Next Steps:")
print("   1. Update LogClassifier to use this model")
print("   2. Update API endpoints")
print("   3. Test predictions")
print("   4. Deploy to production")
print()
print("💡 The model now predicts BUSINESS SEVERITY, not log levels!")
print("   This adds real value beyond what the server already provides.")
print()

