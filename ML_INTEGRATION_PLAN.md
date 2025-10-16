# ML Integration Plan - Better Integration

**Date**: October 16, 2025  
**Goal**: Unify ML system by connecting trained models to the ML service framework  
**Estimated Time**: 3-4 hours

---

## 🎯 What "Better Integration" Means

Currently, you have **disconnected components**:

```
❌ Current State (Disconnected):

external-services/ml/
├── log_classifier.py ──────→ Uses keyword matching (NOT ML)
├── anomaly_detector.py ────→ Uses keyword matching (NOT ML)  
└── ml_service.py ──────────→ Coordinates above (but they're not ML)

models/
├── log_classifier_simple.pkl ──→ Real ML model (UNUSED by framework)
├── anomaly_detector_simple.pkl ─→ Real ML model (UNUSED by framework)
└── vectorizer_simple.pkl ───────→ TF-IDF vectorizer (UNUSED by framework)

api/
├── ml.py ──────────────→ Queries database OR generates mock data
└── ml_lightweight.py ──→ Queries database only
```

**After Integration** (Connected):

```
✅ Integrated State:

external-services/ml/
├── log_classifier.py ──────→ Loads & uses log_classifier_simple.pkl ✅
├── anomaly_detector.py ────→ Loads & uses anomaly_detector_simple.pkl ✅
└── ml_service.py ──────────→ Coordinates real ML models ✅

models/ (deployed to Vercel)
├── log_classifier_simple.pkl
├── anomaly_detector_simple.pkl
└── vectorizer_simple.pkl

api/
├── ml.py ──────────────→ Uses ml_service.py → Real ML models
└── ml_lightweight.py ──→ Uses ml_service.py → Real ML models
```

---

## 📋 Step-by-Step Integration Plan

### Phase 1: Update ML Service Classes (Core Changes)

#### Step 1.1: Update `log_classifier.py`

**Current Issues**:
```python
# Line 102-104
# For this demo, we'll use a simple rule-based classifier
# In a real system, you'd use scikit-learn or similar
self.is_trained = True
```

**Changes Needed**:
1. Remove rule-based `_classify_by_rules()` method
2. Add ability to load `log_classifier_simple.pkl`
3. Update `predict()` to use actual model
4. Update `train()` to actually train sklearn model (or just load pre-trained)

**New Implementation**:
```python
import pickle
import os

class LogClassifier:
    def __init__(self):
        self.model = None  # Will hold RandomForest classifier
        self.vectorizer = None  # Will hold TF-IDF vectorizer
        self.is_trained = False
        self.model_path = 'models/log_classifier_simple.pkl'
        self.vectorizer_path = 'models/vectorizer_simple.pkl'
        self.metadata_path = 'models/metadata_simple.json'
    
    def load_pretrained_model(self) -> bool:
        """Load pre-trained model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            self.is_trained = True
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict(self, log_message: str) -> Dict[str, any]:
        """Predict using actual ML model"""
        if not self.is_trained:
            # Try to load model first
            if not self.load_pretrained_model():
                raise ValueError("Model not available")
        
        # Vectorize the message
        X = self.vectorizer.transform([log_message])
        
        # Predict
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = float(max(probabilities))
        
        return {
            'predicted_level': prediction,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0'
        }
```

---

#### Step 1.2: Update `anomaly_detector.py`

**Current Issues**:
```python
# Line 134-150
# Learn normal patterns (rule-based)
self.normal_patterns = self.prepare_training_data(logs)
```

**Changes Needed**:
1. Remove rule-based pattern learning
2. Add ability to load `anomaly_detector_simple.pkl`
3. Update `detect_anomaly()` to use actual model
4. Keep threshold adjustment capability

**New Implementation**:
```python
import pickle
import os

class AnomalyDetector:
    def __init__(self):
        self.model = None  # Will hold RandomForest classifier
        self.vectorizer = None  # Will hold TF-IDF vectorizer
        self.is_trained = False
        self.threshold = 0.5  # Probability threshold for anomaly
        self.model_path = 'models/anomaly_detector_simple.pkl'
        self.vectorizer_path = 'models/vectorizer_simple.pkl'
    
    def load_pretrained_model(self) -> bool:
        """Load pre-trained model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            self.is_trained = True
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def detect_anomaly(self, log: Dict) -> Dict[str, any]:
        """Detect anomaly using actual ML model"""
        if not self.is_trained:
            if not self.load_pretrained_model():
                raise ValueError("Model not available")
        
        message = log.get('message', '')
        
        # Vectorize
        X = self.vectorizer.transform([message])
        
        # Predict
        prediction = self.model.predict(X)[0]  # 0=normal, 1=anomaly
        probabilities = self.model.predict_proba(X)[0]
        anomaly_score = float(probabilities[1])  # Probability of anomaly
        
        is_anomaly = anomaly_score > self.threshold
        
        return {
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': anomaly_score,
            'confidence': anomaly_score if is_anomaly else (1 - anomaly_score),
            'timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0'
        }
```

---

#### Step 1.3: Update `ml_service.py`

**Changes Needed**:
1. Ensure it loads models on initialization
2. Provide unified interface for predictions
3. Handle model loading failures gracefully

**New Implementation**:
```python
class MLService:
    def __init__(self, model_storage_path: str = "models/"):
        self.model_storage_path = model_storage_path
        self.log_classifier = LogClassifier()
        self.anomaly_detector = AnomalyDetector()
        self.is_initialized = False
    
    def initialize_models(self) -> bool:
        """Load all pre-trained models"""
        try:
            # Load log classifier
            classifier_loaded = self.log_classifier.load_pretrained_model()
            
            # Load anomaly detector
            anomaly_loaded = self.anomaly_detector.load_pretrained_model()
            
            self.is_initialized = classifier_loaded and anomaly_loaded
            
            if self.is_initialized:
                logger.info("✅ All ML models loaded successfully")
            else:
                logger.warning("⚠️ Some models failed to load")
            
            return self.is_initialized
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            return False
    
    def predict_log(self, log_message: str) -> Dict:
        """
        Run both classification and anomaly detection on a log message.
        This is the main interface for predictions.
        """
        if not self.is_initialized:
            self.initialize_models()
        
        # Run both models
        classification_result = self.log_classifier.predict(log_message)
        anomaly_result = self.anomaly_detector.detect_anomaly({'message': log_message})
        
        # Combine results
        return {
            'message': log_message,
            'predicted_level': classification_result['predicted_level'],
            'level_confidence': classification_result['confidence'],
            'is_anomaly': anomaly_result['is_anomaly'],
            'anomaly_score': anomaly_result['anomaly_score'],
            'severity': self._calculate_severity(
                classification_result['predicted_level'],
                anomaly_result['is_anomaly']
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_severity(self, level: str, is_anomaly: bool) -> str:
        """Calculate severity based on level and anomaly status"""
        if level in ['FATAL', 'ERROR'] and is_anomaly:
            return 'critical'
        elif level in ['FATAL', 'ERROR']:
            return 'high'
        elif level == 'WARN' and is_anomaly:
            return 'high'
        elif level == 'WARN':
            return 'medium'
        elif is_anomaly:
            return 'medium'
        else:
            return 'low'
```

---

### Phase 2: Deploy Models to Vercel

#### Step 2.1: Verify Deployment Size

**Check current size**:
```bash
cd engineering_log_intelligence
du -sh .
du -sh models/
```

**Expected**:
- Current deployment: ~5 MB
- Models directory: ~800 KB
- New deployment: ~6 MB (well under limits)

---

#### Step 2.2: Update `.vercelignore` (if needed)

Check if models are excluded:
```bash
cat .vercelignore
```

If `models/` is ignored, remove that line.

---

#### Step 2.3: Test Deployment

```bash
# Test build locally first
vercel build

# Check size
du -sh .vercel/

# Deploy to preview
vercel

# If successful, deploy to production
vercel --prod
```

---

### Phase 3: Update API Endpoints

#### Step 3.1: Update `/api/ml.py`

**Changes**:
1. Import and use `MLService`
2. Remove mock data generation
3. Use real model for predictions
4. Use real metadata for status

**New Implementation**:
```python
from external_services.ml.ml_service import MLService

# Initialize ML service (singleton pattern)
ml_service = MLService()
ml_service.initialize_models()

class handler(BaseHTTPRequestHandler):
    def handle_status(self):
        """Return actual ML model status"""
        # Load real metadata
        import json
        try:
            with open('models/metadata_simple.json', 'r') as f:
                metadata = json.load(f)
            
            return {
                "success": True,
                "models": {
                    "classification": {
                        "status": "active" if ml_service.is_initialized else "inactive",
                        "accuracy": metadata['classifier_accuracy'],
                        "trained_at": metadata['trained_at'],
                        "training_samples": metadata['num_training_samples']
                    },
                    "anomaly_detection": {
                        "status": "active" if ml_service.is_initialized else "inactive",
                        "accuracy": metadata['anomaly_detector_accuracy'],
                        "trained_at": metadata['trained_at']
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "models": {"status": "unavailable"}
            }
    
    def handle_analyze(self, data=None):
        """Use ML service for predictions"""
        if data and data.get('log_data'):
            log_data = data.get('log_data', [])
            results = []
            
            # Check database first
            conn = get_db_connection()
            if conn:
                # Try to get from database (existing flow)
                # ... database query code ...
                pass
            
            # If no database result, use ML service
            for log in log_data[:10]:
                try:
                    # Use real ML models
                    prediction = ml_service.predict_log(log.get('message', ''))
                    results.append({
                        "log_id": log.get('id'),
                        "classification": prediction['predicted_level'],
                        "confidence": prediction['level_confidence'],
                        "is_anomaly": prediction['is_anomaly'],
                        "anomaly_score": prediction['anomaly_score'],
                        "severity": prediction['severity'],
                        "timestamp": prediction['timestamp'],
                        "source": "ml_service_realtime"
                    })
                except Exception as e:
                    logger.error(f"ML prediction failed: {e}")
                    # Only use fallback if ML truly fails
                    results.append({
                        "log_id": log.get('id'),
                        "error": "ML service unavailable",
                        "source": "error"
                    })
            
            return {
                "success": True,
                "results": results,
                "total_analyzed": len(results)
            }
```

---

#### Step 3.2: Update `/api/ml_lightweight.py`

**Changes**:
1. Add fallback to ML service if database has no prediction
2. Store ML service predictions in database for future use

**New Implementation**:
```python
from external_services.ml.ml_service import MLService

ml_service = MLService()
ml_service.initialize_models()

class handler(BaseHTTPRequestHandler):
    def handle_analyze(self):
        """Query database first, use ML service as fallback"""
        conn = self.get_db_connection()
        
        if not conn:
            return {"error": "Database unavailable"}
        
        try:
            cursor = conn.cursor()
            
            # Get recent predictions from database
            cursor.execute("""
                SELECT ... FROM ml_predictions
                WHERE predicted_at > NOW() - INTERVAL '24 hours'
                LIMIT 100
            """)
            
            predictions = cursor.fetchall()
            
            # If we have predictions, return them
            if predictions:
                return {
                    "success": True,
                    "data": predictions,
                    "source": "database"
                }
            
            # Otherwise, use ML service to generate predictions
            # (This handles the "no predictions available" case)
            cursor.execute("""
                SELECT id, message FROM log_entries
                WHERE ... LIMIT 100
            """)
            logs = cursor.fetchall()
            
            results = []
            for log in logs:
                prediction = ml_service.predict_log(log['message'])
                
                # Store in database for future queries
                cursor.execute("""
                    INSERT INTO ml_predictions (
                        log_entry_id, predicted_level, level_confidence,
                        is_anomaly, anomaly_score, severity, predicted_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (
                    log['id'],
                    prediction['predicted_level'],
                    prediction['level_confidence'],
                    prediction['is_anomaly'],
                    prediction['anomaly_score'],
                    prediction['severity']
                ))
                
                results.append(prediction)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "data": results,
                "source": "ml_service_cached"
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            if conn:
                conn.close()
            return {"error": str(e)}
```

---

### Phase 4: Testing & Validation

#### Step 4.1: Local Testing

```bash
cd engineering_log_intelligence

# Test model loading
python3 -c "
from external_services.ml.ml_service import MLService
ml = MLService()
success = ml.initialize_models()
print(f'Models loaded: {success}')

# Test prediction
result = ml.predict_log('ERROR: Database connection failed')
print(f'Prediction: {result}')
"
```

**Expected Output**:
```
✅ All ML models loaded successfully
Models loaded: True
Prediction: {
    'predicted_level': 'ERROR',
    'level_confidence': 0.98,
    'is_anomaly': True,
    'anomaly_score': 0.87,
    'severity': 'critical'
}
```

---

#### Step 4.2: API Testing

```bash
# Test status endpoint
curl "https://your-app.vercel.app/api/ml?action=status" | python3 -m json.tool

# Should show REAL accuracy, not random
# Expected: "accuracy": 1.0 (not changing on each request)

# Test analyze endpoint
curl -X POST "https://your-app.vercel.app/api/ml?action=analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "log_data": [{
      "id": 123,
      "message": "ERROR: Database connection timeout"
    }]
  }' | python3 -m json.tool

# Should show "source": "ml_service_realtime"
```

---

#### Step 4.3: End-to-End Validation

**Checklist**:
- [ ] Models load successfully in Vercel
- [ ] `/api/ml?action=status` returns real accuracy (1.0 / 0.9785)
- [ ] Status accuracy doesn't change on refresh (not random)
- [ ] Predictions use actual ML models
- [ ] Predictions are stored in database
- [ ] Frontend displays predictions correctly
- [ ] No mock data anywhere
- [ ] Deployment size < 10 MB

---

## 📊 Before & After Comparison

### Before Integration

| Component | Status | Data Source |
|-----------|--------|-------------|
| `log_classifier.py` | ❌ Rule-based | Keyword matching |
| `anomaly_detector.py` | ❌ Rule-based | Pattern analysis |
| `ml_service.py` | ⚠️ Coordinator | Coordinates rule-based |
| API status | ❌ Mock | `random.uniform()` |
| API predictions | ⚠️ Mixed | Database OR mock |
| Deployment | ✅ 5 MB | No models |

### After Integration

| Component | Status | Data Source |
|-----------|--------|-------------|
| `log_classifier.py` | ✅ ML-based | `log_classifier_simple.pkl` |
| `anomaly_detector.py` | ✅ ML-based | `anomaly_detector_simple.pkl` |
| `ml_service.py` | ✅ Coordinator | Coordinates real ML |
| API status | ✅ Real | `metadata_simple.json` |
| API predictions | ✅ Real | ML service → Database |
| Deployment | ✅ ~6 MB | Includes models |

---

## 🎯 Success Criteria

Integration is complete when:

1. ✅ All API endpoints use `MLService`
2. ✅ No mock/random data generation
3. ✅ `log_classifier.py` uses scikit-learn models
4. ✅ `anomaly_detector.py` uses scikit-learn models
5. ✅ Models deployed to Vercel
6. ✅ Status endpoint shows real accuracy (1.0 / 0.9785)
7. ✅ Predictions come from trained models
8. ✅ All tests pass

---

## 🚨 Potential Issues & Solutions

### Issue 1: Import Errors in Vercel

**Problem**: Can't import `external_services.ml.ml_service`

**Solution**: Update Python path in API files:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from external_services.ml.ml_service import MLService
```

---

### Issue 2: Models Not Found

**Problem**: `FileNotFoundError: models/log_classifier_simple.pkl`

**Solution**: Use relative paths from project root:
```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(BASE_DIR, 'models', 'log_classifier_simple.pkl')
```

---

### Issue 3: Deployment Size Too Large

**Problem**: Deployment exceeds Vercel limits

**Solution**: 
1. Check actual size: `du -sh .vercel/`
2. If > 50MB, models too large - keep batch processing
3. If < 50MB, good to deploy

---

### Issue 4: Cold Start Slow

**Problem**: First request takes 3+ seconds

**Solution**: Model loading is one-time cost
- First request: ~2-3s (load models)
- Subsequent requests: ~100ms (models cached)
- This is acceptable for real-time predictions

---

## 📁 Files to Modify

### Must Modify (Core Integration)
1. `external-services/ml/log_classifier.py`
2. `external-services/ml/anomaly_detector.py`
3. `external-services/ml/ml_service.py`
4. `api/ml.py`

### Should Modify (Enhancement)
5. `api/ml_lightweight.py`

### May Modify (Optional)
6. `.vercelignore` (if models are excluded)
7. `vercel.json` (if function config needed)

---

## ⏱️ Time Estimates

| Phase | Task | Time |
|-------|------|------|
| 1.1 | Update `log_classifier.py` | 30 min |
| 1.2 | Update `anomaly_detector.py` | 30 min |
| 1.3 | Update `ml_service.py` | 20 min |
| 2 | Deploy models to Vercel | 20 min |
| 3.1 | Update `/api/ml.py` | 40 min |
| 3.2 | Update `/api/ml_lightweight.py` | 30 min |
| 4 | Testing & validation | 30 min |
| **Total** | | **3-4 hours** |

---

## 🚀 Ready to Start?

We can proceed with:

**Option A**: Step-by-step guided implementation
- I'll implement each file one at a time
- We'll test after each change
- Safe and methodical

**Option B**: Batch implementation
- I'll update all files at once
- Single deployment
- Faster but riskier

**Which approach would you prefer?**

---

**Next Step**: Awaiting your direction to begin implementation.

