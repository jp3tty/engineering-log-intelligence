# Data Overview for ML Training

**Created:** October 11, 2025  
**Purpose:** Understanding your log data before ML enablement  
**Audience:** Data scientists, ML engineers, developers

## 🎯 Quick Summary

Your system generates **three types of realistic enterprise logs** that are perfect for ML training:

1. **SPLUNK Logs** (40% of data) - System and infrastructure logs
2. **SAP Transaction Logs** (30% of data) - Business transaction logs  
3. **Application Logs** (30% of data) - Web application and API logs

**Total Data Generation Capacity:** 60,000+ logs per second  
**Built-in Anomalies:** 5% of all logs (configurable)  
**Date Range:** Logs generated daily via GitHub Actions (1,000 logs/day)

---

## 📊 Data Structure Overview

### Common Fields (All Log Types)

Every log entry shares these core fields:

| Field | Type | Description | ML Importance |
|-------|------|-------------|---------------|
| `log_id` | string | Unique identifier | 🔹 ID/Index |
| `timestamp` | datetime | When log was created | ⭐⭐⭐ Time-series features |
| `level` | string | Log severity (DEBUG/INFO/WARN/ERROR/FATAL) | ⭐⭐⭐ Target variable |
| `message` | text | Human-readable message | ⭐⭐⭐ NLP features |
| `category` | string | Log category | ⭐⭐ Categorical feature |
| `tags` | array | Classification tags | ⭐⭐ Multi-label |
| `metadata` | json | Source-specific details | ⭐⭐⭐ Feature-rich |

---

## 1️⃣ SPLUNK Logs (System & Infrastructure)

### What They Are
SPLUNK logs represent **system-level events** from:
- Windows Event Logs (Security, System, Application)
- Web Servers (Apache, IIS)
- System logs (Syslog)

### Sample SPLUNK Log
```json
{
  "log_id": "splunk-1728662400-000001",
  "timestamp": "2025-10-11T14:30:45.123Z",
  "level": "INFO",
  "message": "[4624] User login successful - DOMAIN\\user123@WEBSERVER-01",
  "raw_log": "[4624] User login successful - DOMAIN\\user123@WEBSERVER-01",
  "category": "security",
  "tags": ["splunk", "windows", "security", "authentication"],
  "metadata": {
    "generator": "splunk",
    "source": "WinEventLog:Security",
    "sourcetype": "WinEventLog:Security",
    "host": "webserver-01",
    "event_id": "4624",
    "event_type": "login_success",
    "user": "user123",
    "computer": "WEBSERVER-01",
    "domain": "DOMAIN"
  }
}
```

### Key Features for ML

**Categorical Features:**
- `source` - 8 types (WinEventLog:Security, apache_access, syslog, etc.)
- `event_type` - Events like login_success, service_start, http_request
- `host` - Server hostname (6 different servers)
- `level` - 5 levels (DEBUG, INFO, WARN, ERROR, FATAL)

**Numerical Features:**
- `event_id` - Windows event codes (1000-9999)
- `status` - HTTP status codes (200, 404, 500, etc.)
- `response_size` - Bytes transferred

**Text Features:**
- `message` - Rich text for NLP
- `raw_log` - Original log format
- `user_agent` - Browser/client info (for web logs)

**Anomaly Types (6 types):**
1. System Failure (FATAL) - Multiple services down
2. Security Breach (FATAL) - Unauthorized access attempts
3. Performance Degradation (WARN) - Slow response times
4. Data Corruption (ERROR) - Data integrity issues
5. Network Anomaly (WARN) - Unusual traffic patterns
6. Resource Exhaustion (ERROR) - Low memory/disk/CPU

---

## 2️⃣ SAP Transaction Logs (Business Operations)

### What They Are
SAP logs represent **business transactions** from enterprise resource planning systems:
- Financial operations (payments, invoices)
- Sales orders and quotes
- Purchase orders
- Inventory movements
- HR operations (payroll, leave)
- System administration

### Sample SAP Log
```json
{
  "log_id": "sap-1728662400-000001",
  "timestamp": "2025-10-11T14:30:45.123Z",
  "level": "INFO",
  "message": "Sales order 1234567 created for customer C100001 - $45,234.50",
  "raw_log": "20251011143045|VA01|I|3|Sales order 1234567 created for customer C100001",
  "category": "sap_transaction",
  "tags": ["sap", "sales", "erp"],
  "metadata": {
    "generator": "sap",
    "transaction_type": "sales",
    "transaction_code": "VA01",
    "sap_system": "ERP_PROD",
    "sap_client": "100",
    "sap_server": "sap-erp-01",
    "sap_message_type": "I",
    "sap_severity": "3",
    "order_value": 45234.50,
    "customer_id": "C100001",
    "sales_document": "1234567",
    "material_number": "M789012",
    "currency": "USD"
  }
}
```

### Key Features for ML

**Categorical Features:**
- `transaction_type` - 8 types (financial, sales, purchase, inventory, hr, system, security, performance)
- `transaction_code` - Real SAP T-codes (VA01, FB01, ME21N, etc.)
- `sap_system` - 8 systems (ERP_PROD, CRM_PROD, SCM_PROD, etc.)
- `sap_message_type` - S/I/W/E/A/X (Success/Info/Warning/Error/Abort/Exit)
- `sap_client` - SAP client number

**Numerical Features:**
- `order_value` / `po_value` / `amount` - Transaction amounts ($100 - $1,000,000)
- `sap_severity` - 1-8 scale
- `quantity` - Item quantities
- `response_time` - Transaction response time

**Text Features:**
- `message` - Business-readable transaction description
- `customer_id` / `vendor_id` - Business entity IDs
- `material_number` - Product/material codes

**Anomaly Types (6 types):**
1. Failed Transaction (ERROR) - Database constraint violations
2. Security Violation (FATAL) - Unauthorized access
3. Performance Issue (WARN) - Slow transactions (>5 seconds)
4. Data Integrity Error (ERROR) - Inconsistent data
5. System Error (FATAL) - System failures
6. Business Rule Violation (WARN) - Policy violations

---

## 3️⃣ Application Logs (Web & API)

### What They Are
Application logs represent **web application and API activity**:
- HTTP requests and responses
- API endpoints
- Authentication events
- Performance metrics
- Application errors

### Sample Application Log
```json
{
  "log_id": "application-1728662400-000001",
  "timestamp": "2025-10-11T14:30:45.123Z",
  "level": "INFO",
  "message": "GET /api/users - 200 - 145.67ms",
  "category": "application",
  "tags": ["application", "web_app", "api"],
  "metadata": {
    "generator": "application",
    "application_type": "web_app",
    "framework": "Spring Boot",
    "host": "web-server-01",
    "service": "webapp",
    "http_method": "GET",
    "http_status": 200,
    "endpoint": "/api/users",
    "response_time_ms": 145.67,
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "sess_123456_7890",
    "correlation_id": "corr_1728662400_1234",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  }
}
```

### Key Features for ML

**Categorical Features:**
- `application_type` - 8 types (web_app, microservice, api_gateway, etc.)
- `framework` - Technology stack (Spring Boot, Django, FastAPI, etc.)
- `http_method` - GET, POST, PUT, DELETE, PATCH
- `http_status` - 200, 201, 400, 401, 404, 500, 502, 503, etc.
- `endpoint` - API paths (/api/users, /auth/login, etc.)

**Numerical Features:**
- `response_time_ms` - Response time in milliseconds (1-10,000)
- `http_status` - HTTP status code
- `memory_usage_mb` - Memory usage (50-1000 MB)
- `cpu_usage_percent` - CPU usage (10-100%)
- `thread_count` - Active threads (10-100)

**Text Features:**
- `message` - HTTP request summary
- `endpoint` - URL path
- `user_agent` - Client browser/device info
- `ip_address` - Client IP address

**Anomaly Types (6 types):**
1. Unusual Response Time (WARN) - Response >5 seconds
2. High Error Rate (ERROR) - >10% errors
3. Unusual Traffic Pattern (WARN) - Suspicious activity
4. Resource Exhaustion (ERROR) - High memory/CPU
5. Security Incident (FATAL) - Failed auth attempts
6. Data Corruption (ERROR) - Data integrity issues

---

## 🎯 ML Training Considerations

### Data Volume Recommendations

| Purpose | Minimum Logs | Recommended | Optimal |
|---------|-------------|-------------|---------|
| Basic Testing | 1,000 | 5,000 | 10,000 |
| Development | 5,000 | 10,000 | 50,000 |
| Production | 10,000 | 50,000 | 100,000+ |

**Current Status:** You have automated daily log generation (1,000 logs/day), so:
- Week 1: 7,000 logs ✅ Good for basic training
- Week 2: 14,000 logs ✅ Good for development
- Month 1: 30,000 logs ✅ Ready for production

### Feature Engineering Opportunities

#### 1. **Text Features (NLP)**
- `message` field → TF-IDF, word embeddings, sentiment analysis
- Extract patterns: error codes, IP addresses, user IDs
- Named entity recognition for business data

#### 2. **Time-Series Features**
- Hour of day, day of week, month
- Time since last event
- Event frequency (logs per minute/hour)
- Rolling averages of response times

#### 3. **Categorical Encoding**
- One-hot encoding for low cardinality (http_method, level)
- Label encoding for high cardinality (host, service)
- Target encoding for transaction types

#### 4. **Numerical Features**
- Response time statistics (mean, median, std)
- Log counts per time window
- Anomaly scores
- Resource utilization metrics

#### 5. **Derived Features**
- Error rate (errors / total logs)
- Success rate (2xx status / total requests)
- Anomaly density (anomalies per time window)
- Cross-log correlation (same request_id, correlation_id)

### Class Distribution

**Log Levels (Target Variable for Classification):**
- INFO: ~70% (normal operations)
- WARN: ~15% (warnings, anomalies)
- ERROR: ~4% (errors)
- DEBUG: ~10% (debug info)
- FATAL: ~1% (critical failures)

**Anomaly Distribution:**
- Normal logs: ~95%
- Anomalous logs: ~5%

**Important:** This is a **class imbalance** problem. Use techniques like:
- SMOTE for oversampling
- Class weights in model training
- Precision-recall optimization instead of accuracy

---

## 🔍 Data Quality Characteristics

### Strengths ✅

1. **Realistic Format:** Matches real enterprise log formats
2. **Rich Metadata:** Extensive metadata for feature extraction
3. **Diverse Sources:** 3 distinct log types with different patterns
4. **Anomaly Simulation:** Built-in anomalies for supervised learning
5. **Correlation Fields:** `request_id`, `correlation_id` for cross-log analysis
6. **Temporal Consistency:** Proper timestamps for time-series analysis

### Considerations ⚠️

1. **Synthetic Data:** Generated, not real production logs
   - **Impact:** May not capture all real-world edge cases
   - **Mitigation:** Regular model updates with production data

2. **Fixed Distributions:** Anomaly rate is fixed at 5%
   - **Impact:** Real systems may have different rates
   - **Mitigation:** Configurable anomaly rates, adjustable thresholds

3. **Limited Diversity:** Fixed set of hosts, services, endpoints
   - **Impact:** Model may not generalize to new services
   - **Mitigation:** Expand generator configurations over time

---

## 📈 Recommended ML Models

### 1. **Log Classification**
**Task:** Predict log level (INFO, WARN, ERROR, etc.)

**Recommended Models:**
- **Logistic Regression:** Baseline, fast, interpretable
- **Random Forest:** Good with mixed features, handles non-linearity
- **XGBoost:** Best performance, handles class imbalance
- **LSTM/Transformer:** For sequential patterns (advanced)

**Features to Use:**
- Text: TF-IDF of `message` field
- Categorical: `source`, `transaction_type`, `http_method`
- Numerical: `response_time_ms`, `http_status`
- Temporal: hour of day, day of week

### 2. **Anomaly Detection**
**Task:** Identify anomalous logs (binary classification)

**Recommended Models:**
- **Isolation Forest:** Unsupervised, good baseline
- **One-Class SVM:** Robust to outliers
- **Autoencoder:** Deep learning, captures complex patterns
- **LSTM Autoencoder:** For sequential anomalies (advanced)

**Features to Use:**
- Statistical: response time deviation, error rate
- Behavioral: unusual IP addresses, rare endpoints
- Temporal: events at unusual times
- Cross-log: correlation with other anomalies

### 3. **Log Correlation**
**Task:** Group related logs across systems

**Recommended Models:**
- **Clustering:** K-Means, DBSCAN for grouping
- **Graph Neural Networks:** For complex relationships (advanced)
- **Sequence Models:** For temporal correlation

**Features to Use:**
- Correlation IDs: `request_id`, `session_id`, `correlation_id`
- Temporal proximity: logs within time windows
- Content similarity: similar error messages, patterns

---

## 🚀 Next Steps for ML Enablement

### Step 1: Data Verification (15 minutes)
```bash
# Check database connection
python check_database.py

# Verify log count
# Aim for 1,000+ logs minimum for basic training
```

### Step 2: Data Exploration (30 minutes)
```python
# Load data into pandas
import pandas as pd
import psycopg2

# Connect and query
df = pd.read_sql("SELECT * FROM log_entries LIMIT 10000", conn)

# Explore distribution
print(df['level'].value_counts())
print(df['metadata'].apply(lambda x: x['generator']).value_counts())
print(df['timestamp'].min(), df['timestamp'].max())
```

### Step 3: Feature Engineering (1-2 hours)
```python
# Extract features from metadata
df['generator'] = df['metadata'].apply(lambda x: x.get('generator'))
df['http_status'] = df['metadata'].apply(lambda x: x.get('http_status', 0))
df['response_time'] = df['metadata'].apply(lambda x: x.get('response_time_ms', 0))

# Text features
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(max_features=1000)
X_text = vectorizer.fit_transform(df['message'])

# Combine features
import numpy as np
X = np.hstack([X_text.toarray(), df[['http_status', 'response_time']]])
y = df['level']
```

### Step 4: Model Training (1-2 hours)
```python
# Train classification model
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier(n_estimators=100, class_weight='balanced')
model.fit(X_train, y_train)

# Evaluate
from sklearn.metrics import classification_report
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
```

---

## 📚 Additional Resources

- **[ML Enablement Guide](ML_ENABLEMENT_GUIDE.md)** - Step-by-step ML activation
- **[Data Schema Design](DATA_SCHEMA_DESIGN.md)** - Complete database schema
- **[SPLUNK Log Schema](SPLUNK_LOG_SCHEMA.md)** - Detailed SPLUNK structure
- **[SAP Log Schema](SAP_LOG_SCHEMA.md)** - Detailed SAP structure
- **[Application Log Schema](APPLICATION_LOG_SCHEMA.md)** - Detailed application structure

---

**Last Updated:** October 11, 2025  
**Ready for:** ML Training and Feature Engineering  
**Next Step:** Follow the ML Enablement Guide to train your first models!

