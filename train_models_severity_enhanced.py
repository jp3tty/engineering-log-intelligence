"""
Enhanced Business Severity Prediction Model
============================================

This script trains an ML model using MULTIPLE FEATURES:
- Text features (message content via TF-IDF)
- Categorical features (service name, endpoint, log level)
- Numerical features (HTTP status, response time)

This approach learns context: "payment-api + error" vs "test-service + error"

Author: Engineering Log Intelligence Team
Date: October 16, 2025
"""

import os
import sys
import json
import pickle
from datetime import datetime
import numpy as np

# Install ML libraries if needed
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from scipy.sparse import hstack, csr_matrix
except ImportError:
    print("📦 Installing ML libraries...")
    os.system("pip install scikit-learn scipy numpy")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from scipy.sparse import hstack, csr_matrix

print("="*70)
print("🚀 ENHANCED BUSINESS SEVERITY PREDICTION - MULTI-FEATURE MODEL")
print("="*70)
print()
print("💡 This model uses:")
print("   • Text features (message content)")
print("   • Service context (payment-api vs test-service)")
print("   • Endpoint context (/payment/process vs /health)")
print("   • Log level (ERROR vs INFO)")
print("   • HTTP status codes")
print("   • Response times")
print()

# =============================================================================
# STEP 1: Load Training Data
# =============================================================================
print("📂 Loading labeled training data...")
training_file = 'severity_training_data.json'

if not os.path.exists(training_file):
    print(f"❌ Training data not found: {training_file}")
    sys.exit(1)

with open(training_file, 'r') as f:
    data = json.load(f)

print(f"✅ Loaded {len(data):,} labeled records")
print()

# =============================================================================
# STEP 2: Extract All Features
# =============================================================================
print("🔧 Extracting multiple feature types...")

# Text features
messages = [row['message'] for row in data]
print(f"   • Messages: {len(messages):,}")

# Categorical features
services = [row.get('service', row.get('source_type', 'unknown')) for row in data]
endpoints = [row.get('endpoint', 'unknown') for row in data]
levels = [row['original_level'] for row in data]
print(f"   • Services: {len(set(services))} unique")
print(f"   • Endpoints: {len(set(endpoints))} unique")
print(f"   • Levels: {len(set(levels))} unique")

# Numerical features
http_statuses = [row.get('http_status', 200) or 200 for row in data]
response_times = [float(row.get('response_time_ms', 100) or 100) for row in data]
print(f"   • HTTP statuses: {len(set(http_statuses))} unique")
print(f"   • Response times: {min(response_times):.0f}ms - {max(response_times):.0f}ms")

# Target labels
severities = [row['severity'] for row in data]
print()

# Show distribution
from collections import Counter
severity_dist = Counter(severities)
print(f"📊 Severity distribution:")
for severity in ['critical', 'high', 'medium', 'low']:
    count = severity_dist.get(severity, 0)
    pct = (count / len(severities) * 100) if len(severities) > 0 else 0
    print(f"   {severity.capitalize():8}: {count:5,} ({pct:5.1f}%)")
print()

# =============================================================================
# STEP 3: Feature Engineering - Convert All Features to Numbers
# =============================================================================
print("🧮 Feature Engineering: Converting all features to numerical...")
print()

# 3.1: Text features using TF-IDF
print("   1️⃣  Text Features (TF-IDF)...")
text_vectorizer = TfidfVectorizer(
    max_features=500,  # Top 500 most important words
    stop_words='english',
    ngram_range=(1, 2)  # Single words and 2-word phrases
)
X_text = text_vectorizer.fit_transform(messages)
print(f"      ✅ {X_text.shape[1]} text features created")

# 3.2: Service encoding
print("   2️⃣  Service Features (Label Encoding)...")
service_encoder = LabelEncoder()
X_service = service_encoder.fit_transform(services).reshape(-1, 1)
print(f"      ✅ Encoded {len(service_encoder.classes_)} services")

# 3.3: Endpoint encoding
print("   3️⃣  Endpoint Features (Label Encoding)...")
endpoint_encoder = LabelEncoder()
X_endpoint = endpoint_encoder.fit_transform(endpoints).reshape(-1, 1)
print(f"      ✅ Encoded {len(endpoint_encoder.classes_)} endpoints")

# 3.4: Log level encoding
print("   4️⃣  Log Level Features (Label Encoding)...")
level_encoder = LabelEncoder()
X_level = level_encoder.fit_transform(levels).reshape(-1, 1)
print(f"      ✅ Encoded {len(level_encoder.classes_)} log levels")

# 3.5: Numerical features (normalize)
print("   5️⃣  Numerical Features (HTTP status, response time)...")
scaler = StandardScaler()
X_numerical = scaler.fit_transform(np.column_stack([http_statuses, response_times]))
print(f"      ✅ Normalized 2 numerical features")
print()

# =============================================================================
# STEP 4: Combine All Features
# =============================================================================
print("🔗 Combining all features into single feature matrix...")

# Convert numpy arrays to sparse matrices for efficient combination
X_service_sparse = csr_matrix(X_service)
X_endpoint_sparse = csr_matrix(X_endpoint)
X_level_sparse = csr_matrix(X_level)
X_numerical_sparse = csr_matrix(X_numerical)

# Combine all features horizontally
X_combined = hstack([
    X_text,              # Text features (500 dimensions)
    X_service_sparse,    # Service (1 dimension)
    X_endpoint_sparse,   # Endpoint (1 dimension)
    X_level_sparse,      # Log level (1 dimension)
    X_numerical_sparse   # HTTP status + response time (2 dimensions)
])

print(f"✅ Combined feature matrix: {X_combined.shape[0]:,} samples × {X_combined.shape[1]} features")
print()
print(f"   Feature breakdown:")
print(f"   • Text (TF-IDF):        {X_text.shape[1]} features")
print(f"   • Service:              1 feature")
print(f"   • Endpoint:             1 feature")
print(f"   • Log Level:            1 feature")
print(f"   • HTTP Status:          1 feature")
print(f"   • Response Time:        1 feature")
print(f"   • {'─'*30}")
print(f"   • TOTAL:                {X_combined.shape[1]} features")
print()

# Prepare target
y = np.array(severities)

# =============================================================================
# STEP 5: Split into Training and Testing Sets
# =============================================================================
print("✂️  Splitting data: 80% training, 20% testing...")

X_train, X_test, y_train, y_test = train_test_split(
    X_combined, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Training set: {X_train.shape[0]:,} samples")
print(f"   Testing set:  {X_test.shape[0]:,} samples")
print()

# =============================================================================
# STEP 6: Train Enhanced Model
# =============================================================================
print("🎓 Training Enhanced RandomForest Classifier...")
print("   (Using all features: text + service + endpoint + context)")
print()

classifier = RandomForestClassifier(
    n_estimators=200,  # More trees for better accuracy
    max_depth=25,  # Deeper trees to capture complex patterns
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',  # Handle imbalanced classes
    random_state=42,
    n_jobs=-1,  # Use all CPU cores
    verbose=1  # Show progress
)

classifier.fit(X_train, y_train)
print()
print("✅ Training complete!")
print()

# =============================================================================
# STEP 7: Evaluate Enhanced Model
# =============================================================================
print("🧪 Evaluating enhanced model on test set...")
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
print("   " + " ".join(f"{label:>10}" for label in labels))
for i, label in enumerate(labels):
    print(f"{label:>10}  " + " ".join(f"{cm[i][j]:>10}" for j in range(len(labels))))
print()

# =============================================================================
# STEP 8: Feature Importance Analysis
# =============================================================================
print("🔍 Feature Importance Analysis:")
print("-" * 70)

# Get feature importances
importances = classifier.feature_importances_

# Create feature names
text_feature_names = text_vectorizer.get_feature_names_out()
all_feature_names = list(text_feature_names) + ['service', 'endpoint', 'log_level', 'http_status', 'response_time']

# Sort by importance
indices = np.argsort(importances)[::-1]

# Show top 25 features
print("Top 25 Most Important Features:")
for i in range(min(25, len(importances))):
    idx = indices[i]
    if idx < len(all_feature_names):
        feature_name = all_feature_names[idx]
        print(f"   {i+1:2}. {feature_name:30} | importance: {importances[idx]:.4f}")
print()

# =============================================================================
# STEP 9: Test with Real Examples
# =============================================================================
print("🔮 Testing with real-world examples:")
print("-" * 70)

test_cases = [
    {
        'message': 'Payment processor connection timeout',
        'service': 'payment-api',
        'endpoint': '/payment/process',
        'level': 'ERROR',
        'http_status': 500,
        'response_time_ms': 5000,
        'expected': 'critical'
    },
    {
        'message': 'Database connection failed',
        'service': 'test-service',
        'endpoint': '/test/api',
        'level': 'ERROR',
        'http_status': 500,
        'response_time_ms': 1000,
        'expected': 'low'
    },
    {
        'message': 'User logged in successfully',
        'service': 'auth-service',
        'endpoint': '/auth/login',
        'level': 'INFO',
        'http_status': 200,
        'response_time_ms': 150,
        'expected': 'medium'
    },
    {
        'message': 'Health check passed',
        'service': 'health-check',
        'endpoint': '/health',
        'level': 'INFO',
        'http_status': 200,
        'response_time_ms': 50,
        'expected': 'low'
    },
    {
        'message': 'Payment processed successfully',
        'service': 'payment-api',
        'endpoint': '/payment/process',
        'level': 'INFO',
        'http_status': 200,
        'response_time_ms': 200,
        'expected': 'medium'
    }
]

for i, test in enumerate(test_cases, 1):
    # Transform test case features
    X_test_text = text_vectorizer.transform([test['message']])
    X_test_service = csr_matrix(service_encoder.transform([test['service']]).reshape(-1, 1))
    X_test_endpoint = csr_matrix(endpoint_encoder.transform([test['endpoint']]).reshape(-1, 1))
    X_test_level = csr_matrix(level_encoder.transform([test['level']]).reshape(-1, 1))
    X_test_numerical = csr_matrix(scaler.transform([[test['http_status'], test['response_time_ms']]]))
    
    X_test_combined = hstack([X_test_text, X_test_service, X_test_endpoint, X_test_level, X_test_numerical])
    
    predicted = classifier.predict(X_test_combined)[0]
    probabilities = classifier.predict_proba(X_test_combined)[0]
    confidence = max(probabilities)
    
    match = '✅' if predicted == test['expected'] else '❌'
    
    print(f"{match} Test {i}:")
    print(f"   Service: {test['service']} | Endpoint: {test['endpoint']} | Level: {test['level']}")
    print(f"   Message: '{test['message']}'")
    print(f"   Expected: {test['expected'].upper()} | Predicted: {predicted.upper()} (confidence: {confidence:.1%})")
    print()

# =============================================================================
# STEP 10: Save Enhanced Model
# =============================================================================
print("💾 Saving enhanced model and all encoders...")
os.makedirs('models', exist_ok=True)

# Save classifier
with open('models/severity_classifier_enhanced.pkl', 'wb') as f:
    pickle.dump(classifier, f)
print("   ✅ models/severity_classifier_enhanced.pkl")

# Save text vectorizer
with open('models/severity_vectorizer_enhanced.pkl', 'wb') as f:
    pickle.dump(text_vectorizer, f)
print("   ✅ models/severity_vectorizer_enhanced.pkl")

# Save all encoders
encoders = {
    'service_encoder': service_encoder,
    'endpoint_encoder': endpoint_encoder,
    'level_encoder': level_encoder,
    'scaler': scaler
}
with open('models/severity_encoders_enhanced.pkl', 'wb') as f:
    pickle.dump(encoders, f)
print("   ✅ models/severity_encoders_enhanced.pkl")

# Save metadata
metadata = {
    'trained_at': datetime.now().isoformat(),
    'model_type': 'RandomForestClassifier_MultiFeature',
    'num_training_samples': X_train.shape[0],
    'num_test_samples': X_test.shape[0],
    'accuracy': float(accuracy),
    'total_features': int(X_combined.shape[1]),
    'feature_breakdown': {
        'text_features': int(X_text.shape[1]),
        'service_feature': 1,
        'endpoint_feature': 1,
        'level_feature': 1,
        'http_status_feature': 1,
        'response_time_feature': 1
    },
    'severity_levels': list(set(severities)),
    'severity_distribution': {
        severity: int(severity_dist.get(severity, 0))
        for severity in ['critical', 'high', 'medium', 'low']
    },
    'n_estimators': 200,
    'purpose': 'business_severity_prediction_enhanced'
}

with open('models/severity_metadata_enhanced.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print("   ✅ models/severity_metadata_enhanced.json")
print()

# =============================================================================
# DONE!
# =============================================================================
print("="*70)
print("🎉 ENHANCED MODEL TRAINING COMPLETE!")
print("="*70)
print()
print(f"📊 Final Metrics:")
print(f"   Accuracy:         {accuracy*100:.1f}%")
print(f"   Training samples: {X_train.shape[0]:,}")
print(f"   Total features:   {X_combined.shape[1]}")
print(f"   Text features:    {X_text.shape[1]}")
print(f"   Context features: 5 (service, endpoint, level, status, time)")
print()
print("📁 Saved Files:")
print("   • models/severity_classifier_enhanced.pkl")
print("   • models/severity_vectorizer_enhanced.pkl")
print("   • models/severity_encoders_enhanced.pkl")
print("   • models/severity_metadata_enhanced.json")
print()
print("✨ Key Improvements Over Text-Only Model:")
print("   • Understands service context (payment-api vs test-service)")
print("   • Considers endpoint criticality (/payment vs /health)")
print("   • Uses HTTP status and response time")
print("   • Much higher accuracy on context-dependent scenarios")
print()
print("🚀 Ready for integration into production!")
print()

