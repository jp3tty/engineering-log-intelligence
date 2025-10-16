# Business Severity ML Design

**Date**: October 16, 2025  
**Goal**: Predict business impact severity beyond simple log levels  
**Why**: Log levels (INFO, ERROR) don't indicate actual business impact

---

## 🎯 The Problem

**Current State**:
```
Server: "ERROR: Test database connection failed"
ML:     "Predicted level: ERROR" ← Redundant! We already know it's ERROR
Value:  None ❌
```

**New Approach**:
```
Server: "ERROR: Test database connection failed"
ML:     "Business Severity: LOW" ← Because it's just a test database
Value:  Actionable insight! ✅

Server: "ERROR: Payment processor connection failed"  
ML:     "Business Severity: CRITICAL" ← Revenue impacting!
Value:  Immediate alert to on-call! ✅
```

---

## 📊 Severity Classification System

### Severity Levels

**CRITICAL** - Immediate revenue/security impact
- Payment system failures
- Auth system down
- Data breach indicators
- Customer-facing service outages during peak hours

**HIGH** - Significant business impact
- Core API failures
- Database connection issues in production
- High error rates (>5% of requests)
- Security warnings with potential exploit

**MEDIUM** - Operational concern
- Performance degradation
- Non-critical service issues
- Elevated error rates (1-5%)
- Resource warnings (CPU, memory)

**LOW** - Informational/minimal impact
- Test environment issues
- Debug logging
- Health check failures
- Cache misses
- Non-production errors

---

## 🧮 Severity Calculation Factors

### Primary Factors (High Weight)

1. **Service Criticality**
   ```python
   CRITICAL_SERVICES = ['payment-api', 'auth-service', 'checkout-api']
   HIGH_PRIORITY_SERVICES = ['user-api', 'order-api', 'inventory-api']
   MEDIUM_PRIORITY_SERVICES = ['notification-service', 'analytics-api']
   LOW_PRIORITY_SERVICES = ['test-service', 'dev-sandbox', 'health-check']
   ```

2. **Error Type**
   ```python
   CRITICAL_ERRORS = [
       'payment failed', 'transaction declined', 'unauthorized access',
       'data breach', 'sql injection', 'authentication bypass'
   ]
   HIGH_ERRORS = [
       'database connection failed', 'timeout', 'service unavailable',
       'connection refused', 'out of memory'
   ]
   MEDIUM_ERRORS = [
       'slow response', 'cache miss', 'retry limit exceeded',
       'validation error', 'rate limit exceeded'
   ]
   LOW_ERRORS = [
       'debug', 'test failed', 'health check', 'info'
   ]
   ```

3. **Log Level**
   ```python
   FATAL/ERROR + critical service → Likely CRITICAL
   WARN + critical service → Likely HIGH
   ERROR + low priority service → Likely MEDIUM
   INFO → Usually LOW (unless specific keywords)
   ```

### Secondary Factors (Medium Weight)

4. **Endpoint Criticality**
   ```python
   CRITICAL_ENDPOINTS = ['/checkout', '/payment', '/login', '/authorize']
   HIGH_ENDPOINTS = ['/api/orders', '/api/users', '/api/cart']
   MEDIUM_ENDPOINTS = ['/api/products', '/api/search']
   LOW_ENDPOINTS = ['/health', '/metrics', '/ping', '/test']
   ```

5. **Time Context**
   ```python
   PEAK_HOURS = [9-17]  # Business hours - increase severity
   OFF_HOURS = [0-6, 22-23]  # Night time - decrease severity
   WEEKEND = [Saturday, Sunday]  # Lower traffic - decrease severity
   ```

### Tertiary Factors (Low Weight)

6. **Error Pattern**
   - Isolated error → Lower severity
   - Repeated error (>10 in 5 min) → Higher severity
   - Cascade failure pattern → Higher severity

7. **User Impact**
   - Single user → Lower severity
   - Multiple users → Higher severity
   - All users → Critical severity

---

## 🔧 Implementation Approach

### Phase 1: Create Training Labels

We'll create severity labels using rule-based logic first:

```python
def calculate_business_severity(log: Dict) -> str:
    """
    Calculate business severity based on multiple factors.
    This becomes our training label.
    """
    score = 0
    
    # Factor 1: Service criticality (0-40 points)
    service = log.get('source_type', '').lower()
    if any(s in service for s in ['payment', 'auth', 'checkout']):
        score += 40
    elif any(s in service for s in ['user', 'order', 'inventory']):
        score += 30
    elif any(s in service for s in ['notification', 'analytics']):
        score += 20
    else:
        score += 10
    
    # Factor 2: Log level (0-30 points)
    level = log.get('level', '').upper()
    if level == 'FATAL':
        score += 30
    elif level == 'ERROR':
        score += 25
    elif level == 'WARN':
        score += 15
    else:
        score += 5
    
    # Factor 3: Message content (0-20 points)
    message = log.get('message', '').lower()
    if any(kw in message for kw in ['payment failed', 'breach', 'unauthorized']):
        score += 20
    elif any(kw in message for kw in ['connection failed', 'timeout', 'unavailable']):
        score += 15
    elif any(kw in message for kw in ['slow', 'degraded', 'retry']):
        score += 10
    else:
        score += 5
    
    # Factor 4: Endpoint (0-10 points)
    endpoint = log.get('endpoint', '').lower()
    if any(ep in endpoint for ep in ['/checkout', '/payment', '/login']):
        score += 10
    elif any(ep in endpoint for ep in ['/orders', '/users', '/cart']):
        score += 7
    elif any(ep in endpoint for ep in ['/health', '/ping', '/test']):
        score += 1
    else:
        score += 5
    
    # Convert score to severity (0-100 scale)
    if score >= 80:
        return 'critical'
    elif score >= 60:
        return 'high'
    elif score >= 40:
        return 'medium'
    else:
        return 'low'
```

### Phase 2: Train ML Model

```python
# In train_models_simple.py

# Instead of predicting log level:
# y = [row['level'] for row in data]  ❌

# Predict business severity:
y = [calculate_business_severity(row) for row in data]  ✅

# Train classifier
classifier = RandomForestClassifier(n_estimators=100)
classifier.fit(X_tfidf, y)

# Now the model learns patterns beyond our rules!
```

### Phase 3: ML Learns Beyond Rules

The ML model will learn patterns we didn't explicitly code:

```python
# ML might discover:
"Transaction processing took longer than expected"
→ Often precedes payment failures
→ Should be HIGH severity (even though it's just INFO level)

"Cache warming completed"
→ Always harmless
→ Should be LOW severity (even in critical services)
```

---

## 📈 Training Data Strategy

### Step 1: Label Existing Logs

```python
# Process all 30,000 logs in database
import psycopg2

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Fetch logs
cursor.execute("SELECT * FROM log_entries LIMIT 10000")
logs = cursor.fetchall()

# Generate severity labels
labeled_data = []
for log in logs:
    severity = calculate_business_severity(log)
    labeled_data.append({
        'message': log['message'],
        'severity': severity,
        'original_level': log['level'],
        'source': log['source_type']
    })

# Save for training
import json
with open('training_data_severity.json', 'w') as f:
    json.dump(labeled_data, f)
```

### Step 2: Validate Labels

Check that severity makes sense:

```python
# Review distribution
from collections import Counter
severity_dist = Counter([d['severity'] for d in labeled_data])
print(severity_dist)

# Expected healthy distribution:
# low: 60-70% (most logs are routine)
# medium: 20-25%
# high: 8-12%
# critical: 1-3% (rare but important)
```

### Step 3: Train Model

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

messages = [d['message'] for d in labeled_data]
severities = [d['severity'] for d in labeled_data]

# Vectorize
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(messages)

# Train
model = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced'  # Important! Critical logs are rare
)
model.fit(X, severities)

# Save
import pickle
with open('models/severity_classifier.pkl', 'wb') as f:
    pickle.dump(model, f)
```

---

## 🧪 Testing & Validation

### Test Cases

```python
test_cases = [
    {
        'message': 'Payment processor connection timeout',
        'expected': 'critical',
        'reason': 'Revenue impacting'
    },
    {
        'message': 'Test database connection failed',
        'expected': 'low',
        'reason': 'Non-production environment'
    },
    {
        'message': 'User API response time degraded to 2s',
        'expected': 'medium',
        'reason': 'Performance issue in important service'
    },
    {
        'message': 'Health check endpoint returned 200 OK',
        'expected': 'low',
        'reason': 'Routine informational log'
    },
    {
        'message': 'Unauthorized access attempt detected from IP 1.2.3.4',
        'expected': 'high',
        'reason': 'Security concern'
    }
]

# Run predictions
for test in test_cases:
    X = vectorizer.transform([test['message']])
    predicted = model.predict(X)[0]
    match = '✅' if predicted == test['expected'] else '❌'
    print(f"{match} '{test['message']}'")
    print(f"   Expected: {test['expected']}, Got: {predicted}")
    print(f"   Reason: {test['reason']}\n")
```

---

## 🔄 Updated Architecture

### Old Flow (Redundant)
```
Log Entry (level=ERROR) 
    ↓
ML Prediction: "ERROR" 
    ↓
Value: None ❌
```

### New Flow (Valuable)
```
Log Entry (level=ERROR, message="Payment timeout", service="payment-api")
    ↓
ML Severity Predictor
    ↓
{
    "original_level": "ERROR",
    "business_severity": "CRITICAL",
    "confidence": 0.94,
    "recommended_action": "Alert on-call immediately"
}
    ↓
Value: Actionable intelligence! ✅
```

---

## 🎯 Success Metrics

### Model Performance
- **Accuracy**: >85% overall
- **Critical recall**: >95% (can't miss critical issues!)
- **Low precision**: >80% (don't want false alarms)

### Business Impact
- Reduce alert fatigue by 50% (fewer low-severity alerts)
- Faster response to critical issues (automatic escalation)
- Better resource allocation (route to right team)

---

## 📋 Implementation Checklist

### Phase 1: Design & Labeling (1 hour)
- [x] Define severity levels
- [x] Design severity calculation rules
- [ ] Create severity labeling function
- [ ] Label training data
- [ ] Validate label distribution

### Phase 2: Model Training (1 hour)
- [ ] Update train_models_simple.py
- [ ] Train severity classifier
- [ ] Evaluate on test set
- [ ] Save model artifacts

### Phase 3: Integration (1.5 hours)
- [ ] Update LogClassifier to predict severity
- [ ] Keep anomaly detection as-is
- [ ] Update API responses
- [ ] Update database schema (if needed)

### Phase 4: Testing (30 min)
- [ ] Unit tests for severity predictions
- [ ] Integration tests
- [ ] Manual validation with real logs
- [ ] Deploy to production

**Total Time: ~4 hours**

---

## 🚀 Next Steps

1. **Immediate**: Create severity labeling function
2. **Next**: Generate labeled training data
3. **Then**: Train new model
4. **Finally**: Integrate and deploy

Ready to proceed?

