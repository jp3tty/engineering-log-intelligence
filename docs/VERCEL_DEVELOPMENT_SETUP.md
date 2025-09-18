# Vercel Development Setup Guide

This guide walks you through setting up the Engineering Log Intelligence System for local development with Vercel.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/)
- **Vercel CLI** - Install with `npm install -g vercel`

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd engineering_log_intelligence

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env.local

# Edit the environment file with your settings
nano .env.local  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/engineering_logs

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Kafka
KAFKA_BROKERS=localhost:9092

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Vercel
VERCEL_TOKEN=your_vercel_token_here
```

### 3. Start External Services

```bash
# Start PostgreSQL, Elasticsearch, Kafka, and Redis
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f docker-compose.dev.yml ps
```

### 4. Initialize Database

```bash
# Run database migrations
python -m alembic upgrade head

# Or run the setup script
./scripts/setup-dev-simple.sh
```

### 5. Test the Setup

```bash
# Run all tests
python test_simple_api.py

# Run code quality checks
./scripts/check-code-quality.sh

# Test external services
python test_external_services.py
```

### 6. Start Development Server

```bash
# Start Vercel development server
vercel dev

# The API will be available at:
# http://localhost:3000/api/
```

## Development Workflow

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
black api/ tests/

# Check linting
flake8 api/ tests/

# Type checking
mypy api/

# Run all quality checks
./scripts/check-code-quality.sh
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

### API Development

The API is structured as Vercel Functions:

```
api/
├── health/          # Health check endpoints
├── logs/            # Log processing endpoints
├── auth/            # Authentication endpoints
├── dashboard/       # Dashboard data endpoints
├── ml/              # ML inference endpoints
└── utils/           # Shared utilities
```

Each function should:
- Be in its own directory
- Have a `main.py` or `index.py` file
- Include proper error handling
- Have type hints
- Include docstrings

### Frontend Development

The frontend is a Vue.js SPA:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Vercel-Specific Development

### Local Development

```bash
# Start Vercel development server
vercel dev

# This will:
# - Start local development server on port 3000
# - Hot reload on file changes
# - Simulate Vercel Functions environment
# - Use local environment variables
```

### Environment Management

Vercel supports multiple environments:

```bash
# Development environment
vercel env pull .env.local --environment=development

# Production environment
vercel env pull .env.production --environment=production
```

### Function Development

When developing Vercel Functions:

1. **Create function directory** in `api/`
2. **Add function file** (usually `index.py`)
3. **Test locally** with `vercel dev`
4. **Deploy** with `vercel deploy`

Example function structure:
```python
# api/health/check.py
from fastapi import FastAPI
from typing import Dict

app = FastAPI()

@app.get("/")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "engineering-log-intelligence"}
```

### Debugging

```bash
# Enable debug logging
export VERCEL_DEBUG=1
vercel dev

# View function logs
vercel logs

# View specific function logs
vercel logs --function=api/health/check
```

## Deployment

### Development Deployment

```bash
# Deploy to Vercel development
vercel

# This creates a preview deployment
# URL will be shown in terminal
```

### Production Deployment

```bash
# Deploy to production
vercel --prod

# Or use the CI/CD pipeline
git push origin main
```

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
vercel dev --port 3001
```

**2. Environment Variables Not Loading**
```bash
# Check if .env.local exists
ls -la .env.local

# Pull from Vercel
vercel env pull .env.local
```

**3. External Services Not Connecting**
```bash
# Check Docker services
docker-compose -f docker-compose.dev.yml ps

# Check service logs
docker-compose -f docker-compose.dev.yml logs elasticsearch
```

**4. Python Dependencies Issues**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

- Check the [Vercel Documentation](https://vercel.com/docs)
- Review [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Check project [README.md](../README.md)
- Review [Technical Architecture](TECHNICAL_ARCHITECTURE.md)

## Next Steps

After completing setup:

1. **Explore the API** - Visit `http://localhost:3000/api/health/check`
2. **Read the code** - Start with `api/health/check.py`
3. **Run tests** - Execute `pytest` to see what's tested
4. **Check documentation** - Review other docs in the `docs/` folder
5. **Start developing** - Pick a feature from the daily achievements log

## Development Tips

- **Use type hints** - They help catch errors early
- **Write tests** - They ensure your code works correctly
- **Follow code style** - Use Black and Flake8
- **Document functions** - Add docstrings to explain what code does
- **Test locally first** - Always test with `vercel dev` before deploying
- **Use environment variables** - Never hardcode secrets
- **Check logs** - Use `vercel logs` to debug issues

---

**Last Updated:** September 18, 2025  
**Version:** 1.0.0
