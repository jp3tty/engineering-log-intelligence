# Troubleshooting Guide

This guide helps you resolve common issues when developing with the Engineering Log Intelligence System.

## Quick Diagnostics

Run these commands to quickly diagnose issues:

```bash
# Check system status
./scripts/check-code-quality.sh

# Test external services
python test_external_services.py

# Test API functions
python test_simple_api.py

# Check Vercel status
vercel --version
```

## Common Issues and Solutions

### 1. Python Environment Issues

**Problem:** `python: command not found` or wrong Python version

**Solution:**
```bash
# Check Python version
python --version

# If not 3.12+, install correct version
# macOS with Homebrew:
brew install python@3.12

# Or download from python.org
# Then recreate virtual environment:
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** `pip: command not found`

**Solution:**
```bash
# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# Or use ensurepip
python -m ensurepip --upgrade
```

### 2. Virtual Environment Issues

**Problem:** Dependencies not installing or import errors

**Solution:**
```bash
# Deactivate current environment
deactivate

# Remove and recreate
rm -rf venv
python -m venv venv
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Problem:** Virtual environment not activating

**Solution:**
```bash
# Check if venv exists
ls -la venv/

# If missing, recreate
python -m venv venv

# Activate (try different methods)
source venv/bin/activate
# OR
. venv/bin/activate
# OR (Windows)
venv\Scripts\activate
```

### 3. Docker Issues

**Problem:** `docker: command not found`

**Solution:**
- Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
- Start Docker Desktop application
- Verify with `docker --version`

**Problem:** `docker-compose: command not found`

**Solution:**
```bash
# Install docker-compose
# macOS with Homebrew:
brew install docker-compose

# Or use Docker Desktop (includes docker-compose)
```

**Problem:** External services not starting

**Solution:**
```bash
# Check Docker is running
docker ps

# Check service logs
docker-compose -f docker-compose.dev.yml logs

# Restart services
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

# Check specific service
docker-compose -f docker-compose.dev.yml logs elasticsearch
```

### 4. Vercel Issues

**Problem:** `vercel: command not found`

**Solution:**
```bash
# Install Vercel CLI
npm install -g vercel

# Verify installation
vercel --version
```

**Problem:** `vercel dev` not working

**Solution:**
```bash
# Check if you're in the right directory
pwd
# Should be: .../engineering_log_intelligence

# Check for vercel.json
ls -la vercel.json

# Try with debug mode
VERCEL_DEBUG=1 vercel dev

# Check logs
vercel logs
```

**Problem:** Environment variables not loading

**Solution:**
```bash
# Check .env.local exists
ls -la .env.local

# Pull from Vercel
vercel env pull .env.local

# Check environment variables
vercel env ls
```

### 5. Database Connection Issues

**Problem:** `psycopg2` installation fails

**Solution:**
```bash
# Install system dependencies first
# macOS:
brew install postgresql

# Ubuntu/Debian:
sudo apt-get install libpq-dev

# Then install Python package
pip install psycopg2-binary
```

**Problem:** Database connection refused

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:password@localhost:5432/engineering_logs')
print('Connected successfully')
conn.close()
"
```

### 6. Elasticsearch Issues

**Problem:** Elasticsearch connection refused

**Solution:**
```bash
# Check if Elasticsearch is running
docker-compose -f docker-compose.dev.yml ps elasticsearch

# Check Elasticsearch logs
docker-compose -f docker-compose.dev.yml logs elasticsearch

# Test connection
curl http://localhost:9200

# Reset Elasticsearch
docker-compose -f docker-compose.dev.yml restart elasticsearch
```

**Problem:** Elasticsearch cluster not ready

**Solution:**
```bash
# Wait for cluster to be ready
curl -X GET "localhost:9200/_cluster/health?wait_for_status=yellow&timeout=30s"

# Check cluster status
curl -X GET "localhost:9200/_cluster/health"
```

### 7. Kafka Issues

**Problem:** Kafka connection refused

**Solution:**
```bash
# Check if Kafka is running
docker-compose -f docker-compose.dev.yml ps kafka

# Check Kafka logs
docker-compose -f docker-compose.dev.yml logs kafka

# Test connection
python -c "
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
print('Connected successfully')
producer.close()
"
```

### 8. Code Quality Issues

**Problem:** Black formatting fails

**Solution:**
```bash
# Check Black version
black --version

# Update Black
pip install --upgrade black

# Format code
black api/ tests/

# Check configuration
cat pyproject.toml
```

**Problem:** Flake8 linting errors

**Solution:**
```bash
# Check Flake8 version
flake8 --version

# Update Flake8
pip install --upgrade flake8

# Run with specific rules
flake8 api/ --ignore=E203,W503

# Check configuration
cat .flake8
```

**Problem:** MyPy type checking errors

**Solution:**
```bash
# Check MyPy version
mypy --version

# Update MyPy
pip install --upgrade mypy

# Run with verbose output
mypy api/ --verbose

# Check configuration
cat pyproject.toml
```

### 9. Testing Issues

**Problem:** Tests failing

**Solution:**
```bash
# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/test_specific.py -v

# Run with debug output
pytest --pdb

# Check test coverage
pytest --cov=api --cov-report=html
```

**Problem:** Import errors in tests

**Solution:**
```bash
# Check Python path
echo $PYTHONPATH

# Set Python path
export PYTHONPATH=.

# Run tests with Python path
PYTHONPATH=. pytest
```

### 10. Port and Network Issues

**Problem:** Port 3000 already in use

**Solution:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
vercel dev --port 3001
```

**Problem:** Port 5432 (PostgreSQL) already in use

**Solution:**
```bash
# Check if local PostgreSQL is running
brew services list | grep postgres

# Stop local PostgreSQL
brew services stop postgresql

# Or change Docker port mapping
# Edit docker-compose.dev.yml
```

## Getting More Help

### Debug Mode

Enable debug mode for more detailed output:

```bash
# Vercel debug mode
VERCEL_DEBUG=1 vercel dev

# Python debug mode
PYTHONPATH=. python -m pytest -v --tb=long

# Docker debug mode
docker-compose -f docker-compose.dev.yml up --verbose
```

### Logs and Monitoring

```bash
# View all logs
docker-compose -f docker-compose.dev.yml logs -f

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f elasticsearch

# Vercel function logs
vercel logs --function=api/health/check

# System resource usage
docker stats
```

### Health Checks

```bash
# Check all services
curl http://localhost:3000/api/health/check

# Check individual services
curl http://localhost:9200  # Elasticsearch
curl http://localhost:9092  # Kafka
curl http://localhost:5432  # PostgreSQL
```

## Still Having Issues?

1. **Check the logs** - Most issues have error messages in logs
2. **Restart services** - Often fixes temporary issues
3. **Check documentation** - Review setup guides and API docs
4. **Search online** - Many issues have solutions on Stack Overflow
5. **Ask for help** - Create an issue in the repository

---

**Last Updated:** September 18, 2025  
**Version:** 1.0.0
