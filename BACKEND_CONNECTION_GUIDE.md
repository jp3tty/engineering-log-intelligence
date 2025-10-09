# Backend Connection Guide
## Connecting Frontend to Real Backend Services

This guide explains how to connect the Engineering Log Intelligence frontend to a real backend with database storage.

---

## Current Architecture

### What We Have Now:
- ✅ **Frontend**: Vue.js app deployed on Vercel (production-ready)
- ✅ **Mock Data**: JavaScript-generated simulated data
- ❌ **Backend**: API endpoints exist but not connected
- ❌ **Database**: PostgreSQL/Elasticsearch schemas defined but not running

### What Happens Currently:
1. Frontend tries: `http://localhost:3000/api/dashboard_analytics`
2. Request fails (CORS error / no backend running)
3. Falls back to: `getMockAnalyticsData()` in `frontend/src/services/analytics.js`
4. Returns: Algorithmically generated fake data

---

## Option 1: Vercel Serverless Functions (Recommended for Demo)

### Overview:
Use Vercel's built-in serverless functions - easiest deployment, no separate backend server needed.

### Steps:

#### 1. **Backend Already Exists!**
The API endpoints are already in the `api/` folder and configured for Vercel:
- `api/dashboard_analytics.py` - Dashboard data endpoint
- `api/logs.py` - Logs endpoint
- `api/analytics.py` - Analytics endpoint
- `api/health.py` - Health check endpoint

#### 2. **Update Frontend API Base URL**
Edit: `engineering_log_intelligence/frontend/src/services/analytics.js`

```javascript
// CHANGE THIS:
const analyticsAPI = axios.create({
  baseURL: 'http://localhost:3000',  // ❌ Wrong
  timeout: 10000,
  // ...
})

// TO THIS:
const analyticsAPI = axios.create({
  baseURL: '/api',  // ✅ Use Vercel's built-in routing
  timeout: 10000,
  // ...
})
```

#### 3. **Verify Vercel Configuration**
Check: `engineering_log_intelligence/vercel.json`

Should include:
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"
    }
  },
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ]
}
```

#### 4. **Deploy to Vercel**
```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence
vercel --prod
```

#### 5. **Test the Connection**
- Visit: `https://engineeringlogintelligence.vercel.app/api/dashboard_analytics`
- Should return JSON data (not a CORS error)
- Dashboard will now use this real API endpoint instead of mock data

### Pros:
✅ No separate server to manage  
✅ Auto-scales with traffic  
✅ Free tier available  
✅ Easy deployment  
✅ Already configured!

### Cons:
❌ Stateless (no persistent database connection)  
❌ Cold start delays  
❌ Limited to Vercel's supported databases

---

## Option 2: Separate Backend Server (For Production with Database)

### Overview:
Run a dedicated Python backend server that connects to PostgreSQL/Elasticsearch.

### Architecture:
```
Frontend (Vercel)
    ↓
Backend API (Railway/Render/Heroku)
    ↓
PostgreSQL (Supabase/Neon)
    ↓
Elasticsearch (Elastic Cloud)
```

### Steps:

#### 1. **Set Up Database (Choose One)**

**Option A: PostgreSQL on Supabase (Free)**
```bash
# 1. Sign up at https://supabase.com
# 2. Create a new project
# 3. Get connection string from Settings > Database
# Format: postgresql://user:pass@host:5432/database
```

**Option B: PostgreSQL on Neon (Free)**
```bash
# 1. Sign up at https://neon.tech
# 2. Create a new project
# 3. Get connection string
```

**Option C: Elasticsearch on Elastic Cloud (Free Trial)**
```bash
# 1. Sign up at https://cloud.elastic.co
# 2. Create deployment
# 3. Get connection details
```

#### 2. **Initialize Database Schema**
```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Connect to your PostgreSQL database
psql "postgresql://your_connection_string"

# Run the schema
\i external-services/postgresql/schema.sql
```

#### 3. **Create Backend Server File**
Create: `engineering_log_intelligence/backend_server.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import your existing API functions
from api.dashboard_analytics import handler as dashboard_handler

load_dotenv()

app = FastAPI(title="Engineering Log Intelligence API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://engineeringlogintelligence.vercel.app",
        "http://localhost:5173",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard_analytics")
async def get_dashboard_analytics():
    """Dashboard analytics endpoint"""
    # TODO: Connect to actual database here
    # For now, use existing mock data generator
    return dashboard_handler(type("Request", (), {"method": "GET"}))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-10-08"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
```

#### 4. **Update Requirements**
Edit: `engineering_log_intelligence/requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9  # PostgreSQL
elasticsearch==8.10.0    # Elasticsearch
sqlalchemy==2.0.23       # ORM
```

#### 5. **Deploy Backend to Railway (Free)**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence
railway init

# 4. Create Procfile
echo "web: python backend_server.py" > Procfile

# 5. Deploy
railway up

# 6. Get your backend URL
railway status
# Example: https://engineering-log-intelligence.railway.app
```

#### 6. **Update Frontend API Base URL**
Edit: `engineering_log_intelligence/frontend/src/services/analytics.js`

```javascript
const analyticsAPI = axios.create({
  baseURL: 'https://YOUR-BACKEND-URL.railway.app',
  timeout: 10000,
  // ...
})
```

#### 7. **Connect to Database in Backend**
Update: `backend_server.py`

```python
import psycopg2
from elasticsearch import Elasticsearch

# PostgreSQL connection
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

# Elasticsearch connection
ES_URL = os.getenv('ELASTICSEARCH_URL')
es = Elasticsearch([ES_URL])

@app.get("/api/dashboard_analytics")
async def get_dashboard_analytics():
    """Fetch real data from database"""
    cursor = conn.cursor()
    
    # Query real log data
    cursor.execute("""
        SELECT 
            COUNT(*) as total_logs,
            COUNT(*) FILTER (WHERE level = 'ERROR') as error_count,
            COUNT(*) FILTER (WHERE level = 'WARN') as warn_count,
            COUNT(*) FILTER (WHERE level = 'INFO') as info_count
        FROM logs
        WHERE timestamp > NOW() - INTERVAL '24 hours'
    """)
    
    result = cursor.fetchone()
    
    return {
        "logVolume": {...},  # Format data for frontend
        "systemMetrics": {
            "logsProcessed": result[0],
            "activeAlerts": result[1],
            // ...
        }
    }
```

#### 8. **Populate Database with Simulated Data**
```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence

# Run the data simulator
python -m data_simulation.simulator --count 10000
```

### Pros:
✅ Real database with persistent storage  
✅ Full control over backend logic  
✅ Can handle complex queries  
✅ Stateful connections

### Cons:
❌ More infrastructure to manage  
❌ Separate deployment process  
❌ May require paid tiers for production scale

---

## Option 3: Hybrid Approach (Best of Both Worlds)

### Architecture:
```
Frontend (Vercel)
    ↓
Vercel Serverless Functions (Simple queries)
    ↓
External Database (Supabase PostgreSQL)
    ↓
Background Workers (Railway - Complex processing)
```

### Setup:

#### 1. **Use Vercel Functions for API**
Keep the current `api/` folder structure

#### 2. **Connect Vercel to External Database**
Update: `api/dashboard_analytics.py`

```python
import os
import psycopg2

def handler(request):
    # Connect to Supabase PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    
    # Query real data
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs WHERE timestamp > NOW() - INTERVAL '24 hours'")
    log_count = cursor.fetchone()[0]
    
    # Return real data
    return {
        'statusCode': 200,
        'body': json.dumps({
            'systemMetrics': {
                'logsProcessed': log_count,
                // ...
            }
        })
    }
```

#### 3. **Add Database URL to Vercel Environment**
```bash
# In Vercel dashboard:
# Settings > Environment Variables
# Add: DATABASE_URL = postgresql://your_connection_string
```

#### 4. **Update requirements-vercel.txt**
```txt
fastapi==0.104.1
pydantic==2.5.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9  # Add this
```

### Pros:
✅ Simple API deployment (Vercel)  
✅ Real database storage  
✅ Cost-effective  
✅ Scalable

---

## Quick Start: Get Backend Working in 10 Minutes

**For immediate demo with simulated data:**

### Step 1: Fix API Base URL
```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence/frontend/src/services
```

Edit `analytics.js`:
```javascript
// Change line 21:
baseURL: '/api',  // Instead of 'http://localhost:3000'
```

### Step 2: Deploy
```bash
cd /Users/jeremypetty/Documents/projects/tools_developer/engineering_log_intelligence
vercel --prod
```

### Step 3: Test
Visit: `https://engineeringlogintelligence.vercel.app/api/dashboard_analytics`

**Done!** The dashboard now uses Vercel serverless functions instead of local mock data.

---

## Comparison Table

| Feature | Mock Data (Current) | Vercel Functions | Separate Backend | Hybrid |
|---------|-------------------|------------------|------------------|--------|
| **Setup Time** | ✅ 0 min (done) | ⚡ 10 min | ⏱️ 1-2 hours | ⏱️ 1 hour |
| **Cost** | 💰 Free | 💰 Free | 💰 $5-20/mo | 💰 Free-$10/mo |
| **Real Data** | ❌ No | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **Scalability** | ✅ Infinite | ⚡ Auto | 🔧 Manual | ✅ Good |
| **Complexity** | ✅ Simple | ✅ Simple | 🔧 Complex | ⚡ Moderate |
| **Database** | ❌ None | ⚠️ External only | ✅ Full control | ✅ External |

---

## Recommended Path Forward

### For Portfolio Demo:
➡️ **Use Option 1: Vercel Serverless Functions**
- Quick to implement (10 minutes)
- Professional appearance
- Shows full-stack capability
- No extra costs

### For Production Application:
➡️ **Use Option 3: Hybrid Approach**
- Best balance of simplicity and capability
- Real database storage
- Cost-effective
- Production-ready

### Next Steps:
1. Choose your approach
2. Follow the steps above
3. Test the connection
4. Populate with realistic data
5. Update documentation

---

## Need Help?

Common issues and solutions:

**CORS Errors:**
- Make sure backend has `Access-Control-Allow-Origin: *` header
- Check that API base URL is correct

**Connection Refused:**
- Verify backend is running
- Check firewall/network settings
- Confirm URL is accessible

**Database Connection Failed:**
- Verify connection string
- Check environment variables
- Ensure database is running and accessible

---

**Created**: October 8, 2025  
**Author**: Engineering Log Intelligence Team  
**Status**: Ready for Implementation

