# Engineering Log Intelligence System

An AI-powered log analysis platform that processes engineering logs from multiple sources (SPLUNK, SAP, custom systems), identifies patterns, and provides actionable insights for system optimization.

## Architecture

This project uses a **hybrid Vercel + External Services architecture**:

- **Frontend**: Vue.js SPA deployed on Vercel with global CDN
- **API Layer**: Vercel Functions for serverless API endpoints
- **External Services**: PostgreSQL, Elasticsearch, Kafka for persistent data and processing
- **ML Pipeline**: External services for model training, Vercel Functions for inference

## Project Structure

```
engineering_log_intelligence/
├── api/                    # Vercel Functions (serverless backend)
│   ├── auth/              # Authentication functions
│   ├── logs/              # Log processing functions
│   ├── ml/                # ML inference functions
│   ├── dashboard/         # Dashboard data functions
│   └── health/            # Health check functions
├── frontend/              # Vue.js SPA
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── views/         # Page components
│   │   ├── services/      # API service calls
│   │   └── utils/         # Utility functions
│   └── public/            # Static assets
├── external-services/     # External service configurations
│   ├── postgresql/        # Database configs
│   ├── elasticsearch/     # Search configs
│   ├── kafka/             # Streaming configs
│   └── ml/                # ML service configs
├── docs/                  # Documentation
└── tests/                 # Test files
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker Desktop
- Vercel CLI
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd engineering_log_intelligence
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

4. **Set up development environment**
   ```bash
   ./scripts/setup-dev-simple.sh
   ```

5. **Test the setup**
   ```bash
   python test_simple_api.py
   ```

6. **Run locally (optional)**
   ```bash
   vercel dev
   ```

## Features

- **Real-time Log Processing**: Process logs from SPLUNK, SAP, and custom systems
- **AI-Powered Analysis**: Machine learning models for log classification and anomaly detection
- **Interactive Dashboards**: Real-time visualizations with D3.js
- **Cross-System Correlation**: Identify related events across different systems
- **Natural Language Queries**: Query logs using natural language
- **Automated Alerts**: Intelligent alerting with escalation workflows

## Technology Stack

### Backend (Vercel Functions)
- Python 3.9+
- FastAPI
- PostgreSQL
- Elasticsearch
- Kafka

### Frontend (Vercel)
- Vue.js 3
- D3.js
- Pinia (state management)
- Vite (build tool)

### External Services
- PostgreSQL (Railway/Supabase/Neon)
- Elasticsearch (AWS/GCP)
- Kafka (Confluent Cloud/AWS MSK)
- AWS S3 (file storage)

## Development

### Running Tests
```bash
# Test external services
python test_external_services.py

# Test API functions
python test_simple_api.py

# Run all tests
pytest
```

### Code Quality
```bash
black .
flake8 .
mypy .
```

### External Services
```bash
# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Stop development services
docker-compose -f docker-compose.dev.yml down

# View service logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Deployment
```bash
# Deploy to production
vercel --prod

# Deploy to development
vercel
```

## Documentation

- [Project Status](PROJECT_STATUS.md) - Current project status and achievements
- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [Environment Setup](docs/ENVIRONMENT_SETUP.md)
- [Vercel Development Setup](docs/VERCEL_DEVELOPMENT_SETUP.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Data Schema Design](docs/DATA_SCHEMA_DESIGN.md)
- [Monitoring Setup](docs/MONITORING_SETUP.md)
- [Phase 2 Preparation](docs/PHASE2_PREPARATION.md)
- [API Documentation](docs/API.md) *(Coming Soon)*
- [Deployment Guide](docs/DEPLOYMENT.md) *(Coming Soon)*

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Status

🎉 **Phase 1 Complete** - Foundation phase completed successfully!

### Current Progress (Phase 1 Complete - Day 5)
- ✅ **Project Foundation** (Days 1-3): Complete Vercel + External Services architecture
- ✅ **Code Quality** (Day 4): Automated formatting, linting, type checking, security scanning
- ✅ **CI/CD Pipeline** (Day 4): GitHub Actions with automated testing and deployment
- ✅ **API Functions** (Day 5): All Vercel Functions tested and working locally
- ✅ **Monitoring** (Day 5): Full observability stack with metrics and alerting
- ✅ **Documentation** (Days 4-5): Comprehensive setup, troubleshooting, and architecture guides
- ✅ **Data Schemas** (Day 5): Complete database, search, and streaming schemas designed
- ✅ **Phase 2 Prep** (Day 5): Data simulation framework ready for development

### Phase 1 Achievements
- **Architecture** (Days 1-3): Hybrid Vercel + External Services with auto-scaling
- **Quality** (Day 4): 100% automated code quality controls with Black, Flake8, MyPy
- **CI/CD** (Day 4): GitHub Actions with automated testing and deployment hooks
- **Testing** (Day 5): All Vercel Functions tested and validated
- **Monitoring** (Day 5): Structured logging, performance tracking, alerting
- **Security** (Day 4): Multi-layer security approach with automated scanning
- **Documentation** (Days 4-5): Complete guides for setup, troubleshooting, and development

### Phase 2 Goals (Days 6-12)
- 🔄 **Data Simulation**: SPLUNK, SAP, and application log generators
- 🔄 **Vercel Functions**: Complete API layer with authentication
- 🔄 **External Integration**: Full service integration and testing
- 🔄 **Performance**: Optimization and production readiness

### Available Endpoints
- **Health Check**: `/api/health/check` - System health monitoring
- **Log Ingestion**: `/api/logs/ingest` - Log data ingestion
- **Log Search**: `/api/logs/search` - Log search and filtering
- **Monitoring**: `/api/monitoring/dashboard` - System metrics dashboard
- **Metrics**: `/api/monitoring/metrics` - Detailed performance metrics

---

**Last Updated**: September 21, 2025  
**Version**: 1.0.0  
**Phase**: 1 Complete → Phase 2 Ready
