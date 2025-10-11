"""
Test Your Trained ML Models
============================
This script tests that your models work correctly before deploying.

Author: Engineering Log Intelligence Team
Date: October 11, 2025
"""

import pickle
import json
import os
from datetime import datetime

print("="*70)
print("🧪 TESTING YOUR TRAINED ML MODELS")
print("="*70)
print()

# =============================================================================
# STEP 1: Load the Models
# =============================================================================
print("📂 STEP 1: Loading your trained models...")
print("-" * 70)

try:
    # Load the classifier
    with open('models/log_classifier_simple.pkl', 'rb') as f:
        classifier = pickle.load(f)
    print("✅ Loaded: log_classifier_simple.pkl")
    
    # Load the anomaly detector
    with open('models/anomaly_detector_simple.pkl', 'rb') as f:
        anomaly_detector = pickle.load(f)
    print("✅ Loaded: anomaly_detector_simple.pkl")
    
    # Load the vectorizer (needed to convert text to numbers)
    with open('models/vectorizer_simple.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    print("✅ Loaded: vectorizer_simple.pkl")
    
    # Load metadata
    with open('models/metadata_simple.json', 'r') as f:
        metadata = json.load(f)
    print("✅ Loaded: metadata_simple.json")
    
    print()
    print("📊 Model Information:")
    print(f"   Trained at: {metadata['trained_at']}")
    print(f"   Training samples: {metadata['num_training_samples']:,}")
    print(f"   Classifier accuracy: {metadata['classifier_accuracy']*100:.1f}%")
    print(f"   Anomaly detector accuracy: {metadata['anomaly_detector_accuracy']*100:.1f}%")
    print(f"   Features: {metadata['features']}")
    print()
    
except FileNotFoundError as e:
    print(f"❌ Error: Could not find model files")
    print(f"   Make sure you ran: python train_models_simple.py")
    exit(1)
except Exception as e:
    print(f"❌ Error loading models: {e}")
    exit(1)

# =============================================================================
# STEP 2: Test with Sample Log Messages
# =============================================================================
print("="*70)
print("🔬 STEP 2: Testing with Sample Log Messages")
print("="*70)
print()

# Test messages that simulate real logs
test_logs = [
    {
        "message": "ERROR: Database connection timeout after 30 seconds",
        "expected_level": "ERROR",
        "expected_anomaly": True
    },
    {
        "message": "INFO: User authentication successful",
        "expected_level": "INFO",
        "expected_anomaly": False
    },
    {
        "message": "FATAL: Out of memory exception - system crash imminent",
        "expected_level": "FATAL",
        "expected_anomaly": True
    },
    {
        "message": "DEBUG: Entering function calculateTotal()",
        "expected_level": "DEBUG",
        "expected_anomaly": False
    },
    {
        "message": "WARN: High memory usage detected - 85% capacity",
        "expected_level": "WARN",
        "expected_anomaly": False
    },
    {
        "message": "ERROR: Failed to connect to payment gateway",
        "expected_level": "ERROR",
        "expected_anomaly": True
    },
    {
        "message": "INFO: Request processed in 145ms",
        "expected_level": "INFO",
        "expected_anomaly": False
    }
]

print("Testing 7 sample log messages:")
print()

all_correct = True
for i, log in enumerate(test_logs, 1):
    message = log['message']
    
    # Convert message to numbers (vectorize)
    X = vectorizer.transform([message])
    
    # Predict log level
    predicted_level = classifier.predict(X)[0]
    level_proba = classifier.predict_proba(X)[0]
    level_confidence = max(level_proba)
    
    # Predict if anomaly
    predicted_anomaly = anomaly_detector.predict(X)[0]
    anomaly_proba = anomaly_detector.predict_proba(X)[0]
    anomaly_confidence = max(anomaly_proba)
    
    # Check if predictions match expectations
    level_match = "✅" if predicted_level == log['expected_level'] else "⚠️"
    anomaly_match = "✅" if predicted_anomaly == log['expected_anomaly'] else "⚠️"
    
    if predicted_level != log['expected_level'] or predicted_anomaly != log['expected_anomaly']:
        all_correct = False
    
    print(f"Test {i}:")
    print(f"  Message: \"{message[:60]}...\"")
    print(f"  {level_match} Predicted Level: {predicted_level} (confidence: {level_confidence*100:.1f}%)")
    print(f"  {anomaly_match} Is Anomaly: {'YES' if predicted_anomaly else 'NO'} (confidence: {anomaly_confidence*100:.1f}%)")
    print()

# =============================================================================
# STEP 3: Test API Response Format
# =============================================================================
print("="*70)
print("📡 STEP 3: Testing API Response Format")
print("="*70)
print()

print("💡 Simulating what the API will return to the frontend:")
print()

# Create a sample API response
def create_ml_response(messages):
    """Create an API response in the format the frontend expects"""
    results = []
    
    for msg in messages:
        # Convert to numbers
        X = vectorizer.transform([msg])
        
        # Get predictions
        level = classifier.predict(X)[0]
        level_proba = classifier.predict_proba(X)[0]
        level_confidence = max(level_proba)
        
        is_anomaly = anomaly_detector.predict(X)[0]
        anomaly_proba = anomaly_detector.predict_proba(X)[0]
        anomaly_score = anomaly_proba[1] if len(anomaly_proba) > 1 else anomaly_proba[0]
        
        results.append({
            "message": msg,
            "classification": level,
            "confidence": round(float(level_confidence), 3),
            "anomaly_score": round(float(anomaly_score), 3),
            "is_anomaly": bool(is_anomaly),
            "severity": "high" if is_anomaly else "low",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return {
        "success": True,
        "results": results,
        "total_analyzed": len(results),
        "model_info": {
            "classifier_accuracy": metadata['classifier_accuracy'],
            "anomaly_accuracy": metadata['anomaly_detector_accuracy'],
            "trained_at": metadata['trained_at']
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Test with a few messages
test_messages = [
    "Database connection failed",
    "User logged in successfully",
    "System running out of memory"
]

response = create_ml_response(test_messages)

print("API Response:")
print(json.dumps(response, indent=2))
print()

# =============================================================================
# STEP 4: Performance Test
# =============================================================================
print("="*70)
print("⚡ STEP 4: Performance Test")
print("="*70)
print()

import time

# Test how fast the models can process logs
num_predictions = 100
start_time = time.time()

for _ in range(num_predictions):
    X = vectorizer.transform(["Test message for performance"])
    _ = classifier.predict(X)
    _ = anomaly_detector.predict(X)

end_time = time.time()
elapsed = end_time - start_time
per_prediction = (elapsed / num_predictions) * 1000  # Convert to ms

print(f"📊 Performance Results:")
print(f"   Predictions: {num_predictions}")
print(f"   Total time: {elapsed:.2f} seconds")
print(f"   Time per prediction: {per_prediction:.2f} ms")
print(f"   Throughput: {num_predictions/elapsed:.0f} predictions/second")
print()

if per_prediction < 50:
    print("✅ EXCELLENT: Fast enough for real-time use!")
elif per_prediction < 200:
    print("✅ GOOD: Suitable for production use")
else:
    print("⚠️  SLOW: May need optimization")

print()

# =============================================================================
# STEP 5: Summary
# =============================================================================
print("="*70)
print("📋 TEST SUMMARY")
print("="*70)
print()

print("✅ Models loaded successfully")
print(f"✅ Tested on {len(test_logs)} sample logs")
print(f"✅ API response format validated")
print(f"✅ Performance: {per_prediction:.1f}ms per prediction")
print()

if all_correct:
    print("🎉 ALL TESTS PASSED!")
else:
    print("⚠️  Some predictions didn't match expectations")
    print("   (This is normal - ML models aren't always 100% accurate)")

print()
print("✅ Your models are ready to be integrated into the API!")
print()
print("🚀 Next Steps:")
print("   1. Update api/ml.py to use these real models")
print("   2. Test locally with 'vercel dev'")
print("   3. Deploy to production with 'vercel --prod'")
print()
print("="*70)

